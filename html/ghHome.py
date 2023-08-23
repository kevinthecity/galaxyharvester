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
import cgi
from http import cookies
import dbSession
import env
import ghShared
import ghLists
import dbShared
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
import logger
from utils import setup_user_environment

# Define namedtuples to group related parameters
UserDetails = namedtuple('UserDetails', ['uiTheme', 'currentUser', 'loginResult', 'pictureName'])
GalaxyDetails = namedtuple('GalaxyDetails', ['galaxy', 'galaxyList', 'galaxyAdmin'])
RenderSettings = namedtuple('RenderSettings', ['loggedin', 'linkappend', 'url', 'imgNum', 'enableCAPTCHA', 'siteidCAPTCHA'])
ResourceDetails = namedtuple('ResourceDetails', ['resourceGroupListShort', 'professionList', 'planetList', 'resourceGroupList', 'resourceTypeList'])
Metrics = namedtuple('Metrics', ['totalAmt', 'percentOfGoal'])

def get_donation_total():
	totalAmt = 0.00
	conn = dbShared.ghConn()
	cursor = conn.cursor()
	if (cursor):
		sqlStr = 'SELECT Sum(paymentGross) AS totalAmt FROM tPayments WHERE YEAR(completedDate)=YEAR(NOW()) AND MONTH(completedDate)=MONTH(NOW());'
		cursor.execute(sqlStr)
		row = cursor.fetchone()
		if row[0] != None:
			totalAmt = float(row[0])
	cursor.close()
	conn.close()

	percentOfGoal = totalAmt/28
	totalAmt = str(int(totalAmt))

	return totalAmt, percentOfGoal

def get_galaxy_admin(currentUser):
	adminList = dbShared.getGalaxyAdminList(currentUser).split('/option')[0]
	if len(adminList) > 0:
		galaxyAdmin = int(adminList[15:adminList.rfind('"')])
	else:
		galaxyAdmin = 0
	return galaxyAdmin

def render(
		user: UserDetails, 
	   	galaxy: GalaxyDetails, 
		settings: RenderSettings, 
		resources: ResourceDetails, 
		metrics: Metrics
	):
	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL

	userAgent = os.environ.get('HTTP_USER_AGENT', 'unknown')
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(userAgent)

	template = environ.get_template('home.html')

	print(template.render(
		**user._asdict(), 
		**galaxy._asdict(), 
		**settings._asdict(),
		**resources._asdict(),
		**metrics._asdict()
	))

def render_login(userId, loginResult):
	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL

	userAgent = os.environ.get('HTTP_USER_AGENT', 'unknown')
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(userAgent)
		
	template = environ.get_template('login.html')

	print(template.render(
		currentUser=userId,
		loginResult=loginResult,
		enableCAPTCHA=env.RECAPTCHA_ENABLED, 
		siteidCAPTCHA=env.RECAPTCHA_SITEID,
		url = os.environ.get('SCRIPT_NAME', '')
	))

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
	
	totalAmt, percentOfGoal = get_donation_total()
	galaxyAdmin = get_galaxy_admin(currentUser)

	user_details = UserDetails(
		uiTheme=uiTheme, 
		currentUser=currentUser, 
		loginResult=loginResult, 
		pictureName=pictureName
	)

	galaxy_details = GalaxyDetails(
		galaxy=galaxy, 
		galaxyList=ghLists.getGalaxyList(), 
		galaxyAdmin=galaxyAdmin
	)

	render_settings = RenderSettings(
		loggedin=logged_state, 
		linkappend=linkappend, 
		url=url, 
		imgNum=ghShared.imgNum, 
		enableCAPTCHA=env.RECAPTCHA_ENABLED, 
		siteidCAPTCHA=env.RECAPTCHA_SITEID
	)

	resource_details = ResourceDetails(
		resourceGroupListShort=ghLists.getResourceGroupListShort(), 
		professionList=ghLists.getProfessionList(galaxy), 
		planetList=ghLists.getPlanetList(galaxy), 
		resourceGroupList=ghLists.getResourceGroupList(), 
		resourceTypeList=ghLists.getResourceTypeList(galaxy)
	)

	metrics = Metrics(
		totalAmt=totalAmt, 
		percentOfGoal=percentOfGoal
	)

	render(
		user=user_details, 
		galaxy=galaxy_details, 
		settings=render_settings, 
		resources=resource_details, 
		metrics=metrics
	)

if __name__ == "__main__":
	main()