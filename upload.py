#!/usr/bin/env python
# (Python >= 2.6 including >= 3)

import os, sys, subprocess

# TODO '--mime-type=text/html; charset=utf-8'
# We'll have to wait until a new s3cmd is released that supports this,
# and leaving out the charset is relatively harmless
# when the HTML files are trusted and specify their own
# encoding in a <meta> tag before everything else in <head>.
# https://github.com/s3tools/s3cmd/blob/master/NEWS

# Note that Cloudfront allows any cache duration from 0 on up,
# but if you don't specify one, it will default to caching for
# 24 hours.  So specify!
# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html
#cache15minutes = '--add-header=Cache-Control: max-age=900'
#cache2hours = '--add-header=Cache-Control: max-age=7200'
cache15minutes = '--cache-control=max-age=900'
cache2hours = '--cache-control=max-age=7200'

# Use --no-delete-removed just for caution because we
# usually don't delete files.  Make us do that manually
# so things don't go wrong by accident.

# s3-lasercake caches are mainly end-users
subprocess.call(['aws', 's3', 'sync',
        '--metadata-directive=REPLACE',
	cache2hours,
	'--exclude=releases.html',
	'compiled/s3-lasercake/', 's3://lasercake/'])

subprocess.call(['aws', 's3', 'cp',
        '--metadata-directive=REPLACE',
	'--content-type=text/html; charset=utf-8',
	cache15minutes,
	'compiled/s3-lasercake/releases.html', 's3://lasercake/releases'])

# upload helper files before uploading the HTML that includes them
subprocess.call(['aws', 's3', 'sync',
        '--metadata-directive=REPLACE',
	cache15minutes,
	#cache2hours
	'compiled/_cacheable/', 's3://www-lasercake-net/_cacheable/'])

# www.lasercake.net caches are Cloudfront as well as end-users.
# It's website-y so most things have filename extensions, and the
# ones that don't are the path-visible-to-regular-users HTML files.
# `file --mime-type` can identify these because they start with
# the <!DOCTYPE html>.  Alas, AWS's mime-type guessing can't.
#subprocess.call(['aws', 's3', 'sync',
#        '--metadata-directive=REPLACE',
#	cache15minutes,
#	#cache2hours
#	'compiled/www.lasercake.net/', 's3://www-lasercake-net/'])
for html in ['home', 'downloads', 'blurb']:
    subprocess.call(['aws', 's3', 'cp',
        '--metadata-directive=REPLACE',
        '--content-type=text/html; charset=utf-8',
	cache15minutes,
	#cache2hours
	'compiled/www.lasercake.net/'+html, 's3://www-lasercake-net/'+html])
for inferred in ['favicon.ico']:
    subprocess.call(['aws', 's3', 'cp',
        '--metadata-directive=REPLACE',
	cache15minutes,
	#cache2hours
	'compiled/www.lasercake.net/'+inferred, 's3://www-lasercake-net/'+inferred])

