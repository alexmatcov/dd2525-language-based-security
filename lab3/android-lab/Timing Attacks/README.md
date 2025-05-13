# Messenger Timing Attack Analysis - User Guide

This guide explains how to use the `timing_attack.py` script to analyze timing vulnerabilities in the messenger app and determine the approximate location of users based on network delays.

## Prerequisites

Before running the script, ensure you have the following installed:
- Python 3.6 or later
- ADB (Android Debug Bridge)

## Setting Up the Environment

1. Make sure Docker is installed and the server is running:
   ```bash
   ./launch.sh
   ```

2. Run the Messenger app on your Android emulator
   - You should have at least one conversation with messaging activity

## Understanding the Location Data

The script uses two tables of reference data:

1. **Table 1**: Contains RTT (Round Trip Time) from users to regional CDN servers:
   - Skyrim (803ms)
   - Morrowind (384ms)
   - Hammerfell (723ms)
   - Valenwood (547ms)
   - Elsweyr (427ms)
   - Cyrodiil (1052ms)

2. **Table 2**: Contains RTT from cities to their regional CDN server:
   - Each region has several cities with different network delays
   - For example, in Skyrim: Riften (113ms), Whiterun (375ms), etc.

The script uses these reference values to determine users' locations by matching observed timing patterns.

## Using the Script

### Option 1: Live Capture

Run the script in live capture mode to analyze logs in real-time as you interact with the app:

```bash
python messenger_timing_attack.py --live
```

While the script is running:
1. Open the Messenger app
2. Send messages to different users
3. Wait for delivery acknowledgments
4. Press Ctrl+C to stop capturing logs and view the analysis

### Option 2: Analyze from Log File

If you've already saved logs to a file, you can analyze them directly:

```bash
python messenger_timing_attack.py --logfile your_logfile.txt
```

### Filtering by User

To focus on a specific user:

```bash
python messenger_timing_attack.py --live --user 001
```

## Understanding the Results

The script generates Console output showing:

   - Average delay to server for each user
   - Inferred region based on server delay
   - Average delay to receiver for each user
   - Inferred city based on receiver delay

## Collecting ADB Logs Manually

If you prefer to collect logs manually:

```bash
# Clear existing logs
adb logcat -c

# Collect logs and save to file
adb logcat AppLog:D *:S > messenger_logs.txt
```

Then analyze these logs:

```bash
python messenger_timing_attack.py --logfile messenger_logs.txt
```

## How It Works

The script:
1. Extracts timing data from the app logs, specifically looking for:
   - `new_msg` events (when a message is sent)
   - `server_ack` events (when the server acknowledges receipt)
   - `receiver_ack` events (when the recipient acknowledges receipt)

2. Calculates delays:
   - **Time to server**: Delay between `new_msg` and `server_ack`
   - **Time to receiver**: Delay between `server_ack` and `receiver_ack`

3. Determines location:
   - Matches the observed time to server with half the RTT values in Table 1 to determine region
   - Matches the observed time to receiver with half the RTT values in Table 2 to determine city

4. Generates visualizations showing the timing patterns and a map of inferred locations

## Troubleshooting

If you encounter issues:

- Ensure the Messenger app and server are running
- Check that ADB is properly configured and working
- Verify you can see AppLog entries with: `adb logcat AppLog:D *:S`
- Make sure you have sent and received messages to generate timing data
