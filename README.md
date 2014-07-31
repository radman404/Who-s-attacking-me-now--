Who-s-attacking-me-now--
========================

A Python script that will parse your auth log for failed ssh login attempts

Guide to using WAMN V 0.1a

What is WAMN?

WAMN stands for Who’s Attacking me now? It is a script which reads logs and produces reports, maps and graphs based on attacks which it detects against the system. WAMN is currently pre-alpha. Its current functionality allows it to open the ssh log on a debian based system, parse the log then produce a report which details which IP addresses have attempted to login, their geolocation, a report sorted by country and number of attacks. It then populates a map which can be viewed locally or made public.

Future developments for WAMN include: adding support for different services, different OSs, running the passwords used against common wordlists in an attempt to identify if the attack is targeted or sophisticated and creating an alert, running the usernames attempted against similar lists to identify if a database has been breached and the usernames are being employed, an algorithm to estimate the sophistication of the attack and fingerprint bots, advanced attack detection in webserver logs and an option to submit your data to the WAMN site to crowdsource attacks in real time.

WAMN has many uses: in security education, for sysadmins who have to report on attacks and for systems which require ports to be open on default numbers. An example of this is c-panel which required root login on the default ssh port.   

Installation.

Installation can be achieved with the provided bash script. If you would like to do it manually the instructions are below

WAMN requires a few non standard modules.
From the Google code Project “pygmaps is a Python wrapper for Google Maps JavaScript API V3. pygmaps provides functions to generate HTML file which shows your GPS data on Google map.”
Get pygmaps https://pygmaps.googlecode.com/files/pygmaps-0.1.1.tar.gz 
Unpack the archive and run ‘python setup.py’ script to install.
The other third party modules can be installed through pip. Install pip using apt package manager on Debian based systems or using your operating systems package manager.
Eg. root@yoursystem:~# apt-get install python-pip
Using pip to install modules.
As root in a terminal do
pip install pygeoip pylogsparser
you should now be almost ready to use WAMN!

Usage.

There are a few hard coded paths in the code at the minute, we will figure out a better way of doing this in later versions. These need to be changed to point to your normalizers for logsparser, the .dat file for pygeoip and the auth.log to parse.
normalizer = LN('/usr/share/normalizers') line 12
gi = pygeoip.GeoIP('/path/to/GeoLiteCity.dat') line 13
LOG = '/var/log/auth.log' line 32
OK, so you are now definitely ready to use WAMN!
Run it as root.
#python wamn.py
You’ll get a menu enter the number assigned to an option. 1 is not integrated yet. 
2 runs a geoip on a user given IP address and exits. 
3 will send you to another menu names “Tools Main Menu” and pressing 1 at this menu will take you to the “Geolocation Menu”
All options on this menu work as of this version.
Option 1 will take a user inputted IP address and geolocate it and take you back to the menu. 
Option 2 will take a user inputted URL and use socket.gethostbyname() to get the IP address of the server in which the URL points to.
 Option 3 will parse your auth.log file and check for failed ssh login attempts it will then take the IP address from these attempts and geolocate them, then will output  the data from the geolocation attempt if it got it, if there is no record it will tell you this. It will also sort out attacks by country and tell you how many attempts were made by which countries.

Fix the Menus!
User input of path to log file to be used.
Do something about the other hardcoded paths.
Checks for other services (Apache, su failures …)
Add in a function to collect users IP run a geolocation on it then using the Latitude and Longitude of that IP to create the map in pygmaps (map = pygmaps.maps(55.9013, -3.536, 3)) 
Add nmap functionality, option to nmap ip address of ‘attackers’ Check legalities*
Make script installable.
Investigate whether load balancers affect socket.gethostbyname() – are we getting the server IP or the loadbalancer IP?
Add other OSs
Add check for other logs like webservers
Be able to pipe the failed passwords into a file and diff it with know wordlists to identify bots/skiddies
Create alert is passwords are non standard
Create aleart if username is not on the common lists
Offer option to grep the database to see if the nonstandard user is there- indicating possibl
