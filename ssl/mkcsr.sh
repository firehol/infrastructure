#!/bin/bash

if [ ! "$1" ]
then
  echo "Usage: mkcsr.sh host.key.pem > host.csr"
  exit 1
fi

openssl req -new -key "$1" -config <(cat <<-EOF
	[req]
	default_bits = 2048
	prompt = no
	default_md = sha256
	req_extensions = v3_req
	distinguished_name = dn
	[ dn ]
	C = GB
	ST = Cheshire
	L = Knutsford
	O = Philip Whineray
	CN = www.firehol.org
	emailAddress = hostmaster@firehol.org
	[ v3_req ]
	subjectAltName = @alt_names
	[ alt_names ]
	DNS.1=www.firehol.org
	DNS.2=firehol.org
	DNS.3=lists.firehol.org
	DNS.4=master.firehol.org
	DNS.5=test.firehol.org
	DNS.6=www.sanewall.org
	DNS.7=sanewall.org
	DNS.8=lists.sanewall.org
	DNS.9=bugs.sanewall.org
	DNS.10=git.sanewall.org
	DNS.11=download.sanewall.org
	EOF
	)
