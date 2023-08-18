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
import pymysql
import dbShared


def getStatList():
	result = ''
	result += '    <option value="ER">Entangle Resist</option>'
	result += '    <option value="CR">Cold Resist</option>'
	result += '    <option value="CD">Conductivity</option>'
	result += '    <option value="DR">Decay Resist</option>'
	result += '    <option value="FL">Flavor</option>'
	result += '    <option value="HR">Heat Resist</option>'
	result += '    <option value="MA">Malleability</option>'
	result += '    <option value="PE">Potential Energy</option>'
	result += '    <option value="OQ">Overall Quality</option>'
	result += '    <option value="SR">Shock Resist</option>'
	result += '    <option value="UT">Unit Toughness</option>'
	return result

def getThemeList():
	result = ''
	result += '      <option value="ghAlpha">Alpha Blue</option>'
	result += '      <option value="crafter">Crafter Grey</option>'
	result += '      <option value="Destroyer">Destroyer</option>'
	result += '      <option value="FSJediGray">FS Jedi</option>'
	result += '      <option value="Hutt">Hutt</option>'
	result += '      <option value="Imperial">Imperial</option>'
	result += '      <option value="ghOriginal">Original</option>'
	result += '      <option value="Rebel">Rebel</option>'
	result += '      <option value="rebelFlightSuits">Rebel Flight Suits</option>'
	result += '      <option value="WinduPurple">Windu Purple</option>'
	result += '      <option value="modernDarkMode">Dark Mode</option>'
	return result

def getSchematicTabList():
	result = ''
	result += '    <option value="1">Weapon</option>'
	result += '    <option value="2">Armor</option>'
	result += '    <option value="4">Food</option>'
	result += '    <option value="8">Clothing</option>'
	result += '    <option value="16">Vehicle</option>'
	result += '    <option value="32">Droid</option>'
	result += '    <option value="64">Chemical</option>'
	result += '    <option value="128">Bio-Chemical</option>'
	result += '    <option value="256">Creature</option>'
	result += '    <option value="512">Furniture</option>'
	result += '    <option value="1024">Installation</option>'
	result += '    <option value="2048">Jedi</option>'
	result += '    <option value="8192">Genetics</option>'
	result += '    <option value="131072">Starship Components</option>'
	result += '    <option value="262144">Ship Tools</option>'
	result += '    <option value="524288">Misc</option>'
	return result

def getGalaxyStatusList():
	result = ''
	result += '    <option value="0">Draft</option>'
	result += '    <option value="1">Active</option>'
	result += '    <option value="2">Inactive</option>'
	result += '    <option value="3">Removed</option>'
	return result

def getOptionList(sqlStr, params = None):
    result = []
    current_group = None

    # Connect to the database and execute the SQL query
    with dbShared.ghConn() as conn:
        cursor = conn.cursor()
        cursor.execute(sqlStr, params)
        
        for row in cursor:
            # Handle groupings with more than 2 columns
            if len(row) > 2:
                group_name = str(row[2])

                # If group changes, close previous optgroup and start a new one
                if current_group != group_name:
                    if current_group:
                        result.append('</optgroup>')
                    result.append(f'  <optgroup label="{group_name}">')
                    current_group = group_name

                # Add the option within the group
                result.append(f'  <option value="{row[0]}" group="{group_name}">{row[1]}</option>')

            # Handle regular options with 2 columns
            elif len(row) > 1:
                result.append(f'  <option value="{row[0]}">{row[1]}</option>')

            # Handle options with a single column
            else:
                result.append(f'  <option>{row[0]}</option>')

        # Close the last group if it exists
        if current_group:
            result.append('  </optgroup>')

    return "\n".join(result)

def getResourceTypeList(galaxy):
	if not galaxy or galaxy == -1:
		query = 'SELECT resourceType, resourceTypeName FROM tResourceType ORDER BY resourceTypeName;'
		params = ()
	else:
		query = '''
				SELECT resourceType, resourceTypeName 
				FROM tResourceType 
				WHERE (specificPlanet = 0 OR specificPlanet IN (
					SELECT DISTINCT tPlanet.planetID 
					FROM tPlanet, tGalaxyPlanet 
					WHERE (tPlanet.planetID < 11) OR 
						(tPlanet.planetID = tGalaxyPlanet.planetID AND tGalaxyPlanet.galaxyID = %s)
				)) 
				ORDER BY resourceTypeName;
				'''
		params = (galaxy,)
	
	listStr = getOptionList(query, params)
	return listStr

def getResourceGroupList():
	listStr = getOptionList('SELECT resourceGroup, groupName FROM tResourceGroup WHERE groupLevel > 1 ORDER BY groupName;')
	return listStr

def getResourceGroupListShort():
	listStr = getOptionList('SELECT resourceGroup, groupName FROM tResourceGroup WHERE groupLevel < 4 AND groupLevel > 1 ORDER BY groupName;')
	return listStr

def getGalaxyList():
	listStr = getOptionList('SELECT galaxyID, CASE WHEN galaxyNGE > 0 THEN CONCAT(galaxyName, \' [NGE]\') ELSE galaxyName END, CASE WHEN galaxyState=1 THEN "Active" ELSE "Inactive" END FROM tGalaxy WHERE galaxyState > 0 AND galaxyState < 3 ORDER BY galaxyState, galaxyName;')
	return listStr

def getPlanetList(galaxy):
    if not galaxy or galaxy == -1:
        listStr = getOptionList('SELECT planetID, planetName FROM tPlanet ORDER BY planetName')
    else:
        query = ('SELECT DISTINCT tPlanet.planetID, planetName '
                 'FROM tPlanet, tGalaxyPlanet '
                 'WHERE (tPlanet.planetID < 11) OR '
                 '(tPlanet.planetID = tGalaxyPlanet.planetID AND tGalaxyPlanet.galaxyID = %s) '
                 'ORDER BY planetName')
        params = (galaxy,)
        listStr = getOptionList(query, params)
    return listStr

def getProfessionList(galaxy):
    if not galaxy or galaxy == -1:
        query = 'SELECT profID, profName FROM tProfession WHERE galaxy=0 ORDER BY profName;'
        params = ()
    else:
        base_profs = dbShared.getBaseProfs(galaxy)
        query = ('SELECT profID, profName FROM tProfession WHERE galaxy IN (%s, %s) ORDER BY profName;')
        params = (base_profs, galaxy)

    return getOptionList(query, params)

def getObjectTypeList():
	listStr = getOptionList('SELECT objectType, typeName FROM tObjectType ORDER BY typeName;')
	return listStr
