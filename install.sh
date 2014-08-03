#!/bin/bash

#################################
#	Install script for wamn.py	#
#################################
if [[ $EUID -ne "0" ]]; then
	echo "Needs to be run as root"
	exit 
else
	wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
        gunzip GeoLiteCity.dat.gz
        mkdir /tmp/wamnsetup && cd /tmp/wamnsetup
	wget https://pygmaps.googlecode.com/files/pygmaps-0.1.1.tar.gz
	wget https://bootstrap.pypa.io/get-pip.py
	python get-pip.py
	gunzip pygmaps-0.1.1.tar.gz && tar -xvf pygmaps-0.1.1.tar
	cd pygmaps-0.1.1/
	python setup.py install
	cd ../
	pip install pygeoip pylogsparser mechanize pytz
	cd ~/
	rm -rf /tmp/wamnsetup
fi
