# FireHOL infrastructure

*   [Project releases](#project-releases)
    -   [Prerequisites](#prerequisites)
    -   [Create release](#create-release)
    -   [Push release to github](#push-release-to-github)
    -   [Signing the results](#signing-the-results)
    -   [Release troubleshooting](#release-troubleshooting)
*   [Github and Travis](#github-and-travis)
    -   [Continuous integration](continuous-integration)
    -   [Deployment](#deployment)
*   [User setup](#user-setup)
    -   [GPG key](#gpg-key)
    -   [Authentication token](#authentication-token)
*   [firehol.org setup](#fireholorg-setup)
    -   [Website](#website)
    -   [SSL](#ssl)
    -   [Travis file uploads and publishing to website](#travis-file-uploads-and-publishing-to-website)
    -   [Mailing lists](#mailing-lists)

# Project releases

This section applies to `firehol`, `iprange` and `netdata`.

Note
:   If there is ever a need to release a new FireHOL 1.x, see
    the notes in `doc/release-firehol-v1.md` instead of this procedure.

## Prerequisites

Ensure local repository hooks are installed, they will take care of all
the checking and much of the work.

As well as commit rights to the repository, you need a [GPG key](#gpg-key)
to sign and verify the git tag. To automate release signing and signature
upload, you must set up an [Authentication token](#authentication-token).

## Create release

Note
:   If there is ever a need to release a new FireHOL 2.x, use the custom
    steps in `doc/release-firehol-v2.md` instead of this sub-section.

Update `configure.ac` to remove the version suffix or set it to `-rc.nn`,
update the `ChangeLog` and any `.spec.in` files.

Note
:   Pre-release tags should be of the form vx.y.z-pre.nn or vx.y.z-rc.nn
    in order to comply with http://semver.org/ without limiting the number
    of such releases.

Run `git commit` in the normal way. The hooks will detect a release and
do the following:

* Test build
* Prepare a suitable message
* Ask you to sign a tag
* Update the `configure.ac` for continuing development and commit it

If not satisfied, since we have not yet pushed anything, it is safe
to delete the local tag, and optionally roll back history:

~~~~
git tag -d vx.y.z
git log
git reset --hard commit-before-our-release
~~~~

## Push release to github

Once satisfied with the results, push the branch and tag e.g.:

~~~~
git push origin
git push origin tag va.b.c-rc.d
~~~~

Travis integration will automatically start the build process and
upload the resulting packages as a github release.


## Signing the results

Run the sign-github-release script e.g.:

~~~~
./bin/sign-github-release firehol x.y.z
~~~~

This will check the signature in git, grab any tar files, verify their
checksums and the compare the contents against git to ensure it all
matches.

If everything is OK, detached signatures are created for each tar-file
and the results uploaded to the github release.

Announce on the mailing lists (doc/announce.template) and website.


## Release troubleshooting

Signed tags are created automatically provided the commit hooks are in
place. It can happen that we want to remove a bad tag, however, from
local and from GitHub:

~~~~
git tag -d vx.y.z
git push origin :refs/tags/vx.y.z
~~~~

Note that this will not delete the tag from any other mirrored repositories;
they will get conflicts later on if we re-use the tag.


# Github and Travis

## Continuous integration

The FireHOL tools are built, tested and deployed by linking the
[travis-ci](https://travis-ci.org/) with GitHub. Current status
can be seen here, by administrators of the firehol project:

* [FireHOL](https://travis-ci.org/firehol/firehol)
* [iprange](https://travis-ci.org/firehol/iprange)
* [netdata](https://travis-ci.org/firehol/netdata)

Each repository contains a `.travis.yml` file which controls
the environment used and build steps taken.

The CI process aims to:

* Check that all git pre-commit hooks have been validated
* Build releasable (i.e. with documentation and configure script) tar-files
* Run any unit tests

If all of these are successful, the generated files are deployed.

## Deployment

After a successful build, the releasable tar-files and their checksums
are uploaded:

* to firehol.org, overwriting prior master/stable-nnn branch builds
* to GitHub (only when a tag is built)

[Automatic deployment](https://docs.travis-ci.com/user/deployment/) is set
up as part of the `.travis.yml`.

### Repository setup

GitHib/Travis integration for each repository was made using an
[Authentication token](#authentication-token) with the
"Travis CI command line client" on a development machine:

~~~~
travis setup releases
~~~~

Files are SFTP transferred to `travis@firehol.org:uploads/DIR`, from
where a cron job will move them to the website, once a final `complete.txt`
file has been created.

The SSH key has been added to each repository, (separately, since each
has separate secure environment variables), in [encrypted] form:

[encrypted]: https://docs.travis-ci.com/user/encrypting-files/

~~~~
mkdir .travis
cd .travis
cp /from/somewhere/travis_rsa .
travis login -g `cat ~/.firehol-github-oauth`
travis encrypt-file travis_rsa
rm travis_rsa
git add travis_rsa.enc
travis logout
~~~~

Note that when copying the `openssl` instruction into `.travis.yml`,
the `-in` and `-out` paths need to have the `.travis` folder added.

The .travis.yml decrypts the key, starts an ssh-agent and adds the
key to it, then deletes the file to prevent later parts of the script
gaining access to it, accidentally or otherwise.


# User setup

These sections explain the extra steps someone with commit privileges
to the firehol github repositories needs to take to be able to create
releases.

## GPG key

The key you sign with needs to be in your git configuration ($HOME/.git).

If not run:

~~~~
git config user.signingkey KEYID
~~~~

or:

~~~~
git config --global user.signingkey KEYID
~~~~

If you need to locate the identifier, run:

~~~~
gpg --list-keys
~~~~

Any new keys that will be used for signing a project should be concatenated
to that project's `packaging/gpg.keys` file. This will extract the key
in a suitable format:

~~~~
gpg --armor --export KEYID
~~~~

The key used to sign a tag is checked against this file before a build
is allowed to proceed.


## Authentication token

Signing packages and updating encrypted files both require you to have
a github API authentication token. Store it in `~/.firehol-github-oauth`.

Set up a token with `repo` rights [here](https://github.com/settings/tokens).

~~~~
echo "long-hex-string" > ~/.firehol-github-oauth
chmod 600 ~/.firehol-github-oauth
~~~~

# firehol.org setup

This repository should be exported as the home directory of a user,
firehol, who is a member of group firehol on the firehol.org server.

Create the user in the normal way, then as root:

~~~~
cd /home
rm -rf firehol
git clone https://github.com/firehol/infrastructure.git firehol
chown -R firehol:firehol firehol
find firehol -type d -exec chmod g+s \{\} \;
~~~~

To update:

~~~~
sudo -u firehol -i
git pull
~~~~

## Website

The website is built using nanoc version 3. There are newer versions
which are not compatible. At some point the site will be upgraded
to v4.

[Install docs](http://nanoc.ws/install/) are essentially, this as root:

~~~~
aptitude install rubygems
gem install nanoc --version 3.8.0
~~~~

Then:

~~~~
mkdir -p /home/web/firehol
mkdir -p /home/web/firehol/download
mkdir -p /home/web/firehol/static
mkdir -p /home/web/firehol/tmp
mkdir -p /home/web/firehol/webalizer
~~~~

The sites must be manually installed in nginx the first time, e.g.:

~~~~
cd /etc/nginx/sites-enabled
ln -s /home/web/firehol/master.conf 10-firehol-master
ln -s /home/web/firehol/master.conf 15-firehol-test
~~~~

The master site must have a lower number than all the others so that it
is used by default.

### SSL

SSL is provided by [Let's Encrypt](https://letsencrypt.org/)

Installation:

~~~~
cp -rp letsencrypt /usr/local/letsencrypt
mkdir -p /usr/local/letsencrypt/challenge
mkdir -p /usr/local/letsencrypt/certs
git clone https://github.com/lukas2511/dehydrated.git /usr/local/letsencrypt/dehydrated
echo "10 6 * * 0 root /usr/local/letsencrypt/generate.cron 2>&1" >> /etc/crontab
~~~~

Testing:

~~~~
openssl s_client -connect firehol.org:443
openssl s_client -connect www.firehol.org:443
openssl s_client -connect test.firehol.org:443
openssl s_client -connect lists.firehol.org:443
~~~~

### Website statistics

Website statistics are generated with webalizer

~~~~
aptitude install webalizer
~~~~

Initial report for all existing logs:

~~~~
    gunzip -c `ls -t /var/log/nginx/firehol-master-access*.gz | tac` | \
       webalizer - -b -i -c /home/web/firehol/static/webalizer.conf
~~~~

Rest is managed by daily cron script:

~~~~
cat - > /etc/cron.daily/webalizer-firehol <<_END_
#!/bin/sh
    cat /var/log/nginx/firehol-master-access*.1 /var/log/nginx/firehol-master-access*.log | \
    webalizer - -q -c /home/web/firehol/static/webalizer.conf
_END_
chmod +x /etc/cron.daily/webalizer-firehol
~~~~


## Travis file uploads and publishing to website

~~~~
sudo -i
useradd -m travis
mkdir /home/travis/.ssh
cp /home/firehol/travis/authorized_keys /home/travis/.ssh
chown -R travis:travis /home/travis/.ssh
chmod 0700 /home/travis/.ssh
echo "* * * * * root /home/firehol/bin/travis-project.cron /home/travis/uploads /home/web/firehol/download /home/web/firehol/static/travis-project.log" >> /etc/crontab
echo "* * * * * root /home/firehol/bin/travis-website.cron /home/travis/website /home/web/firehol /home/web/firehol/static/travis-website.log" >> /etc/crontab
~~~~

The scripts create a log of the most recent deployment attempt:

* [project deployment](https://firehol.org/travis-project.log)
* [website deployment](https://firehol.org/travis-website.log)

To see them from the command line:

~~~~
curl https://firehol.org/travis-project.log
curl https://firehol.org/travis-website.log
~~~~

## Mailing lists

The FireHOL lists use mailman as installed by default on Ubuntu/Debian
and customised as described below.

The mailman documentation is here: http://list.org/docs.html

### Web archive

Connecting mailman to nginx also requires installation of fcgiwrap.

The nginx configuration for https://lists.firehol.org/ is stored as
`nginx/sites-available/firehol-lists`. It should be copied to the
live server and linked as `sites-enabled/15-firehol-lists`.

### Postfix

Ensure lists.firehol.org is added to `/etc/postfix/main.cf` for:

* mydestination
* relay_domains

and restart postfix:

~~~~
/etc/init.d/postfix restart
~~~~

### Setting up

The .cfg files are stored under the mailman directory.

For each of firehol-devs and firehol-support:

~~~~
/usr/lib/mailman/bin/newlist --urlhost=lists.firehol.org
/usr/lib/mailman/bin/config_list -i firehol-xyz.cfg firehol-xyz
~~~~

Visit the website and add descriptions, review all settings as required
and re-save them with:

~~~~
/usr/lib/mailman/bin/config_list -o firehol-xyz.cfg firehol-xyz
~~~~

To import an existing mbox:

~~~~
/usr/lib/mailman/bin/arch --wipe firehol-devs firehol-devs.mbox
/usr/lib/mailman/bin/arch --wipe firehol-support firehol-support.mbox
~~~~

N.B. Whenever arch is run, use this to ensure that incoming mails are
correctly handled:

~~~~
    chown -R list:web /var/lib/mailman/archives/private/*
~~~~

### Archive Search

The Gmane archives of the mailing list are searchable. To set up a
search box on the mailing list archive replace the default templates:

~~~~
mkdir /var/lib/mailman/lists/firehol-devs/en
cp mailman/devs-archtoc.html \
        /var/lib/mailman/lists/firehol-devs/en/archtoc.html
cp mailman/devs-archtocnombox.html \
        /var/lib/mailman/lists/firehol-devs/en/archtocnombox.html

mkdir /var/lib/mailman/lists/firehol-support/en
cp mailman/support-archtoc.html \
        /var/lib/mailman/lists/firehol-support/en/archtoc.html
cp mailman/support-archtocnombox.html \
        /var/lib/mailman/lists/firehol-support/en/archtocnombox.html
~~~~

Ensure the new templates are used for incoming mail:

~~~~
/etc/init.d/mailman restart
~~~~

Rebuild the archives:

~~~~
/usr/lib/mailman/bin/arch firehol-devs
/usr/lib/mailman/bin/arch firehol-support
    chown -R list:web /var/lib/mailman/archives/private/*
~~~~


### Backing up

These are the key files for re-creating the mailing list:

~~~~
/var/lib/mailman/archives/private/firehol-devs.mbox/firehol-devs.mbox
/var/lib/mailman/archives/private/firehol-support.mbox/firehol-support.mbox
~~~~

For the list members use the mailman-subscribers.py script which is from:

* http://www.msapiro.net/mailman-subscribers.py

Usage:

~~~~
./mailman-subscribers.py -c -o out.csv lists.firehol.org firehol-devs pass
~~~~

Note that the script does not deal well with the complex passwords, so
the adminpw may need editing internally.
