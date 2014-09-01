#!/usr/bin/python
# Who's Attacking Me Now? (WAMN)
# An application to parse ssh logs, report and map attacks on Debian based systems.
# Further functionality for other OSs and different logs will be added.
# WAMN is released under the GPL V2
# However we would like you to buy us pizza and beer if you like it!
# The authors accept no responsibility for damage cause by the program or irresponsible use
# Authors: Paul Mason (Paulmason126[at]gmail[dot]com) ; Kyle Fleming (kylefleming[at]gmail[dot}com)
# Contributors: TBC Come on folks!!!
# Thanks: TJ O'Connor Author of Violent Python which gave us the inspiration for this app
import sys, signal, socket
import urllib2
import urlparse
import re
import pygmaps
import pygeoip
import mechanize
import os
import gzip
import datetime
from logsparser.lognormalizer import LogNormalizer as LN
from time import sleep
os.system('clear')
normalizer = LN('/usr/local/share/logsparser/normalizers')
gi = pygeoip.GeoIP('WAMN/GeoLiteCity.dat')
countries = {}
latlong = {}

def geo_menu():
  print 'Geolocation Menu'
  print '1) Enter and locate an IP Addr'
  print '2) Enter a url, resolve IP and geolocate'
  print '3) Log Check and IP geolocate (sshd)'
  geo_option = raw_input('Please choose an option: ')
  try:
    choice = geomenudict[geo_option]
    choice()
  except KeyError:
    print "try again..."
    geo_menu()

def sulogcheck(): #############Kinda working.################
  LOG = '/var/log/auth.log'
  su_log = open(LOG, 'r')

  for log in su_log: #################### MAKE A COPY BEFORE EDITING, PLEASE  ##########################
    s = {"raw": log }
    normalizer.normalize(s) #################### THINK WE MIGHT HAVE TO WRITE OUR OWN NORMALIZER FOR THIS #################
                            #################### We don't, Just have to edit the pam-002-generic (iirc) to handle the user that called su #########
    if s.get('component') == 'pam_unix' and s.get('program') == 'su' and s.get('type') == 'auth':
     # u = s['ruser']
      r = s['user']
      print "User %s Failed su attempt" % r

def logcheck():
  f = open('.wamn.save', 'wr')
  print "This function can also handle gzip compressed logfiles"
  LOG =  raw_input('Enter the path to the log file: ')
  if LOG.endswith('.gz'):
    auth_logs = gzip.GzipFile(LOG, 'r')
  else :
    auth_logs = open(LOG, 'r')

  attacks = {}
  users = {}
  origin_unknown = {}
  print "Parsing log file"
  for log in auth_logs:
    l = {"raw": log }
    normalizer.normalize(l)
    if l.get('action') == 'fail' and l.get('program') == 'sshd':
      u = l['user']
      p = l['source_ip']
      try:
        d = l['date']
      except:
        d = "no date available"
      oct1, oct2, oct3, oct4 = [int(i) for i in p.split('.')] #split IP so we can check for private addr
      if oct1 == 192 and oct2 == 168 or oct1 == 172 and oct2 in range(16, 32) or oct1 == 10: #check for private addr
        print "Private ip attack, %s No geolocation available" % str(p)
      if attacks.has_key(p): #if not private do geolocate
        attacks[p] = attacks.get(p, 0)+ 1
        countryRecord(p)
      else:
        printRecord(p)
        attacks[p] = attacks.get(p, 0)+ 1
      users[u] = users.get(u, 0)+ 1
      if d:
        f.write(str(d))

  f.close()
  sort(attacks, users)
  gmaps()
  en2con()
  main()
# reads takes ip addr as string. Reads .dat file, prints coresponding lat, long and area of ip
def geo_ip():
  print "Enter IP address"
  ipaddr = raw_input("Please enter an IP Address: ")
  printRecord(ipaddr)
  gmaps()
  geo_menu()
def countryRecord(p):
  # This function gets run just to keep the country attack count right if the Ip address doesn't need geolocated again.
  # This needs fixed (As in removed, there must be a nicer way to do it!)
  rec = gi.record_by_name(p)
  try:
    country = rec['country_name']
    if country:
      countries[rec['country_name']] = countries.get(rec['country_name'], 0)+ 1
  except TypeError:
    print "No country in DB"
  return

def printRecord(tgt):
  rec = gi.record_by_name(tgt)
  try:
    city = rec['city']
    if city:
      city = city.encode('utf8')
  except TypeError:
    print "no city in DB"
  try:
    region = rec['time_zone']
  except TypeError:
    print "no timezone in db"
  try:
    country = rec['country_name']
    if country:
      countries[rec['country_name']] = countries.get(rec['country_name'], 0) + 1

  except TypeError:
    print "No country in db"
  try:
    long = rec['longitude']
    lat = rec['latitude']
    if lat and long:
      latlong[rec['latitude']] = rec['longitude']
  except TypeError:
    print "No coords in db"
  try:
    print '[*] Target: ' + tgt + ' Geo-located. '
    print '[+] ' + str(city) +', '+str(region)+ ', '+ str(country)
    print '[+] Latitude: '+str(lat)+ ', ' +str(long)
    print ''
  except UnboundLocalError:
    print "error"
  return

def gmaps():
  #Build map
  map = pygmaps.maps(latitude, longitude, 3)
  for p,k in latlong.items():
    #Add in locations
    map.addpoint(float(p), float(k))
  #Draw the map
  map.draw('./map.html')

def sort(attacks, users):
  l = ''
  m = ''
  n = ''
  print "Attack IP Sorted in order"
  for i,j in sorted(attacks.items(), cmp = lambda a,b: cmp(a[1], b[1]) ):

    print "\t%s (%i attempts)" % (i,j)
    w = "\t%s (%i attempts)\n" % (i,j)
    l += w

  print "Attacking countries Sorted in order"
  for p,k in sorted(countries.items(), cmp = lambda c,d: cmp(c[1], d[1]) ):

    print "\t%s (%i attempts)" % (p,k)
    x = "\t%s (%i attempts)\n" % (p,k)
    m += x
  print "Usernames used in attacks Sorted in Order only if 10 or more attempts made with same username"
  for u,a in sorted(users.items(), cmp = lambda e,f: cmp(e[1], f[1]) ):
    if a > 9:
      print "\t%s (%i attempts)" % (u,a)
      g = "\t%s (%i attempts)\n" % (u,a)
      n += g
  report(l, m, n)

def report(what, wheres, whos):
 file = datetime.date.today()
 name = file.strftime('%d%m%y')
 end = '-wamn.txt'
 filename = name+end
 with open(filename, 'w') as f:
  f.write(what)
  f.write(wheres)
  f.write(whos)

def getlocation():
  try:
    i = urllib2.Request("http://icanhazip.com")
    p = urllib2.urlopen(i)
    ip = p.read()
  except:
    print "No Internet Access, Default Coordinates being used to build map."
  try:
    s = gi.record_by_name(ip)
    global latitude
    latitude = s['latitude']
    global longitude
    longitude = s['longitude']
  except :
    print "No coordinates held for your IP address"
    global latitiude
    latitude = "55.9013"
    global longitude
    longitude = "-3.536"

def resolvegeoip():
  ur = raw_input("URL [>] ")
  if "http://" in ur or "https://" in ur:
    req = urllib2.Request(ur)
  else:
    url = "http://" + ur
    req = urllib2.Request(url)
  webdat = urllib2.urlopen(req)
  ip = socket.gethostbyname(urlparse.urlparse(webdat.geturl()).hostname)
  print ip
  printRecord(ip)
  gmaps()
  en2con()
  main()

def ctrlc_catch(signal, frame):

  print "\n Exiting clean"
  sys.exit(0)

def en2con(Prompt='Hit Enter to continue'):
        raw_input("Hit Enter to continue")

def main():
  getlocation()
  signal.signal(signal.SIGINT, ctrlc_catch)
  print 'Welcome to WAMN.'
  print '1) Automatic set-up and run on local system'
  print '2) Set advanced options'
  print '3) Perform specific task from WAMN toolkit.'
  print '0) Exit'
  option = raw_input('Please choose an option: ')
  try:
    main_choice = main_menu[option]
    main_choice()
  except KeyError:
    print "Invalid selection"
    main()

def toolsmenu():
  print 'Tools Main Menu'
  print '1) Geolocation Tool'
  print '2) TBC'
  print '3) TBC'
  print '0) Exit'
  tools_option = raw_input('Please choose an option: ')
  try:
    choice = tools_dict[tools_option]
    choice()
  except KeyError:
    print "Invalid selection"
    toolsmenu()

main_menu = {
  '1': geo_ip,
  '2': sulogcheck,
  '3': toolsmenu,
  '0': exit
  }
tools_dict = {
  '1': geo_menu,
# '2': tbc,
# '3': tbc,
  '0': exit
  }
geomenudict = {
  '1': geo_ip,
  '2': resolvegeoip,
  '3': logcheck,
  '0': exit
  }
main()
