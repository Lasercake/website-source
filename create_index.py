#!/usr/bin/env python
# (Python >= 2.6 including >= 3)
"""Usage: ./create-index.py path/to/directory [output file]
    Indexes every file under the directory (recursively)
    in a single index HTML file.  This somewhat resembles
    the directory indexes that Apache generates, but
    differs in several details.  The generated HTML
    is written to [output file] or else stdout.
"""

import sys, os, hashlib, cgi, distutils.version

### helper functions ###

def sha256file(path):
        # http://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
        hash1 = hashlib.sha256()
        with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(2**20), b''):
                        hash1.update(chunk)
        return hash1


def escape(s): return cgi.escape(s, True)

def human_size_str(n):
	k = 1024
	if   n < k**1: return str(n)
	elif n < k**2: return str(round(n/k**1, 1))+'kiB'
	elif n < k**3: return str(round(n/k**2, 1))+'MiB'
	elif n < k**4: return str(round(n/k**3, 1))+'GiB'
	else         : return str(round(n/k**4, 1))+'TiB'


### main script ###

# Compute the location of the destination file here
# so it's not affected by the chdir, but only open
# the file at the end so that it's not created as an
# empty file if this script has an error or is interrupted.
destfile = None
if len(sys.argv) > 2:
	destfile = os.path.abspath(sys.argv[2])

# Chdir to simplify the path-displaying code below.
os.chdir(sys.argv[1])

output = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Lasercake releases</title>
<link rel="shortcut icon" href="//d2dvq9ryeo0vx7.cloudfront.net/_cacheable/favicon.ico" />
<link rel="canonical" href="https://lasercake.s3.amazonaws.com/releases" />
<style>
body{font-size:16px;background-color:#ddff99;color:black;}
th{text-align:left;}
td{font-family:Andale Mono,monospace;}
body,td:first-child{font-family:Verdana,sans-serif;}
p,th,td{padding: 0 0.5em;}
a:link{color:blue;}
a:visited{color:purple;}
</style>
</head>
<body>
<p><a href="http://www.lasercake.net/"><img src="//d2dvq9ryeo0vx7.cloudfront.net/_cacheable/icon-64x64.png" alt="Lasercake" /></a> <a href="http://www.lasercake.net/downloads">[back]</a></p>
<p>PGP sigs are by Isaac Dupree, fingerprint AC5B DA24 40BD BF34 C4C7 DCF3 9ADC 2732 1706 2391</p>
<table>
<tr>
<th>file</th>
<th>size</th>
<th>SHA256</th>
</tr>
"""

fpaths = []
for fdir, subdirs, files in os.walk('./'):
	for fname in files:
		fpaths.append(os.path.join(fdir, fname)[2:])
for fpath in sorted(fpaths, key=distutils.version.LooseVersion):
	line = """<tr><td><a href="{path}">{path}</a></td><td>{size}</td><td>{sha}</td></tr>\n""".format(
		sha = escape(sha256file(fpath).hexdigest()),
		size = escape(human_size_str(os.stat(fpath).st_size)),
		path = escape(fpath))
	output += line

output += """</table>
</body>
</html>
"""

# Don't open the output file until here so that a Python error above
# won't leave a blank file sitting there.
if destfile != None:
	with open(destfile, 'w') as f:
		f.write(output)
else:
	sys.stdout.write(output)

