#!/usr/bin/env python
# (Python >= 2.6 including >= 3)

import os, sys, subprocess

# TODO '--mime-type=text/html; charset=utf-8'
# We'll have to wait until a new s3cmd is released that supports this,
# and leaving out the charset is relatively harmless
# when the HTML files are trusted and specify their own
# encoding in a <meta> tag before everything else in <head>.
# https://github.com/s3tools/s3cmd/blob/master/NEWS

cache15minutes = '--add-header=Cache-Control: max-age=900'
cache2hours = '--add-header=Cache-Control: max-age=7200'

# Use --no-delete-removed just for caution because we
# usually don't delete files.  Make us do that manually
# so things don't go wrong by accident.

# s3-lasercake caches are mainly end-users
subprocess.call(['s3cmd', 'sync',
	'--guess-mime-type',
	'--no-delete-removed',
	cache2hours,
	'--exclude=releases.html',
	'compiled/s3-lasercake/', 's3://lasercake/'])

subprocess.call(['s3cmd', 'sync',
	'--mime-type=text/html',
	'--no-delete-removed',
	cache15minutes,
	'compiled/s3-lasercake/releases.html', 's3://lasercake/releases'])

# upload helper files before uploading the HTML that includes them
subprocess.call(['s3cmd', 'sync',
	'--guess-mime-type',
	'--no-delete-removed',
	cache15minutes,
	#cache2hours
	'compiled/_cacheable/', 's3://www-lasercake-net/_cacheable/'])

# www.lasercake.net caches are shared Cloudfront as well as end-users
# It's website-y so most things have extensions and the ones
# that don't are the path-visible-to-regular-users HTML files.
subprocess.call(['s3cmd', 'sync',
	'--guess-mime-type',
	'--mime-type=text/html', #default type
	'--no-delete-removed',
	cache15minutes,
	#cache2hours
	'compiled/www.lasercake.net/', 's3://www-lasercake-net/'])

