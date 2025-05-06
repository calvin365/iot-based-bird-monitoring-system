<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "sensor_data";

// Connect to database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

if (
  isset($_POST['latitude']) &&
  isset($_POST['longitude']) &&
  isset($_POST['temperature']) &&
  isset($_POST['humidity']) &&
  isset($_POST['satellites'])
) {
  $latitude = $_POST['latitude'];
  $longitude = $_POST['longitude'];
  $temperature = $_POST['temperature'];
  $humidity = $_POST['humidity'];
  $satellites = $_POST['satellites'];

  $sql = "INSERT INTO sensor_readings (latitude, longitude, temperature, humidity, satellites)
          VALUES ('$latitude', '$longitude', '$temperature', '$humidity', '$satellites')";

  if ($conn->query($sql) === TRUE) {
    echo "Data inserted successfully";
  } else {
    echo "Error: " . $conn->error;
  }
} else {
  echo "Error: Missing required POST data.";
}

$conn->close();
?>
