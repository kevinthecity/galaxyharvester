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

	resCategories = ['Creature Food','Creature Structural','Flora Food','Flora Structural','Chemical','Water','Mineral','Gas','Energy']
	resCategoryIDs = ['creature_food','creature_structural','flora_food','flora_structural','chemical','water','mineral','gas','energy_renewable']

	pictureName = dbShared.getUserAttr(currentUser, 'pictureName')
	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(os.environ['HTTP_USER_AGENT'])
	template = environ.get_template('resourcelist.html')

	print(template.render(
		uiTheme=uiTheme, 
		loggedin=logged_state, 
		currentUser=currentUser, 
		loginResult=loginResult, 
		linkappend=linkappend, 
		url=url, 
		pictureName=pictureName, 
		imgNum=ghShared.imgNum, 
		galaxyList=ghLists.getGalaxyList(), 
		resourceTypeList=ghLists.getResourceTypeList(galaxy), 
		resourceGroupList=ghLists.getResourceGroupList(), 
		planetList=ghLists.getPlanetList(galaxy), 
		resCategories=resCategories, 
		resCategoryIDs=resCategoryIDs, 
		enableCAPTCHA=env.RECAPTCHA_ENABLED, 
		siteidCAPTCHA=env.RECAPTCHA_SITEID
		)
	)

if __name__ == "__main__":
	main()
