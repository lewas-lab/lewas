#!/usr/bin/env python

import re
import argparse
import json, urllib, urllib2, ConfigParser, os, sys
from datetime import datetime

http_errors = r'HTTP Error ([45]0[02])'
request_data = r'\s*request: (\{.*)$'

http_re = re.compile(http_errors)
request_re = re.compile(request_data)

def request_generator(instream):
    message_on_next = False
    code = 200
    for line in instream:
        if message_on_next:
            message_on_next = False
            m = request_re.match(line)
            request = {}
            if m:
                try:
                    request = json.loads(m.group(1))
                except ValueError:
                    pass
                yield code, request

        m = http_re.match(line)
        if m:
            code = int(m.group(1))
            message_on_next = True

if __name__ == '__main__':
    sys.stderr.write("entering __main__\n")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--site", default='test1', help="The site id to post to, e.g. 'test1'")
    parser.add_argument("-i","--instrument", help="The instrument to post to, e.g. 'sonde'")

    host = 'http://localhost:8080'
    endpoint = '/observations'

    args = parser.parse_args()

    if not args.instrument:
        sys.stderr.write("Error: instrument argument is required")

    sys.stderr.write("about to read lines\n")
    for code, request in request_generator(sys.stdin):
        if not code == 500:
            continue
        url = urllib2.Request(host + urllib2.quote('/sites/' + args.site + '/instruments/' \
                                                   + args.instrument + endpoint), json.dumps(request, indent=4),
                              {'Content-Type': 'application/json'})
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if not e.code == 409:
                sys.stderr.write("{}\n\trequest: {}\n".format(e, json.dumps(request)))
                response = None
            else:
                sys.stderr.write("conflict, probably due to duplicate data\n")
        except urllib2.URLError as e:
            sys.stderr.write("{}\n\turl: {}\n".format(e, url))
            response = None


