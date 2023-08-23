#!/usr/bin/env python3

import os
import cgi
import env
import ghShared
import dbShared
import dbSession
from http import cookies

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

def get_form_and_cookie_values(form, c):
	SUCCESS_LOGIN = 'success'
	currentUser = get_value_from_cookie(c, 'userID')
	loginResult = get_value_from_cookie(c, 'loginAttempt', SUCCESS_LOGIN)
	sid = get_value_from_form_or_cookie(form, c, 'gh_sid')
	uiTheme = get_value_from_cookie(c, 'uiTheme', ghShared.DEFAULT_THEME)
	galaxy = get_value_from_form_or_cookie(form, c, 'galaxy', ghShared.DEFAULT_GALAXY)
	return currentUser, loginResult, sid, uiTheme, galaxy

def get_galaxy_from_url(c):
	# Allow for specifying galaxy in URL
	galaxy = None
	path = []
	if 'PATH_INFO' in os.environ:
		path = os.environ['PATH_INFO'].split('/')[1:]
		path = [p for p in path if p != '']

	if len(path) > 0 and path[0].isdigit():
		galaxy = dbShared.dbInsertSafe(path[0])
		c['galaxy'] = path[0]
		c['galaxy']['path'] = '/'
		print(c)
	
	try:
		galaxy = int(galaxy)
	except Exception:
		galaxy = None

	return galaxy

def setup_user_environment():
	url, form, use_cookies, c = setup_environment()
	currentUser, loginResult, sid, uiTheme, galaxy = get_form_and_cookie_values(form, c)

	galaxy = get_galaxy_from_url(c) or galaxy

	# Defaults
	logged_state = 0
	linkappend = ''

	# Get session
	sess = dbSession.getSession(sid)
	if sess:
		logged_state = 1
		currentUser = sess
		uiTheme = uiTheme or dbShared.getUserAttr(currentUser, 'themeName')
		if not use_cookies:
			linkappend = 'gh_sid=' + sid
	
	pictureName = dbShared.getUserAttr(currentUser, 'pictureName')

	return {
		'url': url,
		'currentUser': currentUser,
		'loginResult': loginResult,
		'sid': sid,
		'uiTheme': uiTheme,
		'galaxy': galaxy,
		'logged_state': logged_state,
		'linkappend': linkappend,
		'pictureName': pictureName
	}