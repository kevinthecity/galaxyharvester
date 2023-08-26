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
sys.path.append("../")
import env
import ghShared
from jinja2 import Environment, FileSystemLoader

def main():
	print('Content-type: text/html\n')
	environ = Environment(loader=FileSystemLoader('templates'))
	environ.globals['BASE_SCRIPT_URL'] = ghShared.BASE_SCRIPT_URL

	userAgent = os.environ.get('HTTP_USER_AGENT', 'unknown')
	environ.globals['MOBILE_PLATFORM'] = ghShared.getMobilePlatform(userAgent)

	template = environ.get_template('missing.html')

	print(template.render(CONTACT_EMAIL=env.CONTACT_EMAIL))

if __name__ == "__main__":
	main()