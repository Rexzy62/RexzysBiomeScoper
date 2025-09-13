import os
import glob
import time
import json
import requests
import configparser
from datetime import datetime
import keyboard

stop_script_flag = False

def set_stop_script_flag():
    global stop_script_flag
    stop_script_flag = True
    print("\nF2 pressed. Script will terminate shortly...")

def read_config_from_ini(ini_path):
    config = configparser.ConfigParser()
    settings = {
        'PrivateServerLinkEnable': False,
        'EnableOnThisBiome': [],
        'PingOnThisBiome': [],
        'StatusEnabled': False,
        'EmojiEnabled': False,
        'DiscordUserId': None,
        'WebhookLink': None,
        'PSLink': None
    }

    try:
        if not os.path.exists(ini_path):
            print(f"DEBUG: Config file NOT found at {ini_path}")
            return settings
        
        print(f"DEBUG: Attempting to read config file from: {ini_path}")
        config.read(ini_path)
        
        print(f"DEBUG: Sections found in config.ini: {config.sections()}")

        if 'Main' in config:
            print(f"DEBUG: Section '[Main]' found.")
            main_config = config['Main']

            settings['WebhookLink'] = main_config.get('WebhookLink')
            if settings['WebhookLink']:
                print(f"DEBUG: Successfully read WebhookLink (first 10 chars): {settings['WebhookLink'][:10]}...")
            else:
                print(f"ERROR: Key 'WebhookLink' not found in section '[Main]'. Webhook will not be sent.")

            settings['PSLink'] = main_config.get('PSLink')
            if settings['PSLink']:
                print(f"DEBUG: Successfully read PSLink (first 10 chars): {settings['PSLink'][:10]}...")
            else:
                print(f"ERROR: Key 'PSLink' not found in section '[Main]'. PSLink will not be added to embed.")
            
            settings['PrivateServerLinkEnable'] = main_config.getboolean('PrivateServerLinkEnable', False)
            print(f"DEBUG: PrivateServerLinkEnable: {settings['PrivateServerLinkEnable']}")
            
            enable_biomes_str = main_config.get('EnableOnThisBiome', '')
            settings['EnableOnThisBiome'] = [b.strip().upper() for b in enable_biomes_str.split(',') if b.strip()]
            print(f"DEBUG: EnableOnThisBiome: {settings['EnableOnThisBiome']}")

            ping_biomes_str = main_config.get('PingOnThisBiome', '')
            settings['PingOnThisBiome'] = [b.strip().upper() for b in ping_biomes_str.split(',') if b.strip()]
            print(f"DEBUG: PingOnThisBiome: {settings['PingOnThisBiome']}")

            settings['StatusEnabled'] = main_config.getboolean('StatusEnabled', False)
            print(f"DEBUG: StatusEnabled: {settings['StatusEnabled']}")

            settings['EmojiEnabled'] = main_config.getboolean('EmojiEnabled', False)
            print(f"DEBUG: EmojiEnabled: {settings['EmojiEnabled']}")

            settings['DiscordUserId'] = main_config.get('DiscordUserId')
            if settings['DiscordUserId']:
                print(f"DEBUG: DiscordUserId: {settings['DiscordUserId']}")

        else:
            print(f"ERROR: Section '[Main]' not found in {ini_path}. Default settings will be used.")

        return settings
        
    except (KeyError, configparser.Error) as e:
        print(f"ERROR: An error occurred while reading config.ini: {e}")
        return settings
    except Exception as e:
        print(f"ERROR: An unexpected exception occurred in read_config_from_ini: {e}")
        return settings

def get_newest_log_file(log_dir):
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    if not log_files:
        return None
    newest_file = max(log_files, key=os.path.getmtime)
    return newest_file

def send_webhook_message(webhook_url, game_name, biome, state, config_settings):
    
    embed_title = "New Biome Detected"
    
    if config_settings['EmojiEnabled']:
        embed_title = f"✨ {embed_title} ✨"

    description_lines = []
    if biome and biome != 'Unknown Biome':
        description_lines.append(f"**Biome:** {biome}")
    
    if config_settings['StatusEnabled'] and state and state != 'Unknown State':
        # Remove "Equipped_" or "_Equipped" and "None" if present
        cleaned_state = state.replace('Equipped_', '').replace('_Equipped', '').replace('None', '').strip()
        if cleaned_state:
            description_lines.append(f"**Current Aura Equipped:** {cleaned_state.replace('_', ' ')}")
        else:
            description_lines.append(f"**Current Aura Equipped:** None") # Explicitly show "None" if no aura
        
    description_content = "\n".join(description_lines) if description_lines else "Details are unavailable."

    if config_settings['PrivateServerLinkEnable'] and config_settings['PSLink']:
        description_content += f"\n\n**Join Server:** [Click Here]({config_settings['PSLink']})" 

    embed = {
        "title": embed_title,
        "description": description_content,
        "color": 0x3498db,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": f"Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }

    payload = {
        "embeds": [embed]
    }
    
    if biome.upper() in config_settings['PingOnThisBiome'] and config_settings['DiscordUserId']:
        payload["content"] = f"<@{config_settings['DiscordUserId']}>"

    try:
        resp = requests.post(webhook_url, json=payload)
        resp.raise_for_status()
        print(f"Sent Discord embed for game: {game_name}, biome: {biome}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send webhook: {e}")

def tail_log_file(path, config_settings, keyword="[BloxstrapRPC]", detection_delay=2):
    global stop_script_flag
    print(f"Tailing log file: {path}")
    last_known_size = os.path.getsize(path)
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while not stop_script_flag:
            if not os.path.exists(path):
                print(f"Log file {path} disappeared.")
                return False
            
            current_size = os.path.getsize(path)
            if current_size < last_known_size:
                print(f"Log file {path} was truncated or replaced. Switching to new file if available.")
                return False
            last_known_size = current_size

            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            if keyword in line:
                try:
                    json_start = line.index(keyword) + len(keyword)
                    json_str = line[json_start:].strip()
                    data = json.loads(json_str)
                    
                    game_name = data.get('data', {}).get('smallImage', {}).get('hoverText', 'Unknown Game')
                    biome = data.get('data', {}).get('largeImage', {}).get('hoverText', 'NORMAL')
                    state = data.get('data', {}).get('state', 'Unknown State')

                    print(f"Found presence data: Game: {game_name}, Biome: {biome}, State: {state}")
                    
                    if config_settings['EnableOnThisBiome'] and biome.upper() not in config_settings['EnableOnThisBiome']:
                        print(f"Biome '{biome}' not in 'EnableOnThisBiome' list. Not sending webhook.")
                        continue

                    if config_settings['WebhookLink']:
                        send_webhook_message(config_settings['WebhookLink'], game_name, biome, state, config_settings)
                        time.sleep(detection_delay)
                    else:
                        print("WebhookLink is not configured, skipping Discord notification.")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Failed to parse JSON from log line: {e}")
                    print("Raw line:", line.strip())
                except Exception as e:
                    print(f"An unexpected error occurred during webhook processing: {e}")
    
    return True

def main():
    global stop_script_flag

    keyboard.add_hotkey('f2', set_stop_script_flag)
    print("Press F2 at any time to stop the script.")

    roblox_log_dir = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\logs")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(script_dir, "config.ini")

    config_settings = read_config_from_ini(ini_path)
    
    if not config_settings['WebhookLink']:
        print("Exiting because a valid Webhook URL could not be read from config.ini.")
        return 

    current_log_file = None
    print("Starting Roblox log monitor...")

    while not stop_script_flag:
        try:
            newest_log = get_newest_log_file(roblox_log_dir)

            if newest_log and newest_log != current_log_file:
                if current_log_file:
                    print(f"Switching from {current_log_file} to new log file: {newest_log}")
                else:
                    print(f"Found initial log file: {newest_log}")
                current_log_file = newest_log
                
                if not tail_log_file(current_log_file, config_settings): 
                    current_log_file = None 
                    print("Re-evaluating log files...")
            elif not newest_log:
                print("No Roblox log files found. Waiting...", end="\r")
                time.sleep(5)
            else:
                if current_log_file:
                    if not tail_log_file(current_log_file, config_settings): 
                        current_log_file = None
                        print("Current log file truncated. Re-evaluating log files...")
                else:
                    print("Waiting for initial log file...", end="\r")
                    time.sleep(1)
        
        except Exception as e:
            print(f"An unhandled error occurred in the main loop: {e}")
            time.sleep(5)
    
    print("Script stopped by user (F2). Goodbye!")

if __name__ == "__main__":
    main()
