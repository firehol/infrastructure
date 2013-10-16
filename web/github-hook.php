<?php
$payload = $_POST['payload'];
$result = json_decode($payload);
#var_dump($result);

$ref = $result->{"ref"};
if ($ref == "") {
  print "ERROR: No ref\n";
  exit(1);
}

$pusher = $result->{"pusher"};
$repository = $result->{"repository"};
$url = $repository->{"url"};
$email = $pusher->{"email"};
$action = "build";

print "URL: $url\n";
print "Ref: $ref\n";
print "Email: $email\n";
print "Action: build\n";

$parturl = preg_replace('/.*github.com./', '', $url);
$fileurl = preg_replace('/[^A-Za-z0-9_-]/', '-', $parturl);
$fileref = preg_replace('/[^A-Za-z0-9_-]/', '-', $ref);

$fh = fopen("/home/firehol/web/requests/req.$fileurl.$fileref", "w");
if (!$fh) {
  exit(1);
}
fwrite($fh, "URL: $url\n");
fwrite($fh, "Ref: $ref\n");
fwrite($fh, "Email: $email\n");
fwrite($fh, "Action: build\n");
fclose($fh);
?>
