# Releasing FireHOL v2

These instructions replace the `Create release` section of the common
release procedure for FireHOL v2 only. v1 has its own procedure and
v3 should follow the commin procedure verbatim.

## Create release

Ensure everything is checked in that should be and perform a dry run build:

~~~~
cd firehol
git status
./packaging/git-build
~~~~

Run any further tests, then ensure all files were listed in `EXTRA_DIST` in
`Makefile.am` as needed:

~~~~
./packaging/check-contents . firehol-development.tar.gz | less
~~~~

Update `ChangeLog` and `NEWS` (they will be checked before the tag is
built) and commit a new release.

Tag the commit with a signature and push it:

~~~~
git tag -s v2.x.y -m "Release version 2.x.y"
~~~~

Continue with the `Push release to github` step in the main procedure.
