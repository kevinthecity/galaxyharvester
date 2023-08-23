#!/usr/bin/env python3
"""

 Copyright 2020 Paul Willworth <ioscode@gmail.com>

 This file is part of Galaxy Harvester.

 Galaxy Harvester is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Galaxy Harvester is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with Galaxy Harvester.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import sys
import cgi
from http import cookies
import dbSession
import dbShared
import pymysql
import ghShared
import env
import ghLists
import logger
from jinja2 import Environment, FileSystemLoader

def getPlanetList(galaxy, available):
	listHTML = ''
	
	# Ensure the galaxy value is an integer
	try:
		galaxy = int(galaxy)
	except ValueError:
		galaxy = 0

	# Choose the SQL query based on the availability value
	if available > 0:
		planetSQL = ('SELECT planetID, planetName FROM tPlanet '
					 'WHERE planetID > 10 AND planetID NOT IN '
					 '(SELECT planetID FROM tGalaxyPlanet WHERE galaxyID=%s) '
					 'ORDER BY planetName;')
	else:
		planetSQL = ('SELECT tGalaxyPlanet.planetID, planetName FROM tGalaxyPlanet '
					 'INNER JOIN tPlanet ON tGalaxyPlanet.planetID=tPlanet.planetID '
					 'WHERE tGalaxyPlanet.planetID > 10 AND tGalaxyPlanet.galaxyID=%s '
					 'ORDER BY planetName;')

	conn = dbShared.ghConn()
	# Execute the SQL query and build the HTML list
	with conn.cursor() as cursor:
		cursor.execute(planetSQL, (galaxy,))
		for row in cursor.fetchall():
			listHTML += '<option value="{0}">{1}</option>'.format(row[0], row[1])
	conn.close()
	return listHTML

def main():
	useCookies = 1
	linkappend = ''
	logged_state = 0
	currentUser = ''
	msgHTML = ''
	galaxy = ''
	uiTheme = ''
	galaxyName = ''
	galaxyState = 0
	galaxyCheckedNGE = ''
	galaxyWebsite = ''
	galaxyAdminList = []
	galaxyPlanetList = []
	availablePlanetList = []
	galaxyAdmins = []
	# Get current url
	try:
		url = os.environ['SCRIPT_NAME']
	except KeyError:
		url = ''

	form = cgi.FieldStorage()
	# Get Cookies

	C = cookies.SimpleCookie()
	try:
		C.load(os.environ['HTTP_COOKIE'])
	except KeyError:
		useCookies = 0

	if useCookies:
		try:
			currentUser = C['userID'].value
		except KeyError:
			currentUser = ''
		try:
			loginResult = C['loginAttempt'].value
		except KeyError:
			loginResult = 'success'
		try:
			sid = C['gh_sid'].value
		except KeyError:
			sid = form.getfirst('gh_sid', '')
		try:
			uiTheme = C['uiTheme'].value
		except KeyError:
			uiTheme = ''
	else:
		loginResult = form.getfirst('loginAttempt', '')
		sid = form.getfirst('gh_sid', '')

	# escape input to prevent sql injection
	sid = dbShared.dbInsertSafe(sid)

	# Get a session

	if loginResult == None:
		loginResult = 'success'

	sess = dbSession.getSession(sid)
	if (sess != ''):
		logged_state = 1
		currentUser = sess
		if (uiTheme == ''):
			uiTheme = dbShared.getUserAttr(currentUser, 'themeName')
		if (useCookies == 0):
			linkappend = 'gh_sid=' + sid
	else:
		if (uiTheme == ''):
			uiTheme = 'crafter'

	path = ['']
	if 'PATH_INFO' in os.environ:
		path = os.environ['PATH_INFO'].split('/')[1:]
		path = [p for p in path if p != '']

	if len(path) > 0:
		galaxy = dbShared.dbInsertSafe(path[0])

		galaxyAdminList = dbShared.getGalaxyAdminList(currentUser)
		availablePlanetList = getPlanetList(galaxy, 1)

		if galaxy.isdigit():
			# get the galaxy details for edit
			conn = dbShared.ghConn()
			galaxyCursor = conn.cursor()
			galaxyCursor.execute('SELECT galaxyName, galaxyState, galaxyNGE, website FROM tGalaxy WHERE galaxyID={0};'.format(galaxy))
			galaxyRow = galaxyCursor.fetchone()
			if galaxyRow != None:
				galaxyName = galaxyRow[0]
				galaxyState = galaxyRow[1]
				if galaxyRow[2] > 0:
					galaxyCheckedNGE = 'checked'
				galaxyWebsite = galaxyRow[3]
			galaxyCursor.close()
			galaxyPlanetList = getPlanetList(galaxy, 0)
			galaxyAdmins = dbShared.getGalaxyAdmins(galaxy)
			conn.close()
		else:
			galaxyAdmins = [currentUser]
			msgHTML = '<h2>Please enter galaxy details for review.</h2>'
	else:
		msgHTML = '<h2>No Galaxy found in URL path.</h2>'

	pictureName = dbShared.getUserAttr(currentUser, 'pictureName')
	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(os.environ['HTTP_USER_AGENT'])
	template = environ.get_template('galaxy.html')
	print(template.render(uiTheme=uiTheme, loggedin=logged_state, currentUser=currentUser, pictureName=pictureName, loginResult=loginResult, linkappend=linkappend, url=url, imgNum=ghShared.imgNum, galaxyID=galaxy, galaxyList=ghLists.getGalaxyList(), msgHTML=msgHTML, galaxyName=galaxyName, galaxyState=galaxyState, galaxyCheckedNGE=galaxyCheckedNGE, galaxyWebsite=galaxyWebsite, galaxyStatusList=ghLists.getGalaxyStatusList(), galaxyPlanetList=galaxyPlanetList, availablePlanetList=availablePlanetList, galaxyAdminList=galaxyAdminList, galaxyAdmins=galaxyAdmins, enableCAPTCHA=env.RECAPTCHA_ENABLED, siteidCAPTCHA=env.RECAPTCHA_SITEID))


if __name__ == "__main__":
	main()
