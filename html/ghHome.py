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

# Define namedtuples to group related parameters
UserDetails = namedtuple('UserDetails', ['uiTheme', 'currentUser', 'loginResult', 'pictureName'])
GalaxyDetails = namedtuple('GalaxyDetails', ['galaxy', 'galaxyList', 'galaxyAdmin'])
RenderSettings = namedtuple('RenderSettings', ['loggedin', 'linkappend', 'url', 'imgNum', 'enableCAPTCHA', 'siteidCAPTCHA'])
ResourceDetails = namedtuple('ResourceDetails', ['resourceGroupListShort', 'professionList', 'planetList', 'resourceGroupList', 'resourceTypeList'])
Metrics = namedtuple('Metrics', ['totalAmt', 'percentOfGoal'])

def get_value_from_cookie(cookie, key, default=None):
	try:
		return cookie[key].value
	except KeyError:
		return default

def get_value_from_form_or_cookie(form, cookie, key, default=None):
	return form.getfirst(key, get_value_from_cookie(cookie, key, default))

def setup_environment():
	url = os.environ.get('SCRIPT_NAME', '')
	form = cgi.FieldStorage()
	use_cookies = bool(os.environ.get('HTTP_COOKIE'))

	c = cookies.SimpleCookie()
	if use_cookies:
		c.load(os.environ['HTTP_COOKIE'])
	
	return url, form, use_cookies, c

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

def get_galaxy_from_url(cookies):
	# Allow for specifying galaxy in URL
	galaxy = None
	path = []
	if 'PATH_INFO' in os.environ:
		path = os.environ['PATH_INFO'].split('/')[1:]
		path = [p for p in path if p != '']

	if len(path) > 0 and path[0].isdigit():
		galaxy = dbShared.dbInsertSafe(path[0])
		cookies['galaxy'] = path[0]
		cookies['galaxy']['path'] = '/'
		print(cookies)
	
	return galaxy

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

	# logger.info(env.DB_NAME)
	# logger.info(env.DB_PASS)
	
	SUCCESS_LOGIN = 'success'

	url, form, use_cookies, c = setup_environment()

	currentUser = get_value_from_cookie(c, 'userID')
	loginResult = get_value_from_cookie(c, 'loginAttempt', SUCCESS_LOGIN)
	sid = get_value_from_form_or_cookie(form, c, 'gh_sid')
	uiTheme = get_value_from_cookie(c, 'uiTheme', ghShared.DEFAULT_THEME)
	galaxy = get_value_from_form_or_cookie(form, c, 'galaxy', ghShared.DEFAULT_GALAXY)

	# Get a session
	logged_state = 0
	linkappend = ''
	
	sess = dbSession.getSession(sid)
	# Check session validity
	if sess:
		logged_state = 1
		currentUser = sess
		
		# Get user-specific theme if not provided
		uiTheme = uiTheme or dbShared.getUserAttr(currentUser, 'themeName')
		
		# Set link append if cookies are not used
		if not use_cookies:
			linkappend = 'gh_sid=' + sid
	else:
		if env.REQUIRE_LOGIN:
			# If not logged in, render the login only page
			render_login(currentUser, loginResult)
			return
	
	galaxy = get_galaxy_from_url(c) or galaxy
	totalAmt, percentOfGoal = get_donation_total()
	galaxyAdmin = get_galaxy_admin(currentUser)
	pictureName = dbShared.getUserAttr(currentUser, 'pictureName')

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