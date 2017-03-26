#!/usr/bin/env python
# (Python >= 2.6 including >= 3)

# Creates website stuff.  `rm -r tmp compiled` to clean.

# TODO: use a real build system for this
# TODO: use some server to allow Cloudfront to serve gzipped versions
#   to user-agents that support it.
# TODO: make not-directly-user-accessed filenames/links be auto updated
#   e.g. from image.jpg to image.v5.jpg (a new name for each file contents)
#   so that _cacheable/** can be given HTTP headers to allow them to
#   be cached for a month (by Cloudfront as well as by user agents;
#   though of course they'll probably discard it from their cache sometime
#   sooner).
#
# Tools:
#   Whichever command line tools this script uses; you'll probably
#   have to install some.
# Sources:
#   src/ : Regular source files.
#   downloadable/ : Put here all the Lasercake source tarballs, binaries
#       and digital signatures that you intend to be downloadable.
#       This should always include every binary that we have ever released,
#       unless something odd happens like a released binary containing malware.
#
# Destinations:
#   tmp/ : intermediate files used in compiling but not elsewhere
#   compiled/
#     www.lasercake.net/ : canonical paths on www.lasercake.net
#         (which is hosted on Cloudfront, backed by S3 bucket 'www-lasercake-net')
#     s3-lasercake/ : goes to s3://lasercake/ i.e. lasercake.s3.amazonaws.com
#         which is used for serving the Lasercake downloads via HTTPS with
#         a semi-user-friendly URL.
#     _cacheable/ : currently goes to www.lasercake.net/_cacheable/ ,
#         and once the above TODO is resolved its contents will be cacheable
#         indefinitely (e.g. Cache-Control: max-age=5000000).  For now
#         we'll just use a few-hours-long cache duration for everything.
#     misc/ : not used directly on a website.  Currently this is stuff that
#         goes into the Lasercake binary distributions but is generated out
#         of the same stuff the website is.

import os, sys, subprocess, shutil

for directory in ('tmp', 'compiled', 'compiled/www.lasercake.net',
'compiled/s3-lasercake', 'compiled/_cacheable', 'compiled/misc'):
	try: os.makedirs(directory)
	except OSError: pass

# These operations are sorted roughly from low-runtime to high-runtime
# because in the absence of using a sensible build system, that's the
# best way to get errors for your mistakes sooner.

shutil.copyfile('src/downloads.html', 'compiled/www.lasercake.net/downloads')
# Only because we can't have a file named '' here, and S3 doesn't seem
# to support uploading to the path '/' either.  Our Cloudfront is configured
# to return the contents of '/home' for a request to '/'.  The file contains
# a <link rel="canonical"..> to specify the intended path (as all our HTML
# files do), just in case someone accesses it via /home (this <head> tag
# specifies to Google & co. which path is the canonical path to the file).
shutil.copyfile('src/index.html', 'compiled/www.lasercake.net/home')

pandoc_html = ['pandoc', '-t', 'html5', '--email-obfuscation=references',
		'--template=src/markdown-template.html']
pandoc_rtf = ['pandoc', '-t', 'rtf', '--self-contained']

# Blurb for the website
subprocess.call(pandoc_html + ["src/blurb.markdown", "-Vpagetitle:Lasercake blurb", "-Vrelcanonical=https://www.lasercake.net/blurb", '-o', 'compiled/www.lasercake.net/blurb'])

subprocess.call(pandoc_rtf + ["src/README.markdown", '-o', 'compiled/misc/ReadMe.rtf'])

subprocess.call(['convert', 'src/lasercake-snapshot.png', '-quality', '95',
	'-interlace', 'line', '-resize', '1366x768>',
	'compiled/_cacheable/lasercake-snapshot-progressive.jpg'])

resolutions = ('8x8', '16x16', '32x32', '64x64', '128x128', '256x256', '512x512', '1024x1024')
for res in resolutions:
	# I couldn't get imagemagick to create partial png transparency
	# out of an SVG, but inkscape happily does it:
	os.system(r"""inkscape --without-gui --export-png=tmp/uncrushed-icon-{0}x{1}.png --export-background-opacity=0 -w {0} -h {1} src/icon.svg""".format(*res.split('x')))
	# pngcrush, in addition to shrinking the file size,
	# removes EXIF image metadata.  It's a good thing
	# that it gets rid of the DPI metadata.
	os.system(r"""pngcrush -q tmp/uncrushed-icon-{0}.png compiled/_cacheable/icon-{0}.png""".format(res))

# We could use PNG for the favicon, but ICO supports all the same
# features (alpha channel, etc), isn't much bigger in filesize,
# and is slightly more compatible.
#
# All HTML files point explicitly to a versioned, cached favicon path,
# but it's nice to have a copy at /favicon.ico just in case
# someone is viewing a non-HTML file or in case we make a mistake.
subprocess.call(['convert', 'compiled/_cacheable/icon-16x16.png', 'compiled/_cacheable/favicon.ico'])
shutil.copyfile('compiled/_cacheable/favicon.ico', 'compiled/www.lasercake.net/favicon.ico')
shutil.copyfile('compiled/_cacheable/favicon.ico', 'compiled/s3-lasercake/favicon.ico')


# For the Windows binary.
subprocess.call(['convert']
	+ ['compiled/_cacheable/icon-{0}.png'.format(res) for res in resolutions]
	+ ['compiled/misc/icon-multires.ico'])

# ICNS is the OS X icon format.  png2icns of `libicns` is the only
# FOSS/cross-platform software I found to create them.  Its current
# version (0.8.1) doesn't support the @2x retina icon components but
# does support sizes up to 1024x1024 pixels.   Apple's `iconutil` is
# OS X 10.7+, which does not include 10.6, Linux, or Windows.
# '64x64' is not a component of ICNS files, so we explicitly list the
# resolutions.
subprocess.call(['png2icns', 'compiled/misc/icon-multires.icns']
	+ ['compiled/_cacheable/icon-{0}.png'.format(res) for res in
	('16x16', '32x32', '128x128', '256x256', '512x512', '1024x1024')])

# The path in fact is /releases, not /releases.html, but we're also creating
# a directory called /releases and our local filesystem can't handle them both
# existing at the same place (though S3 can and has to).
subprocess.call(['./create_index.py', './downloadable/', 'compiled/s3-lasercake/releases.html'])

subprocess.call(['rsync', '-a', './downloadable/', 'compiled/s3-lasercake/releases'])

