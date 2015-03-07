#!/usr/bin/python

import pygeoip
import json
from logsparser.lognormalizer import LogNormalizer as LN
import gzip
import glob
import socket
import urllib2
IP = 'IP.Of,Your.Server'
normalizer = LN('/usr/local/share/logsparser/normalizers')
gi = pygeoip.GeoIP('../GeoLiteCity.dat')
def complete(text, state):
  return (glob.glob(text+'*')+[none])[state]
def sshcheck():
  attacks = {}
  users = {}
  try:
    import readline, rlcompleter
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
  except ImportError:
    print 'No Tab Completion'
  LOGs = raw_input('Enter the path to the log file: ')
  for LOG in LOGs.split(' '):
    if LOG.endswith('.gz'):
      auth_logs = gzip.GzipFile(LOG, 'r')
    else:
      auth_logs = open(LOG, 'r')
    if len(LOGs) is '1':
      print "Parsing log file"
    else:
      print "Parsing log files"
    for log in auth_logs:
      l = {"raw": log }
      normalizer.normalize(l)
      if l.get('action') == 'fail' and l.get('program') == 'sshd':
        u = l['user']
        p = l['source_ip']
        o1, o2, o3, o4 = [int(i) for i in p.split('.')]
        if o1 == 192 and o2 == 168 or o1 == 172 and o2 in range(16, 32) or o1 == 10:
          print "Private IP, %s No geolocation data" %str(p)
        attacks[p] = attacks.get(p, 0) + 1
  getip()
  dojson(attacks, IP)
def getip():
  global IP
  if IP is 0:
    try:
      i = urllib2.Request("http://icanhazip.com")
      p = urllib2.urlopen(i)
      IP = p.read()
    except:
      print "can't seem to grab your IP please set IP variable so We can better map attacks"

def dojson(attacks, IP):
  data = {}
  for i,(a,p) in enumerate(attacks.iteritems()):
    datalist = [{ 'ip': a, 'attacks': p, 'local_ip': IP }]
    data[i] = datalist
  newdata = data
  newjson = json.dumps(newdata)
  print json.loads(newjson)
  send(newjson)

def send(data):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('Ip.Of.Your.Server', 9999))
  s.sendall(data)
  s.close()
try:
  sshcheck()
except KeyboardInterrupt:
  print '\nCtrl+C Exiting...'
  exit(0)
