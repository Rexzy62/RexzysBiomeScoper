import os
import glob
import time
import json
import requests
import configparser
from datetime import datetime
import keyboard

# Global variable to signal script termination
stop_script_flag = False

def set_stop_script_flag():
    """Sets the global flag to stop the script."""
    global stop_script_flag
    stop_script_flag = True
    print("\nF2 pressed. Script will terminate shortly...")

def read_webhook_url_from_ini(ini_path):
    """Reads the webhook URL and PSLink from a config.ini file with enhanced debugging."""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(ini_path):
            print(f"DEBUG: Config file NOT found at {ini_path}")
            return None, None
        
        print(f"DEBUG: Attempting to read config file from: {ini_path}")
        config.read(ini_path)
        
        print(f"DEBUG: Sections found in config.ini: {config.sections()}")

        webhook_link = None
        ps_link = None

        # Check for 'Main' section as per new config.ini
        if 'Main' in config:
            print(f"DEBUG: Section '[Main]' found.")
            print(f"DEBUG: Keys under [Main]: {config['Main'].keys()}")
            
            # Attempt to read WebhookLink
            if 'WebhookLink' in config['Main']:
                webhook_link = config['Main']['WebhookLink']
                print(f"DEBUG: Successfully read WebhookLink (first 10 chars): {webhook_link[:10]}...")
            else:
                print(f"ERROR: Key 'WebhookLink' not found in section '[Main]'. Webhook will not be sent.")

            # Attempt to read PSLink
            if 'PSLink' in config['Main']:
                ps_link = config['Main']['PSLink']
                print(f"DEBUG: Successfully read PSLink (first 10 chars): {ps_link[:10]}...")
            else:
                print(f"ERROR: Key 'PSLink' not found in section '[Main]'. PSLink will not be added to embed.")
        else:
            print(f"ERROR: Section '[Main]' not found in {ini_path}. Neither Webhook nor PSLink will be available.")

        return webhook_link, ps_link
        
    except (KeyError, configparser.Error) as e:
        print(f"ERROR: An error occurred while reading config.ini: {e}")
        return None, None
    except Exception as e:
        print(f"ERROR: An unexpected exception occurred in read_webhook_url_from_ini: {e}")
        return None, None

def get_newest_log_file(log_dir):
    """Finds and returns the path to the newest log file in a directory."""
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    if not log_files:
        return None
    newest_file = max(log_files, key=os.path.getmtime)
    return newest_file

def send_webhook_message(webhook_url, biome, ps_link=None):
    """Sends a formatted message to a Discord webhook with an embed, including PSLink if available."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    description_content = f"**Biome:** {biome}"
    if ps_link:
        # Markdown for linking text: [Link Text](URL)
        description_content += f"\n**Join Server:** [Click Here]({ps_link})" 

    embed = {
        "title": "New Biome Detected!",
        "description": description_content,
        "color": 0x3498db, # A nice blue color (decimal representation of hex #3498db)
        "timestamp": datetime.utcnow().isoformat() + "Z", # Discord requires ISO 8601 with 'Z' for UTC
        "footer": {
            "text": f"Detected at: {timestamp}"
        }
    }

    payload = {
        "embeds": [embed]
    }
    
    try:
        resp = requests.post(webhook_url, json=payload)
        resp.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"Sent Discord embed for biome: {biome}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send webhook: {e}")

def tail_log_file(path, webhook_url, ps_link, keyword="[BloxstrapRPC]"):
    """
    Tails a log file and sends a webhook message when the keyword is found.
    This function continuously reads new lines from the file.
    It returns True if it should continue tailing, False if the file was replaced/truncated.
    """
    global stop_script_flag
    print(f"Tailing log file: {path}")
    last_known_size = os.path.getsize(path)
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2) # Go to the end of the file initially
        while not stop_script_flag: # Check stop flag in the loop
            # Check if the file has been replaced (size decreased) or deleted
            if not os.path.exists(path):
                print(f"Log file {path} disappeared.")
                return False # Signal to main loop to find newest file
            
            current_size = os.path.getsize(path)
            if current_size < last_known_size:
                print(f"Log file {path} was truncated or replaced. Switching to new file if available.")
                return False # Signal to main loop to find newest file
            last_known_size = current_size

            line = f.readline()
            if not line:
                time.sleep(0.1) # Wait a bit before trying to read again
                continue
            
            if keyword in line:
                try:
                    json_start = line.index(keyword) + len(keyword)
                    json_str = line[json_start:].strip()
                    data = json.loads(json_str)
                    
                    # Safely get biome information, defaulting to 'Unknown Biome'
                    biome = data.get('data', {}).get('largeImage', {}).get('hoverText', 'Unknown Biome')
                    print(f"Found presence data: {data}")
                    send_webhook_message(webhook_url, biome, ps_link) # Pass ps_link to send_webhook_message
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Failed to parse JSON from log line: {e}")
                    print("Raw line:", line.strip())
                except Exception as e:
                    print(f"An unexpected error occurred during webhook processing: {e}")
    
    return True # Loop exited due to stop_script_flag

def main():
    """Main function to orchestrate log tailing and webhook sending."""
    global stop_script_flag

    # Register the F2 hotkey to stop the script
    keyboard.add_hotkey('f2', set_stop_script_flag)
    print("Press F2 at any time to stop the script.")

    roblox_log_dir = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\logs")
    
    # --- CORRECTED PATH TO config.ini FOR THE NEW PROJECT STRUCTURE ---
    # Since config.ini is in the same directory as main.pyw,
    # we just need to get the script's directory and join "config.ini"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(script_dir, "config.ini")
    # --- END OF CORRECTED PATH ---

    webhook_url, ps_link = read_webhook_url_from_ini(ini_path)
    
    # Only exit if no webhook_url is found. ps_link is optional for the embed.
    if not webhook_url:
        print("Exiting because a valid Webhook URL could not be read.")
        return 

    current_log_file = None
    print("Starting Roblox log monitor...")

    while not stop_script_flag: # Check stop flag in the main loop
        try:
            newest_log = get_newest_log_file(roblox_log_dir)

            if newest_log and newest_log != current_log_file:
                if current_log_file:
                    print(f"Switching from {current_log_file} to new log file: {newest_log}")
                else:
                    print(f"Found initial log file: {newest_log}")
                current_log_file = newest_log
                
                # If tail_log_file returns False, it means the file was truncated/replaced,
                # so we set current_log_file to None to force re-detection of the newest log.
                if not tail_log_file(current_log_file, webhook_url, ps_link): 
                    current_log_file = None 
                    print("Re-evaluating log files...")
            elif not newest_log:
                print("No Roblox log files found. Waiting...", end="\r")
                time.sleep(5) # Wait longer if no logs are present at all
            else:
                # If we are already tailing a file (current_log_file is not None)
                # and it's still the newest (newest_log == current_log_file),
                # we continue to tail it.
                if current_log_file:
                    if not tail_log_file(current_log_file, webhook_url, ps_link): 
                        current_log_file = None # File was truncated, force re-detection
                        print("Current log file truncated. Re-evaluating log files...")
                else:
                    # This case means newest_log is None AND current_log_file is None,
                    # so we are still waiting for *any* log file to appear.
                    print("Waiting for initial log file...", end="\r")
                    time.sleep(1)
        
        except Exception as e:
            print(f"An unhandled error occurred in the main loop: {e}")
            time.sleep(5) # Wait before retrying to prevent a tight error loop
    
    print("Script stopped by user (F2). Goodbye!")

if __name__ == "__main__":
    main()