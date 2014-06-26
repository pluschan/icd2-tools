#!/usr/bin/env python

import glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

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

def on_statistics_sig(*args):
  print 'Statistics for %s network "%s"' % (humanReadableNetworkType(args[3]), args[5])
  print 'Signal: %i / Active for %s' % (args[7], parseSeconds(args[6]))
  print '%s sent. %s received.' % (parseBytes(args[8]), parseBytes(args[9]))
  mainloop.quit()

def humanReadableNetworkType(type):
  return {
    'WLAN_INFRA': 'Infrastructure WiFi',
    'WLAN_ADHOC': 'Ad-Hoc WiFi',
    'GPRS' : 'Cellular Data'
  }[type]


DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()
icd2_proxy = bus.get_object('com.nokia.icd2', '/com/nokia/icd2')
icd2 = dbus.Interface(icd2_proxy, 'com.nokia.icd2')
icd2.connect_to_signal('statistics_sig', on_statistics_sig, byte_arrays=True)

icd2.statistics_req()

mainloop = glib.MainLoop()
mainloop.run()
