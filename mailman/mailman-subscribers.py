#!/usr/bin/env python
# vi: set et sw=4 st=4:
#
# 2004-08-27 Jim Tittsler <jwt@starship.python.net>
# 2004-10-03 jwt    change authentication
# 2004-10-04 jwt    remove dependency on ClientCookie
# 2004-10-07 jwt    use getopt to retrieve host, list, password from command
# 2004-10-10 jwt    return to using ClientCookie
# 2004-10-13 jwt    add --fullnames option
# 2005-02-15 jwt    switch on RFC2965 cookie support when newer version
#                     of ClientCookie is detected
# 2005-02-16 jwt    use Python 2.4's cookielib if it is available
# 2005-02-27 jwt    only visit the roster page for letters that exist
# 2005-06-04 mas    add --nomail option (Mark Sapiro <mark@msapiro.net>)
# 2005-06-14 jwt    handle chunks of email addresses starting [0-9]*
# 2006-01-27 mas    Retry urllib2.URLError exceptions in main loop.
#                   Modify parser to get most of the member attributes on the
#                     page (I don't get nomail reason because I haven't yet
#                     figured out how, and I don't get the language option).
#                     This provides a foundation for adding options to deal
#                     with any of these attributes.
# 2006-01-28 mas    Add --regular and --digest options.
# 2006-01-29 mas    Get the nomail reason (I figured out how)
#                   Add the --csv option intended to produce a file that can
#                     be imported into a local spreadsheet. Mostly useful for
#                     larger lists when multiple sublists are desired and where
#                     multiple passes are expensive.
# 2006-04-10 mas    Add some error checking for invalid URL (hostname),
#                     listname and password.
# 2006-04-11 mas    Correct test on find(). Success is '>= 0', not 'True'.
# 2006-08-24 mas    Catch more exceptions on invalid URLs.
#                   Add some more explaination of hostname and when
#                     member_url might need changing.
# 2006-09-20 Ed Lally <elally@jersey.net>
# 2006-09-20 ejl    Add config variable for admin path (/mailman/admin/) for
#                     sites that don't use default URLs.
# 2006-09-21 mas    Make Ed's change a command line option.
# 2007-05-07 mas    Acommodate possible urllib.quote()ed email addresses.
# 2008-02-03 mas    Clarify that script works with Membership list through
#                   2.1.10.
#                   Fix broken --url_path option.
# 2008-10-06 mas    Works with 2.1.11.
#                   Handle chunks starting with other than [0-9A-Z].
#                   Print verbose output to stderr.
# 2008-10-07 mas    Added -U/--unhide option
# 2008-10-09 mas    Forgot to make the unhide '.' prints conditional on
#                   verbose. Also, csv printed "on" for members changed to
#                   unhidden. Fixed.
# 2011-10-24 mas    Added type to nomail selection.
# 2012-10-20 mas    Encode real name as iso-8859-1 to avoid Unicode error
#                   with non-ascii.
# 2012-11-14 jak    Added support to use HTTPS (james@jameskinnaird.ca)
# 2013-01-25 mas    Revised the help for -u.
#

"""List the email addresses subscribed to a mailing list, fetched from web.

Usage: %(PROGRAM)s [options] hostname listname password

Where:
   --output file
   -o file
       Write output to specified file instead of standard out.

   --regular
   -r
       List only the regular (non-digest) members.

    --digest={any|mime|plain}
    -d {any|mime|plain}
       List only the digest members. One of 'any', 'mime' or 'plain'
       is required.
       'any' lists all the digest members.
       'mime' lists only the mime digest members.
       'plain' lists only the plain digest members.

   --fullnames
   -f
       Include the full names in the output.

   --nomail={any|admin|bounce|user|unknown|enabled}
   -n {any|admin|bounce|user|unknown|enabled}
       List members based on their nomail status. One of 'any', 'admin',
       'bounce', 'user', 'unknown' or 'enabled' is required.
       'any' lists members with delivery disabled for any reason.
       'admin' lists members with delivery disabled by admin.
       'bounce' lists members with delivery disabled by bounce.
       'user' lists members with delivery disabled by the member.
       'unknown' lists members with delivery disabled by mailman 2.0
       'enabled' lists members with delivery enabled.

   --csv
   -c
       This option overrides the above four selection options and lists
       all members, one per line, with comma separated, quoted values as
       follows:
          "full name" if available, else "","email address","mod",
          "hide","nomail" ("off" or "[A]" or "[B]" or "[U]" or "[?]"),
          "ack","not metoo","nodupes","digest","plain"
       analogous to the admin membership list (the values of the 'checkbox'
       fields are either "off" or "on"). A title line with the above names
       is listed before the member lines.

   --url_path path
   -u path
       If the list admin pages are accessed at your site via a URL of form
       different from http://hostname/mailman/admin/listname, you need to
       specify the path portion of the URL that is between hostname and
       /listname with this option. For example, a URL such as
       http://hostname/admin.cgi/listname requires the option
       --url_path /admin.cgi
       or
       -u /admin.cgi
       and a URL like http://hostname/cgi-bin/mailman/admin/listname
       requires the option
       --url_path /cgi-bin/mailman/admin
       or
       -u /cgi-bin/mailman/admin
       Default value is /mailman/admin.

   --unhide
   -U
       Set the 'hidden' flag off for all list members including those not
       selected for output.  This will take a long time if there are a lot
       of hidden members.  The -v option prints '.' after every 100 unhides.

   --ssl
   -s
       Use https instead of http for accessing the list.

   --verbose
   -v
       Include extra progress output.

   --help
   -h
       Print this help message and exit

   hostname is the name used in the URL of the list's web interface
   listname is the name of the mailing list
   password is the list's admin password

   The list of subscribers is fetched from the web administrative
   interface.  Using the bin/list_members program from a shell
   account is preferable, but not always available.

   Tested with the Mailman 2.1.5 - 2.1.15 Membership list layout.

   If Python 2.4's cookielib is available,  use it.  Otherwise require
   ClientCookie  http://wwwsearch.sourceforge.net/ClientCookie/

   This script runs on your workstation and requires that you have Python
   <http://www.python.org> installed. It works best with Python 2.4.x
   through Python 2.6.x. It is not tested with Python 3.x.x.
"""

import sys
import re
import string
import urllib
import getopt
import httplib
import urllib2
from time import sleep
from HTMLParser import HTMLParser
# if we have Python 2.4's cookielib, use it
try:
    import cookielib
    policy = cookielib.DefaultCookiePolicy(rfc2965 = True)
    cookiejar = cookielib.CookieJar(policy)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar)).open
except ImportError:
    import ClientCookie
    # if this is a new ClientCookie, we need to turn on RFC2965 cookies
    cookiejar = ClientCookie.CookieJar()
    try:
        cookiejar.set_policy(ClientCookie.DefaultCookiePolicy(rfc2965 = True))
        # install an opener that uses this policy
        opener = ClientCookie.build_opener(
                ClientCookie.HTTPCookieProcessor(cookiejar))
        ClientCookie.install_opener(opener)
    except AttributeError:
        # must be an old ClientCookie, which already accepts RFC2965 cookies
        pass
    opener = ClientCookie.urlopen

PROGRAM = sys.argv[0]

try:
    True, False
except NameError:
    True = 1
    False = 0

def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__ % globals()
    if msg:
        print >> fd, msg
    sys.exit(code)

subscribers = {}
vnames = ['_realname', '_mod', '_hide', '_nomail', '_ack', '_notmetoo',
          '_nodupes', '_digest', '_plain']
maxchunk = 0
letters = ['0']
processed_letters = []
gotnomail = False

class MailmanHTMLParser(HTMLParser):
    '''cheap way to find email addresses and pages with multiple
       chunks from Mailman 2.1.5 membership pages'''
    def handle_starttag(self, tag, attrs):
        global maxchunk, letters, gotnomail, subemail, url_path
        if tag == 'input':
            for vname in vnames:
                s = False
                for a,v in attrs:
                    if a == 'name' and v.endswith(vname):
                        subemail = v[:-len(vname)]
                        s = True
                    elif a == 'value':
                        subval = v
                if s:
                    if not subscribers.has_key(subemail):
                        subscribers[subemail] = {}
                    if vname == '_nomail' and subval == "on":
                        gotnomail = True
                    else:
                        subscribers[subemail][vname] = subval.encode(
                                                       'iso-8859-1', 'replace')
        if tag == 'a':
            for a,v in attrs:
                if a == 'href' and v.find("%s/" % (url_path)) >= 0:
                    m = re.search(r'chunk=(?P<chunkno>\d+)', v, re.I)
                    if m:
                        if int(m.group('chunkno')) > maxchunk:
                            maxchunk = int(m.group('chunkno'))
                    m = re.search(r'letter=(?P<letter>.)', v, re.I)
                    if m:
                        letter = m.group('letter')
                        if letter not in letters + processed_letters:
                            letters.append(letter)

    def handle_data(self, data):
        global gotnomail, subemail
        if gotnomail:
            gotnomail = False
            subscribers[subemail]['_nomail'] = data

def main():
    global maxchunk, letters, url_path
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:rd:fn:cu:Uvs",
                ["help", "output=", "regular", "digest=", "fullnames",
                 "nomail=", "csv", "url_path=", "unhide", "verbose",
                 "ssl"])
    except:
        usage(2)
    fp = sys.stdout
    fullnames = False
    nomail = None
    verbose = False
    regular = False
    digest = None
    csv = False
    unhide = False
    protocol = 'http'
    url_path = '/mailman/admin'
    for o,a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        if o in ("-h", "--help"):
            usage(0)
        if o in ("-o", "--output"):
            fp = open(a, "wt")
        if o in ("-f", "--fullnames"):
            fullnames = True
        if o in ("-n", "--nomail"):
            nomail = a.lower()
        if o in ("-r", "--regular"):
            regular = True
        if o in ("-d", "--digest"):
            digest = a.lower()
        if o in ("-c", "--csv"):
            csv = True
        if o in ("-u", "--url_path"):
            url_path = a
        if o in ("-U", "--unhide"):
            unhide = True
        if o in ("-s", "--ssl"):
            protocol = 'https'
    if regular and digest:
        usage(2, "Both 'regular' and 'digest' will produce an empty list.")
    if digest not in [None, 'any', 'mime', 'plain']:
        usage(2, "Digest type %s unrecognized" % digest)
    if nomail not in [None, 'any', 'admin', 'bounce', 'user', 'unknown',
                      'enabled']:
        usage(2, "Nomail type %s unrecognized" % nomail)
    if len(args) != 3:
        usage(2)

    member_url = '%s://%s%s/%s/members' % (protocol, args[0], url_path,
                                           args[1])
    options_url = '%s://%s%s/%s' % (protocol, args[0],
                                    re.sub('admin', 'options', url_path),
                                    args[1])
    p = {'adminpw':args[2]}
        

    # login, picking up the cookie
    try:
        page = opener(member_url, urllib.urlencode(p))
    except (urllib2.URLError, httplib.InvalidURL):
        usage(1, """Error accessing %s
Supplied host may be incorrect or you may need to specify --url_path.
""" % (member_url))
    lines = page.read()
    page.close()
    p = {}
    # Try to recognize the returned page independent of the list language
    if re.search(r'INPUT\s+type="SUBMIT"\s+name="admlogin"', lines,
                 re.M + re.I):
        # login page - invalid password
        usage(1, 'Invalid password.')
    if not re.search(r'<form\s+action=', lines, re.M + re.I):
        # no <form> tag - admin overview page
        usage(1, """Non-existent list: %s.
If the provided list name is valid, the supplied host may be incorrect
or you may need to specify --url_path.
""" % args[1])

    # loop through the letters, and all chunks of each
    while len(letters) > 0:
        letter = letters[0]
        letters = letters[1:]
        processed_letters.append(letter)
        chunk = 0
        maxchunk = 0
        while chunk <= maxchunk:
            if verbose:
                print >> sys.stderr, "%c(%d)" % (letter, chunk)
            while True:
                try:
                    page = opener(member_url + "?letter=%s&chunk=%d" %
                            (letter, chunk))
                    lines = page.read()
                    page.close()
                except urllib2.URLError:
                    if verbose:
                        print >> sys.stderr,\
                            'Error encountered in accessing web page.',\
                            'Retrying.'
                    sleep(2)
                else:
                    break

            parser = MailmanHTMLParser()
            parser.feed(lines)
            parser.close()
            chunk += 1

    subscriberlist = subscribers.items()
    subscriberlist.sort()

    # print the subscribers list
    if csv:
        print >>fp, '"Full name","email address","mod","hide",\
"nomail","ack","not metoo","nodupes","digest","plain"'

    nunhide = 0
    for (email, d) in subscriberlist:
        if unhide and d['_hide'] == "on":
            params = urllib.urlencode({'conceal':0,
                                       'options-submit':1})
            u = opener("%s/%s" % (options_url, email), params)
            u.close()
            d['_hide'] = "off"
            nunhide += 1
            if verbose and nunhide % 100 == 0:
                print >>sys.stderr, '.',
        email = urllib.unquote(email)
        if csv:
            print >>fp,\
                '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"'\
                 % (d['_realname'], email, d['_mod'], d['_hide'],
                    d['_nomail'], d['_ack'], d['_notmetoo'],
                    d['_nodupes'], d['_digest'], d['_plain'])
            continue
        if nomail == 'enabled' and d['_nomail'] <> "off":
            continue
        if nomail == 'any' and d['_nomail'] == "off":
            continue
        if nomail == 'admin' and d['_nomail'] <> "[A]":
            continue
        if nomail == 'bounce' and d['_nomail'] <> "[B]":
            continue
        if nomail == 'user' and d['_nomail'] <> "[U]":
            continue
        if nomail == 'unknown' and d['_nomail'] <> "[?]":
            continue
        if regular and d['_digest'] == "on":
            continue
        if digest and d['_digest'] == "off":
            continue
        if digest == "mime" and d['_plain'] == "on":
            continue
        if digest == "plain" and d['_plain'] == "off":
            continue
        if not fullnames or d['_realname'] == "":
            print >>fp, email
        else:
            print >>fp, '%s <%s>' % (d['_realname'], email)

    fp.close()


if __name__ == '__main__':
    main()

