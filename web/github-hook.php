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
$email = $pusher->{"email"};
$action = "build";

$filename = preg_replace('/[^A-Za-z0-9_-]/', '-', $ref);
print "Ref: $ref\n";
print "Email: $email\n";
print "Action: build\n";

$fh = fopen("/home/firehol/web/requests/req.$filename", "w");
if (!$fh) {
  exit(1);
}
fwrite($fh, "Ref: $ref\n");
fwrite($fh, "Email: $email\n");
fwrite($fh, "Action: build\n");
fclose($fh);
?>
