<?php

# For command line testing
if (isset($_SERVER["HTTP_HOST"])) {
  $input_sig = $_SERVER["HTTP_X_HUB_SIGNATURE"];
  $body = file_get_contents('php://input');
} else {
  parse_str($argv[1], $_POST);
  $body = $argv[1];
  $input_sig = getenv("HTTP_X_HUB_SIGNATURE");
}


if (!$input_sig) {
  print "ERROR: No HTTP_X_HUB_SIGNATURE in request\n";
  #foreach ($_SERVER as $k => $v) {
  #  print "$k = $v\n";
  #}

  exit(1);
}

$reqdir = getenv("HOOK_REQUEST_DIR");
if (!$reqdir) {
  $reqdir = "/home/firehol/web/requests";
}
$creddir = getenv("HOOK_CREDENTIALS_DIR");
if (!$creddir) {
  $creddir = "/home/firehol/hook-credentials";
}

$url = "";
$ref = "";
$email = "";
$action = "";
$upload = "";
$given_user = "github";

if (isset($_POST['payload'])) {
  $payload = $_POST['payload'];
  $result = json_decode($payload);
  #var_dump($result);

  $ref = $result->{"ref"};
  if ($ref == "") {
    print "ERROR: No ref\n";
    error_log("ERROR: no ref in payload $payload");
    $fh = fopen("$reqdir/payload.failed", "w");
    if ($fh) {
      fwrite($fh, "$payload\n");
      fclose($fh);
    }
    exit(1);
  } else {
    $fh = fopen("$reqdir/payload.latest", "w");
      if ($fh) {
      fwrite($fh, "$payload\n");
      fclose($fh);
    }
  }

  $repository = $result->{"repository"};
  $pusher = $result->{"pusher"};

  if ($pusher->{"email"} == "") {
    $pusher = $repository->{"owner"};
  }

  if ($pusher->{"email"} == "") {
    $email = "firehol-devs@lists.firehol.org";
  } else {
    $email = $pusher->{"email"} . ", firehol-devs@lists.firehol.org";
  }

  $url = $repository->{"url"};
  $action = "build";

  error_log("GitHub Hook: URL: $url - $ref - $email - $action - $payload");
} else if (isset($_POST['action'])) {
  $action = $_POST['action'];
  $url = $_POST['url'];
  $ref = $_POST['ref'];
  $email = $_POST['email'];
  $given_user = $_POST['username'];

  error_log("Direct Post: URL: $url - $ref - $email - $action");
} else {
  print "ERROR: no payload and no action\n";
  exit(1);
}

if (!$email) {
  print "ERROR: No email\n";
  exit(1);
}

print "URL: $url\n";
print "Ref: $ref\n";
print "Email: $email\n";
print "Action: $action\n";

if ($url == "") {
  print "ERROR: No url\n";
  exit(1);
}
if ($ref == "") {
  print "ERROR: No ref\n";
  exit(1);
}
if ($action == "") {
  print "ERROR: No action\n";
  exit(1);
}

$urlpath = preg_replace('/.*github.com./', '', $url);
$organisation = preg_replace('/[^A-Za-z0-9_-].*/', '', $urlpath);

if (file_exists("$creddir/$organisation.$given_user.secret")) {
  $secret = file_get_contents("$creddir/$organisation.$given_user.secret");
  $secret = rtrim($secret);
} else {
  print "ERROR: invalid credentials\n";
  error_log("ERROR: no file - $creddir/$organisation.$given_user.secret");
  exit(1);
}

$input_sig = preg_replace('/^sha1=/', '', $input_sig);
$sig = sha1("$secret$body");
if ($sig != $input_sig) {
  print "ERROR: invalid credentials\n";
  error_log("ERROR: signature mismatch");
  error_log("given $input_sig but expected $sig");
  exit(1);
}

$fileurl = preg_replace('/[^A-Za-z0-9_-]/', '-', $urlpath);
$fileref = preg_replace('/[^A-Za-z0-9_-]/', '-', $ref);

$fh = fopen("$reqdir/prep.$fileurl.$fileref", "w");
if (!$fh) {
  print "ERROR: invalid configuration\n";
  error_log("ERROR: cannot write to $reqdir");
  exit(1);
}

fwrite($fh, "URL: $url\n");
fwrite($fh, "Ref: $ref\n");
fwrite($fh, "Email: $email\n");
fwrite($fh, "Action: $action\n");
fclose($fh);

if (file_exists("$reqdir/req.$fileurl.$fileref")) {
  unlink("$reqdir/req.$fileurl.$fileref");
}
link("$reqdir/prep.$fileurl.$fileref", "$reqdir/req.$fileurl.$fileref");
unlink("$reqdir/prep.$fileurl.$fileref");
?>
