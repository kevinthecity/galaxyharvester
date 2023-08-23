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
import dbShared
import ghShared
import env
import ghLists
from jinja2 import Environment, FileSystemLoader
from utils import setup_user_environment

def get_planet_list(galaxy, available):
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

	# Execute the SQL query and build the HTML list
	listHTML = ''
	with dbShared.ghConn() as conn:
		with conn.cursor() as cursor:
			cursor.execute(planetSQL, (galaxy,))
			for row in cursor.fetchall():
				listHTML += '<option value="{0}">{1}</option>'.format(row[0], row[1])
	return listHTML

def main():

	user_env = setup_user_environment()
	url=user_env['url']
	currentUser=user_env['currentUser']
	loginResult=user_env['loginResult']
	uiTheme=user_env['uiTheme']
	galaxy=user_env['galaxy']
	logged_state=user_env['logged_state']
	linkappend=user_env['linkappend']
	pictureName=user_env['pictureName']

	msgHTML = ''
	galaxyName = ''
	galaxyState = 0
	galaxyCheckedNGE = ''
	galaxyWebsite = ''
	galaxyPlanetList = []
	availablePlanetList = []
	galaxyAdminList = dbShared.getGalaxyAdminList(currentUser)

	if not galaxy:
		galaxyAdmins = [currentUser]
		msgHTML = '<h2>Please enter galaxy details for review.</h2>'
	else:
		availablePlanetList = get_planet_list(galaxy, 1)
		galaxyPlanetList = get_planet_list(galaxy, 0)
		galaxyAdmins = dbShared.getGalaxyAdmins(galaxy)

		with dbShared.ghConn() as conn:
			with conn.cursor() as galaxyCursor:
				galaxyCursor.execute('SELECT galaxyName, galaxyState, galaxyNGE, website FROM tGalaxy WHERE galaxyID={0};'.format(galaxy))
				galaxyRow = galaxyCursor.fetchone()
				if galaxyRow != None:
					galaxyName = galaxyRow[0]
					galaxyState = galaxyRow[1]
					if galaxyRow[2] > 0:
						galaxyCheckedNGE = 'checked'
					galaxyWebsite = galaxyRow[3]

	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(os.environ['HTTP_USER_AGENT'])
	template = environ.get_template('galaxy.html')
	print(template.render(
		uiTheme=uiTheme, 
		loggedin=logged_state, 
		currentUser=currentUser, 
		pictureName=pictureName, 
		loginResult=loginResult, 
		linkappend=linkappend, 
		url=url, 
		imgNum=ghShared.imgNum, 
		galaxyID=galaxy, 
		galaxyList=ghLists.getGalaxyList(), 
		msgHTML=msgHTML, 
		galaxyName=galaxyName, 
		galaxyState=galaxyState, 
		galaxyCheckedNGE=galaxyCheckedNGE, 
		galaxyWebsite=galaxyWebsite, 
		galaxyStatusList=ghLists.getGalaxyStatusList(), 
		galaxyPlanetList=galaxyPlanetList, 
		availablePlanetList=availablePlanetList, 
		galaxyAdminList=galaxyAdminList, 
		galaxyAdmins=galaxyAdmins, 
		enableCAPTCHA=env.RECAPTCHA_ENABLED, 
		siteidCAPTCHA=env.RECAPTCHA_SITEID))


if __name__ == "__main__":
	main()
