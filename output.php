<?php
// Load the JSON data from the output file
$output = json_decode(file_get_contents('output.json'), true);

// Default values if JSON file is not found
if (!$output) {
    $output = [
        "error" => "N/A",
        "anomaly" => false,
        "sensor_data" => []
    ];
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bird Migration Anomaly Detection</title>
    <style>
        /* styles.css */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }

        body {
            background-color: #f4f7fc;
            color: #333;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        h1 {
            color: #0052cc;
            font-size: 32px;
        }

        h2 {
            font-size: 24px;
            margin-bottom: 10px;
            color: #007bff;
        }

        section {
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        table th, table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: center;
        }

        table th {
            background-color: #f2f2f2;
        }

        .status-message {
            font-size: 18px;
            font-weight: bold;
        }

        .status-message.anomaly {
            color: #d9534f;
        }

        .status-message.normal {
            color: #5bc0de;
        }

        .alert {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ffeeba;
        }

        .alert p {
            font-weight: bold;
            color: #856404;
        }

        footer {
            text-align: center;
            font-size: 14px;
            color: #777;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Bird Migration Anomaly Detection</h1>
        </header>
        
        <section class="status">
            <h2>Status</h2>
            <p id="statusMessage" class="status-message">
                <?php
                if ($output['anomaly']) {
                    echo "Anomaly Detected!";
                } else {
                    echo "No Anomaly";
                }
                ?>
            </p>
        </section>

        <section class="error">
            <h2>Prediction Error</h2>
            <p id="predictionError"><?php echo $output['error']; ?></p>
        </section>

        <section class="sensor-data">
            <h2>Latest Sensor Data</h2>
            <table id="sensorData">
                <thead>
                    <tr>
                        <th>Latitude</th>
                        <th>Longitude</th>
                        <th>Temperature</th>
                        <th>Humidity</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    foreach ($output['sensor_data'] as $row) {
                        echo "<tr>";
                        foreach ($row as $cell) {
                            echo "<td>$cell</td>";
                        }
                        echo "</tr>";
                    }
                    ?>
                </tbody>
            </table>
        </section>

        <section class="alert">
            <h2>Alert</h2>
            <p id="alertMessage">
                <?php
                if ($output['anomaly']) {
                    echo "⚠️ Anomaly Detected. Action is required!";
                } else {
                    echo "Everything is normal.";
                }
                ?>
            </p>
        </section>

        <footer>
            <p>&copy; 2025 Bird Migration Project</p>
        </footer>
    </div>
</body>
</html>
