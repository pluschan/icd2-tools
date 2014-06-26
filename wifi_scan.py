#!/usr/bin/env python

import glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

import sys
import time

def parseScanStatus(status):
  return {
    0 : 'New (Found new network.)',
    1 : 'Update (Signal strength increased!)',
    2 : 'Notify',
    3 : 'Expired (Probably left network range?)',
    4 : 'Complete'
  }[status]

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

def parseTimestamp(timestamp):
  ctime = int(time.time())
  delta = ctime - timestamp

  if delta <= 0:
    return 'just now'
  else:
    return '%s ago' % parseSeconds(delta)

def on_scan_sig(*args):
  if args[0] == 4:
    print '= = = = = = = = = = '
  elif args[0] == 2:
    if '-s' in sys.argv:
      pass
  else:
    if '-v' in sys.argv:
      print '[SSID: %s]' % (args[8])
      print '- Signal: %i (%i dBm)' % (args[12], args[14])
      print '- Type: %s' % (humanReadableNetworkType(args[7]))
      print '- Seen at: %i' % (args[1])
      print '- Network ID: %s' % (args[10])
      print '- MAC Address: %s' % (args[13])
      print '- Network Priority: %i' % args[11]
      print '- Scan Status: %s' % parseScanStatus(args[0])
      print '- - - - - - - - '
    else:
      if '-header' in sys.argv:
        print 'name (signal / rssi) - type / timestamp / network id / mac / priority / status'
      print '%s (%i/%i dBm) - %s / %s / %s / %s / %i / %s' % (args[8], args[12], args[14], humanReadableNetworkType(args[7]), parseTimestamp(args[1]), args[10], args[13], args[11], parseScanStatus(args[0]))

def humanReadableNetworkType(type):
  return {
    'WLAN_INFRA': 'Infrastructure WiFi',
    'WLAN_ADHOC': 'Ad-Hoc WiFi',
    'GPRS' : 'Cellular Data'
  }[type]

DBusGMainLoop(set_as_default=True)

if '-h' in sys.argv:
  print 'Usage: wifi_scan [-s] [-v] [-header] [-h]'
  print '-s      : Silence notify events.'
  print '-v      : Print network events in multi-line format instead of single-line.'
  print '-header : Print header. Implying that you didn\'t use -v.'
  print '-h      : This help.'
else:
  bus = dbus.SystemBus()
  icd2_proxy = bus.get_object('com.nokia.icd2', '/com/nokia/icd2')
  icd2 = dbus.Interface(icd2_proxy, 'com.nokia.icd2')
  icd2.connect_to_signal('scan_result_sig', on_scan_sig, byte_arrays=True)

  icd2.scan_req(dbus.UInt32(1))

  mainloop = glib.MainLoop()
  mainloop.run()
