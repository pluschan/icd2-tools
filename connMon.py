#!/usr/bin/env python

import sys
import glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

def on_addrinfo_sig(*args):
  printAddrInfo(args)
  if '-s' in sys.argv:
    icd2.statistics_req(args[0], args[1], args[2], args[3], args[4], args[5])

def parseSeconds(seconds):
  m , s  = divmod(seconds, 60)
  h , m  = divmod(m, 60)
  d , h  = divmod(h, 24)
  w , d  = divmod(d, 7)
  mn, w = divmod(w, 4)
  y , mn = divmod(mn, 12)
  
  # print 'y: %i mn:%i w: %i d:%i h:%i m:%i s: %i' % (y,mn,w,d,h,m,s)

  # 1 year - 29030400 seconds
  # 1 month - 2419200 seconds
  # 1 week - 604800 seconds
  # 1 day - 86400 seconds
  # 1 hour - 3600 seconds
  # 1 minute - 60 seconds

  if seconds >= 29030400:
    return '%i years' % (y)
  elif seconds >= 2419200:
    return '%i months' % (mn)
  elif seconds >= 604800:
    return '%i weeks' % (w)
  elif seconds >= 86400:
    return '%i days' % (d)
  elif seconds >= 3600:
    return '%i hours' % (h)
  elif seconds >= 60:
    return '%i minutes' % (m)
  else:
    return '%i seconds' % (s)

def parseBytes(num):
  for x in ['bytes','KB','MB','GB']:
    if num < 1024.0 and num > -1024.0:
      return "%3.1f%s" % (num, x)
    num /= 1024.0
  return "%3.1f%s" % (num, 'TB')

# (dbus.String(u''), dbus.UInt32(0L), dbus.String(u''), dbus.String(u'WLAN_INFRA'), dbus.UInt32(83888801L), dbus.ByteArray('7961cf3e-24f8-40a0-b80a-74a924d8babf\x00'), dbus.UInt32(1L), dbus.Int32(5), dbus.UInt32(11261L), 
# dbus.UInt32(252327L))

def on_statistics_sig(*args):
  print 'Statistics for %s network "%s"' % (humanReadableNetworkType(args[3]), args[5])
  print 'Signal: %i / Active for %s' % (args[7], parseSeconds(args[6]))
  print '%s sent. %s received.' % (parseBytes(args[8]), parseBytes(args[9]))

def printConnState(id, type, state):
  print '%s connection "%s" %s.' % (type, id, state)

def printAddrInfo(addrinfo):
  print 'Address information for %s connection "%s"' % (humanReadableNetworkType(addrinfo[3]), addrinfo[5])
  ip_info = addrinfo[6][0]
  print ':: IP Address: %s' % (ip_info[0])
  print ':: Netmask: %s' % (ip_info[1])
  print ':: Default Gateway: %s' % (ip_info[2])
  print ':: 1st DNS Server: %s' % (ip_info[3])
  print ':: 2nd DNS Server: %s' % (ip_info[4])
  print ':: 3rd DNS Server: %s' % (ip_info[5])

def humanReadableNetworkType(type):
  return {
    'WLAN_INFRA': 'Infrastructure WiFi',
    'WLAN_ADHOC': 'Ad-Hoc WiFi',
    'GPRS' : 'Cellular Data'
  }[type]

def on_state_sig(*args):
  if len(args) == 2:
    if args[1] == 8:
      print 'Phone started searching for %s networks.' % (humanReadableNetworkType(args[0]))
    elif args[1] == 9:
      print 'Phone stopped searching for %s networks.' % (humanReadableNetworkType(args[0]))
  elif len(args) == 8:
    if not args[6]:
      if args[7] == 0:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'has disconnected')
      elif args[7] == 1:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'is connecting')
      elif args[7] == 2:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'has connected')
        if '-a' in sys.argv:
          icd2.addrinfo_req(args[0], args[1], args[2], args[3], args[4], args[5])
      elif args[7] == 3:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'is disconnecting')
      elif args[7] == 4:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'is in state: limited connectivity enabled')
      elif args[7] == 5:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'is in state: limited connectivity disabled')
      elif args[7] == 15:
        printConnState(args[5], humanReadableNetworkType(args[3]), 'has acquired an internal address')
    else:
      print 'E: ICD2 is reporting an error while connecting.'
  else:
    print 'E: Unknown state signal type.'

DBusGMainLoop(set_as_default=True)

print 'ICD2 DBUS Connection Listener'

if '-h' in sys.argv:
  print 'Usage: connMon [-a] [-s] [-h]'
  print '-a : Show address information after connection.'
  print '-s : Show statistics after connection.'
  print '-h : This help.'
else:
  bus = dbus.SystemBus()
  icd2_proxy = bus.get_object('com.nokia.icd2', '/com/nokia/icd2')
  icd2 = dbus.Interface(icd2_proxy, 'com.nokia.icd2')
  icd2.connect_to_signal('state_sig', on_state_sig, byte_arrays=True)
  icd2.connect_to_signal('addrinfo_sig', on_addrinfo_sig, byte_arrays=True)
  icd2.connect_to_signal('statistics_sig', on_statistics_sig, byte_arrays=True)

  mainloop = glib.MainLoop()
  mainloop.run()
