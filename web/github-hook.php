<?php
$payload = $_POST['payload'];
$result = json_decode($payload);
#var_dump($result);

$ref = $result->{"ref"};
if ($ref == "") {
  print "ERROR: No ref\n";
  error_log("ERROR: no ref in payload $payload");
  $fh = fopen("/home/firehol/web/requests/payload.failed", "w");
  if ($fh) {
    fwrite($fh, "$payload\n");
    fclose($fh);
  }
  exit(1);
} else {
  $fh = fopen("/home/firehol/web/requests/payload.latest", "w");
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

$url = $repository->{"url"};
$email = "firehol-devs@lists.firehol.org";
$action = "build";

error_log("GitHub Hook: URL: $url - $ref - $email - $action - $payload");

$parturl = preg_replace('/.*github.com./', '', $url);
$fileurl = preg_replace('/[^A-Za-z0-9_-]/', '-', $parturl);
$fileref = preg_replace('/[^A-Za-z0-9_-]/', '-', $ref);

if ($email == "") {
  print "ERROR: No email\n";
  error_log("ERROR: no email in payload $payload");
  exit(1);
}

print "URL: $url\n";
print "Ref: $ref\n";
print "Email: $email\n";
print "Action: $action\n";

$fh = fopen("/home/firehol/web/requests/req.$fileurl.$fileref", "w");
if (!$fh) {
  exit(1);
}
fwrite($fh, "URL: $url\n");
fwrite($fh, "Ref: $ref\n");
fwrite($fh, "Email: $email\n");
fwrite($fh, "Action: $action\n");
fclose($fh);
?>
