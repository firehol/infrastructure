# Manual v1 release - without automated infrastructure

Replace 1.297 with appropriate value.

Create a signed tag and push it up manually:

~~~~
git tag -s v1.297
git push origin tag v1.297
~~~~

Download from the github release, then:

~~~~
md5sum -b firehol-1.297.tar.gz > firehol-1.297.tar.gz.md5
sha1sum -b firehol-1.297.tar.gz > firehol-1.297.tar.gz.sha
gpg --local-user $signwith --armor --detach-sign firehol-1.297.tar.gz
gpg -v firehol-1.297.tar.gz.asc
~~~~

Finally upload all the files as assets to the github release:

~~~~
firehol-1.297.tar.gz
firehol-1.297.tar.gz.md5
firehol-1.297.tar.gz.sha
firehol-1.297.tar.gz.asc
~~~~
