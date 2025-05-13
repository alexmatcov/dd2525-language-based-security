import subprocess
import re
import time
import argparse
from datetime import datetime
from collections import defaultdict

# Configure argument parser
parser = argparse.ArgumentParser(description='Analyze timing attacks on Messenger app')
parser.add_argument('--live', action='store_true', help='Capture logs in real-time')
parser.add_argument('--logfile', type=str, help='Analyze from log file instead of live capture')
parser.add_argument('--user', type=str, default='all', help='Specific user ID to analyze')
args = parser.parse_args()

# Known delays for regions from Table 1
REGIONS = {
    "Skyrim": {"rtt": 803},
    "Morrowind": {"rtt": 384},
    "Hammerfell": {"rtt": 723},
    "Valenwood": {"rtt": 547},
    "Elsweyr": {"rtt": 427},
    "Cyrodiil": {"rtt": 1052}
}

# Cities and their RTT to their regional server from Table 2
CITIES = {
    # Skyrim cities
    "Riften": {"rtt": 113, "region": "Skyrim"},
    "Whiterun": {"rtt": 375, "region": "Skyrim"},
    "Windhelm": {"rtt": 342, "region": "Skyrim"},
    "Solitude": {"rtt": 312, "region": "Skyrim"},
    "Markarth": {"rtt": 149, "region": "Skyrim"},
    "Falkreath": {"rtt": 255, "region": "Skyrim"},
    
    # Morrowind cities
    "Vivec": {"rtt": 247, "region": "Morrowind"},
    "Mournhold": {"rtt": 345, "region": "Morrowind"},
    "Balmora": {"rtt": 307, "region": "Morrowind"},
    "Ald'ruhn": {"rtt": 128, "region": "Morrowind"},
    "Blacklight": {"rtt": 387, "region": "Morrowind"},
    "Narsis": {"rtt": 289, "region": "Morrowind"},
    
    # Hammerfell cities
    "Sentinel": {"rtt": 157, "region": "Hammerfell"},
    "Rihad": {"rtt": 286, "region": "Hammerfell"},
    "Taneth": {"rtt": 336, "region": "Hammerfell"},
    "Elinhir": {"rtt": 305, "region": "Hammerfell"},
    "Dragonstar": {"rtt": 356, "region": "Hammerfell"},
    "Hegathe": {"rtt": 220, "region": "Hammerfell"},
    
    # Valenwood cities
    "Falinesti": {"rtt": 340, "region": "Valenwood"},
    "Elden Root": {"rtt": 244, "region": "Valenwood"},
    "Haven": {"rtt": 128, "region": "Valenwood"},
    "Silvenar": {"rtt": 72, "region": "Valenwood"},
    "Arenthia": {"rtt": 321, "region": "Valenwood"},
    "Southpoint": {"rtt": 389, "region": "Valenwood"},
    
    # Cyrodiil cities
    "Anvil": {"rtt": 209, "region": "Cyrodiil"},
    "Bruma": {"rtt": 305, "region": "Cyrodiil"},
    "Bravil": {"rtt": 260, "region": "Cyrodiil"},
    "Chorrol": {"rtt": 189, "region": "Cyrodiil"},
    "Leyawiin": {"rtt": 245, "region": "Cyrodiil"},
    "Cheydinhal": {"rtt": 326, "region": "Cyrodiil"},
    
    # Elsweyr cities
    "Rimmen": {"rtt": 129, "region": "Elsweyr"},
    "Riverhold": {"rtt": 336, "region": "Elsweyr"},
    "Orcrest": {"rtt": 302, "region": "Elsweyr"},
    "Dune": {"rtt": 285, "region": "Elsweyr"},
    "Senchal": {"rtt": 420, "region": "Elsweyr"},
    "Torval": {"rtt": 168, "region": "Elsweyr"}
}

def get_logs(logfile=None):
    """Get logs either from a file or via ADB logcat"""
    if logfile:
        try:
            with open(logfile, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"Error: Log file {logfile} not found")
            return []
    else:
        # Clear logcat first
        subprocess.run(['adb', 'logcat', '-c'], check=False)
        print("Capturing live logs. Press Ctrl+C to stop and analyze...")
        try:
            # Filter logs with tag "AppLog" (used in the messenger app)
            process = subprocess.Popen(['adb', 'logcat', 'AppLog:D', '*:S'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
            logs = []
            try:
                while True:
                    line = process.stdout.readline()
                    if line:
                        logs.append(line)
                        print(".", end="", flush=True)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopped log collection.")
                process.terminate()
                return logs
        except Exception as e:
            print(f"Error capturing logs: {e}")
            return []

def parse_logs(logs):
    """Parse the log lines to extract message information"""
    message_data = []
    
    for line in logs:
        # Extract log info using regex
        match = re.search(r'AppLog\s*:\s*User:(\d+) ; Type:(\w+) ; Message:(.*?) ; MessageID:(\d+) ; Time:(.*?)$', line)
        if match:
            user_id, msg_type, message, msg_id, timestamp = match.groups()
            
            # Parse the timestamp 
            # The timestamp format depends on how the app logs it
            try:
                time_obj = datetime.strptime(timestamp.strip(), "%H:%M:%S.%f")
            except ValueError:
                try:
                    time_obj = datetime.strptime(timestamp.strip(), "%H:%M:%S")
                except ValueError:
                    # If we can't parse the time, use the current date with the time
                    continue
            
            message_data.append({
                'user_id': user_id,
                'msg_type': msg_type,
                'message': message,
                'msg_id': int(msg_id),
                'timestamp': time_obj,
                'raw_log': line
            })
    
    return message_data

def calculate_timing_info(message_data):
    """Calculate time to server and time to receiver for each message"""
    timing_info = []
    messages_by_id = {}
    
    # First, organize messages by ID
    for msg in message_data:
        if msg['msg_id'] not in messages_by_id:
            messages_by_id[msg['msg_id']] = {}
        
        messages_by_id[msg['msg_id']][msg['msg_type']] = msg
    
    # Calculate timing differences
    for msg_id, msg_events in messages_by_id.items():
        if 'new_msg' in msg_events and 'server_ack' in msg_events:
            time_to_server = (msg_events['server_ack']['timestamp'] - 
                              msg_events['new_msg']['timestamp']).total_seconds() * 1000
            
            # Only include time to receiver if we have the receiver_ack event
            time_to_receiver = None
            if 'server_ack' in msg_events and 'receiver_ack' in msg_events:
                time_to_receiver = (msg_events['receiver_ack']['timestamp'] - 
                                   msg_events['server_ack']['timestamp']).total_seconds() * 1000
            
            timing_info.append({
                'msg_id': msg_id,
                'user_id': msg_events['new_msg']['user_id'],
                'message': msg_events['new_msg']['message'],
                'time_to_server': time_to_server,
                'time_to_receiver': time_to_receiver,
                'total_time': time_to_server + (time_to_receiver if time_to_receiver else 0)
            })
    
    return timing_info

def infer_location(timing_info):
    """Infer the location of users based on timing data and known delays"""
    user_timing = defaultdict(lambda: {'server_delays': [], 'receiver_delays': []})
    
    # Collect timing data by user
    for info in timing_info:
        user_id = info['user_id']
        if info['time_to_server'] is not None:
            user_timing[user_id]['server_delays'].append(info['time_to_server'])
        if info['time_to_receiver'] is not None:
            user_timing[user_id]['receiver_delays'].append(info['time_to_receiver'])
    
    # Calculate average delays and determine most likely location
    results = {}
    for user_id, delays in user_timing.items():
        if delays['server_delays']:
            avg_server_delay = sum(delays['server_delays']) / len(delays['server_delays'])
        else:
            avg_server_delay = None
            
        if delays['receiver_delays']:
            avg_receiver_delay = sum(delays['receiver_delays']) / len(delays['receiver_delays'])
        else:
            avg_receiver_delay = None
        
        # Find most likely region based on round trip time (RTT)
        # We divide by 2 to get one-way time from RTT
        likely_region = None
        if avg_server_delay is not None:
            min_diff = float('inf')
            for region, values in REGIONS.items():
                diff = abs((values['rtt']) - avg_server_delay)
                if diff < min_diff:
                    min_diff = diff
                    likely_region = region
        
        # Find most likely city based on RTT to their regional server
        likely_city = None
        if likely_region is not None and avg_receiver_delay is not None:
            min_diff = float('inf')
            
            # Only look at cities in the likely region
            region_cities = {city: data for city, data in CITIES.items() 
                            if data['region'] == likely_region}
            
            for city, values in region_cities.items():
                diff = abs((values['rtt']) - avg_receiver_delay)
                if diff < min_diff:
                    min_diff = diff
                    likely_city = city
                    
        results[user_id] = {
            'avg_server_delay': avg_server_delay,
            'avg_receiver_delay': avg_receiver_delay,
            'likely_region': likely_region,
            'likely_city': likely_city,
            'sample_count_server': len(delays['server_delays']),
            'sample_count_receiver': len(delays['receiver_delays'])
        }
    
    return results

def main():
    """Main function to run the analysis"""
    print("Messenger Timing Attack Analysis Tool")
    print("-------------------------------------")
    
    # Get logs
    if args.logfile:
        print(f"Reading logs from file: {args.logfile}")
        logs = get_logs(logfile=args.logfile)
    else:
        print("Capturing logs from device...")
        logs = get_logs()
    
    if not logs:
        print("No logs found. Exiting.")
        return
    
    print(f"Analyzing {len(logs)} log entries...")
    
    # Parse logs
    message_data = parse_logs(logs)
    print(f"Found {len(message_data)} message-related events")
    
    # Calculate timing information
    timing_info = calculate_timing_info(message_data)
    print(f"Calculated timing for {len(timing_info)} messages")
    
    # Filter by user if specified
    if args.user != 'all':
        timing_info = [info for info in timing_info if info['user_id'] == args.user]
        print(f"Filtered to {len(timing_info)} messages for user {args.user}")
    
    # Infer location
    inferred_locations = infer_location(timing_info)
    
    # Print results
    print("\nInferred User Locations:")
    print("------------------------")
    for user_id, data in inferred_locations.items():
        print(f"User ID: {user_id}")
        print(f"  Average delay to server: {data['avg_server_delay']:.2f}ms (samples: {data['sample_count_server']})")
        
        if data['likely_region']:
            print(f"  Likely region: {data['likely_region']} (RTT: {REGIONS[data['likely_region']]['rtt']}ms)")
        
        if data['avg_receiver_delay'] is not None:
            print(f"  Average delay to receiver: {data['avg_receiver_delay']:.2f}ms (samples: {data['sample_count_receiver']})")
            
            if data['likely_city']:
                print(f"  Likely city: {data['likely_city']} in {data['likely_region']} (RTT to regional server: {CITIES[data['likely_city']]['rtt']}ms)")
        else:
            print("  No receiver timing data available")
        print()

if __name__ == "__main__":
    main()