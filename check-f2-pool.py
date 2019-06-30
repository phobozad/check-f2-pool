#!/usr/bin/env python

import requests
import sys
import argparse

# Argument Parsing
parser = argparse.ArgumentParser(description="Query F2Pool.com mining pool API to get current mining hashrate for a given account.  Default is total hasrate for the user.  May also specify a worker name to query only for the hashrate of that worker.")
parser.add_argument("-w", metavar="HASHRATE", type=float, dest="warnThresh", help="Warning threshold", required=True)
parser.add_argument("-c", metavar="HASHRATE", type=float, dest="critThresh", help="Critical threshold", required=True)
parser.add_argument("-u", metavar="URL", dest="url", help="URL to pool's API (include port)", default="https://api.f2pool.com/")
parser.add_argument("--coin", metavar="COIN", dest="coinName", help="Coin name being mined (e.g. grin-31)", required=True)
parser.add_argument("-a", metavar="ACCOUNT", dest="accountName", help="Account to query on", required=True)
parser.add_argument("--worker", metavar="WORKERNAME", dest="workerName", help="Query the hashrate for a single worker named WORKERNAME", default=None)



args = parser.parse_args()

# Verify parameters passed in

warnThresh = args.warnThresh
critThresh = args.critThresh
url = args.url.rstrip("/")
coinName = args.coinName
accountName = args.accountName
workerName = args.workerName


if warnThresh < critThresh:
	print "Error: Warning threshold must be greater than critical threshold"
	sys.exit(3)


# Variables
exitCode=3
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


url+="/{coin}/{account}".format(coin=coinName, account=accountName)

#if workerName!=None:
#	url+="/{worker}".format(worker=workerName)


# Get the data & parse it

response = requests.get(url=url)

if response.status_code == requests.codes.ok:
	apiData = response.json()
	
	# Extract the relevant hashrate data	
	# If a specific worker was specified, extract that data
	if workerName!=None:
		# Parse worker list of lists to a dict of lists.
		# This allows looking up worker data with workerName as a key
		# The F2 API format has index 0 as the worker name
		apiDataParsed = {worker[0]: worker[1:] for worker in apiData["workers"]}

		# Fire an error if the specified workername isn't in the JSON object from the server
		try:
			# The current hashrate for the worker was index 1, but is now index 0 (stripped off name as index 1)
			hashRate=apiDataParsed[workerName][0]
		except KeyError:
			exitCode=3
			print "Error - Worker name not found"
			sys.exit(exitCode)
	# Otherwise just grab the global hashrate
	else:
		hashRate=apiData["hashrate"]

	
	# Evaluate the returned data to determine our monitor state & ouput
	if hashRate < critThresh:
		exitCode=2
		output="Critical - Hash rate: {} H/s".format(hashRate)
	elif hashRate < warnThresh:
		exitCode=1
		output="Warning - Hash rate: {} H/s".format(hashRate)
	else:
		exitCode=0
		output="OK - Hash rate: {} H/s".format(hashRate)

	output += " | Hashrate={};{};{};;".format(hashRate, warnThresh, critThresh)
	print output

else:
	exitCode=3
	print "HTTP Error: {}".format(response.status_code)

sys.exit(exitCode)
