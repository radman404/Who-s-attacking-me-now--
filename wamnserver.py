#!/usr/bin/python
import pygeoip
import folium
import SocketServer
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
reporting = {}
countries = {}
attacks = {}
whoattacked = {}
rowindb = {}
class MyTCPServer(SocketServer.ThreadingTCPServer):
  allow_reuse_address = True

class MyTCPServerHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    try:
      data = ''
      print 'Ready to recieve data'

      while True:
        chunk = self.request.recv(2048)
        data += chunk
        if chunk == '':
          break
      print 'Data Recieved'
      staging(data)
    except Exception, e:
      print e


def staging(data):
  ip_data = json.loads(data)
  for i in ip_data.keys():
    ip = ip_data[i][0]['ip']
    att = ip_data[i][0]['attacks']
    locip = ip_data[i][0]['local_ip']
    whoattacked[ip] = locip
    attacks[ip] = att

  geoip(attacks)
  sortattacks(attacks)
  pycharting(attacks)

def geoip(ip):
  gi = pygeoip.GeoIP('../GeoLiteCity.dat')
  for i in ip.keys():
    rec = gi.record_by_name(i)
    try:
      country = rec['country_name']
      if country:
        countries[rec['country_name']] = countries.get(rec['country_name'], 0) + 1
    except TypeError:
      countries['Unknown Country'] = countries.get('Unknown Country', 0) + 1
    try:
      lon = rec['longitude']
      lat = rec['latitude']
      if lat and lon:
        reporting[i] = str(lat) +','+str(lon)
    except TypeError:
      print ''
  gmaps(reporting, ip)
  return

def sortattacks(attacks):
  print 'Attacks sorted by attempts'
  for i,j in sorted(attacks.items(), cmp = lambda a,b: cmp(a[1], b[1]) ):
    if j > 100:
      print '\t%s (%i attempts)' % (i,j)

def pycharting(attacks):
#This is a disaster atm, I really need to spend some time getting this to working
# IN TESTING
  fig = plt.figure(figsize = (20,10), dpi = 80)
  ax1 = fig.add_subplot(121)
  todraw = sorted(countries.items(),cmp = lambda a,b: cmp(a[1], b[1]) )[-5:]
  labels, values = zip(*reversed(todraw))
  pie, thing = ax1.pie(values,
                        startangle=90,
                        colors = plt.cm.nipy_spectral(np.linspace(0,1,len(values))),
                        )
  lgd = plt.legend(pie,
                    labels,
                    bbox_to_anchor=(0.6, 0.5),
                    title="Top 5 Countries",
                    bbox_transform=plt.gcf().transFigure
                    )
  plt.savefig('/var/www/chart.png', additional_artists=(lgd), dpi = fig.dpi, bbox_inches="tight") #save chart as pdf

def gmaps(reporting, attacks):
  #Build map
  latitude = "55.9013"
  longitude = "-3.536"
  map1 = folium.Map(location=[latitude, longitude])
  for i,d in reporting.items():
    lat, long = d.split(',')
    numofattacks = attacks[i]
                #Plot map and insert info
    map1.simple_marker([lat, long], popup="IP: %s Attempts: %s" %(str(i), str(numofattacks)))

  #Draw the map
  map1.create_map(path='/var/www/mapp.html')
  poststage()
  return
def poststage():
  #where everythin gets ready to be put in the database
  for i in attacks.keys():
    rowindb[i] = (attacks[i], whoattacked[i], reporting[i])
  dbthis(rowindb)
def dbthis(rowindb):
  con = sqlite3.connect('test.db')
  with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS Attackers")
    cur.execute("CREATE TABLE Attackers(IP TEXT, Attacks INT, Local_ip TEXT, Latitude TEXT, Longitude TEXT)")
    for i, x in rowindb.iteritems():
      ip = i
      attacks = x[0]
      local_ip = x[1]
      lat, lon = x[2].split(',')
      sql = "INSERT INTO Attackers VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(ip, int(attacks), local_ip, lat, lon)
      cur.execute(sql)
    cur.execute("SELECT * FROM Attackers")
    rows = cur.fetchall()
    print ' 1'
    for row in rows:
      string = "IP: '{0}' Attacks:'{1}' Local_IP:'{2}' Latitude:'{3}' Longitude:'{4}'".format(row[0], row[1], row[2], row[3], row[4])
      print string
server = MyTCPServer(('185.47.61.126', 9999), MyTCPServerHandler)
try:
 server.serve_forever()
except KeyboardInterrupt:
  print '\nServer closing...'
  exit(0)
