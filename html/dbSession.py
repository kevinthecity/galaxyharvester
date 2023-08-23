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

import time
import dbShared

# make sure the sessions table exists
def verifySessionDB():
	conn = dbShared.ghConn()
	cursor = conn.cursor()
	cursor.execute("show tables like 'tSessions';")
	row = cursor.fetchone()
	if row == None:
		tablesql = "CREATE TABLE tSessions (sid VARCHAR(40) NOT NULL PRIMARY KEY, userID VARCHAR(32) NOT NULL, expires FLOAT, pushKey VARCHAR(255));"
		cursor.execute(tablesql)
	cursor.close()
	conn.close()

def getSession(sid):
    conn = dbShared.ghConn()
    cursor = conn.cursor()

    # Using parameterized query for sid lookup
    cursor.execute("SELECT userID, expires FROM tSessions WHERE sid = %s", (sid,))
    row = cursor.fetchone()

    if row is None:
        result = ""
    else:
        if time.time() > row[1]:
            result = ""
            # Using parameterized query for session deletion
            cursor.execute("DELETE FROM tSessions WHERE sid = %s", (sid,))
        else:
            # Valid session
            result = row[0]

    cursor.close()
    conn.close()

    return result
