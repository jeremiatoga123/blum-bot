import requests
import json, os
import time
import random
import signal
import threading
import concurrent.futures
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
GREEN = "\033[92m"

PAYLOAD_SERVER_URL = "https://blum-toga-c3d9617e40ff.herokuapp.com/api/game"
should_exit = False
run_config = {
    'min_clover': 200,
    'max_clover': 200
}

def print_header():
    header = """
    ███╗   ███╗██╗   ██╗███████╗ ██████╗ ███╗   ██╗ ██████╗ 
    ████╗ ████║╚██╗ ██╔╝██╔════╝██╔═══██╗████╗  ██║██╔════╝ 
    ██╔████╔██║ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║  ███╗
    ██║╚██╔╝██║  ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║   ██║
    ██║ ╚═╝ ██║   ██║   ███████╗╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝     ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
                        ████████╗ ██████╗  ██████╗ ██╗     ███████╗
                        ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
                           ██║   ██║   ██║██║   ██║██║     ███████╗
                           ██║   ██║   ██║██║   ██║██║     ╚════██║
                           ██║   ╚██████╔╝╚██████╔╝███████╗███████║
                           ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
    """
    
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    print(BLUE + header + RESET)
    print(GREEN + "=" * 70 + RESET)
    print(YELLOW + "\t\t\tSupport & Donations" + RESET)
    print(CYAN + """
    ╔════════════════════════════════════════════════════════╗
    ║  DANA    : 082286000280                                ║
    ║  SeaBank : 901058100087                                ║
    ║  GoPay   : 089524227639                                ║
    ║  ETH     : 0xFF4a4601d87b966ce1e437ae95D19116E49ee99e  ║
    ╚════════════════════════════════════════════════════════╝
    """ + RESET)
    print(GREEN + "=" * 70 + RESET)
    print(GREEN + "\t\tWelcome to Blum Bot Myeong Tools " + RESET)
    print(BLUE + "\t\t\tCreated by Toga" + RESET)
    print(GREEN + "=" * 70 + RESET)

def signal_handler(signum, frame):
    global should_exit
    print(f"\n{RED}Received interrupt signal. Stopping...{RESET}")
    should_exit = True
    os._exit(0)

def read_queries(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

        

farming_summary = {
    'total_points': 0,
    'total_tickets': 0,
    'total_profit': 0,
    'active_accounts': [],
    'start_time': time.time(),
    'duration': 0
}

load_dotenv()
bot_token = os.getenv('TELEGRAM_BOT_TOKEN', None)
chat_id = os.getenv('TELEGRAM_CHAT_ID', None)

def send_telegram_message(bot_token, chat_id, message):
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"{CYAN}{'='*52}{RESET}")
            print(f"{GREEN}Notification sent to Telegram{RESET}")
            print(f"{CYAN}{'='*52}{RESET}")
    except requests.RequestException as e:
        print(f"{YELLOW}Telegram notification disabled or failed{RESET}")

def send_farming_summary(bot_token, chat_id, farming_data):
    """Send farming summary to Telegram if credentials are available"""
    if not bot_token or not chat_id:
        print(f"{YELLOW}Telegram notifications disabled. No bot_token or chat_id provided.{RESET}")
        return

    total_points = farming_data['total_points']
    total_tickets = farming_data['total_tickets']
    total_profit = farming_data['total_profit']
    active_accounts = len(farming_data['active_accounts'])
    duration = farming_data['duration']
    
    total_dogs = sum(acc.get('total_dogs', 0) for acc in farming_data['active_accounts'])
    
    message = (
        "🤖 <b>BLUM BOT FARMING SUMMARY</b>\n"
        "═══════════════════════\n\n"
        f"⏱️ Duration: <code>{duration:.2f} hours</code>\n\n"
        f"📊 <b>FARMING STATS</b>\n"
        f"🎯 Total Points: <code>{total_points:,}</code>\n"
        f"🦴 Total Dogs: <code>{total_dogs:.1f}</code>\n"  
        f"🎟️ Tickets Used: <code>{total_tickets}</code>\n"
        f"💰 Total Profit: <code>{total_profit:,.2f}</code>\n\n"
        f"👥 <b>ACCOUNTS INFO</b>\n"
        f"📱 Active Accounts: <code>{active_accounts}</code>"
    )
    
    send_telegram_message(bot_token, chat_id, message)

def update_farming_stats(username, points, tickets, profit, dogs=0):  
    """Update farming statistics"""
    user_exists = False
    for acc in farming_summary['active_accounts']:
        if acc['username'] == username:
            user_exists = True
            acc['last_points'] = float(points) 
            if 'total_dogs' not in acc:
                acc['total_dogs'] = 0
            acc['total_dogs'] += dogs
            break

    if not user_exists:
        farming_summary['active_accounts'].append({
            'username': username,
            'last_points': float(points),
            'total_dogs': dogs
        })

    farming_summary['total_points'] = sum(float(acc['last_points']) for acc in farming_summary['active_accounts'])
    farming_summary['total_tickets'] += tickets
    farming_summary['total_profit'] += profit
    farming_summary['duration'] = (time.time() - farming_summary['start_time']) / 3600

def auth(query, retries=3, delay=2):
    global should_exit
    url = "https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "referer": "https://telegram.blum.codes/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    body = {
        "query": query
    }
    
    for attempt in range(retries):
        if should_exit:
            return None
        try:
            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"{RED}Authentication error: {e}{RESET}")
        
        if attempt < retries - 1:
            time.sleep(delay)
    
    return None

def refresh_token(refresh_token):
    url = "https://user-domain.blum.codes/api/v1/auth/refresh"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "referer": "https://telegram.blum.codes/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    data = { 'refresh': refresh_token }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        else:
            print(f"{RED}Refresh failed!{RESET}")
            print(f"Response: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"{RED}Error during refresh: {e}{RESET}")
        return None

def get_headers(access_token=None):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "referer": "https://telegram.blum.codes/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers

def get_balance(access_token, retries=3, delay=2):
    global should_exit
    url = "https://game-domain.blum.codes/api/v1/user/balance"
    headers = get_headers(access_token)
    
    for attempt in range(retries):
        if should_exit:
            return None
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"{YELLOW}Balance check failed. Status: {response.status_code}{RESET}")
        except Exception as e:
            print(f"{RED}Balance check error: {e}{RESET}")
        if attempt < retries - 1:
            time.sleep(delay)
    return None

def play_game(access_token, username, retries=3, delay=2):
    global should_exit
    url = "https://game-domain.blum.codes/api/v2/game/play"
    headers = get_headers(access_token)
    
    for attempt in range(retries):
        if should_exit:
            return None, None
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                game_id = response_json.get("gameId")
                assets = response_json.get("assets")
                if game_id and assets:
                    print(f"[{username}] : {CYAN}Game started. ID : {GREEN}{game_id}{RESET}")
                    return game_id, assets
            else:
                print(f"[{username}] : {YELLOW}Failed to start game. Status: {response.status_code}{RESET}")
        except Exception as e:
            print(f"[{username}] : {RED}Start game error: {e}{RESET}")
        if attempt < retries - 1:
            time.sleep(delay)
    return None, None

def generate_payload(game_id, clover_amount, dogs_eligible=False, max_retries=3, delay=2):
    global should_exit
    payload_data = {
        "gameId": game_id,
        "points": clover_amount
    }
    
    dogs = None

    if dogs_eligible:
        dogs = str(random.randint(5, 10) * 0.1)
        payload_data["dogs"] = dogs
    
    for attempt in range(max_retries):
        try:
            response = requests.post(PAYLOAD_SERVER_URL, json=payload_data)
            
            if response.status_code == 200:
                response_json = response.json()
                if 'payload' in response_json:
                    return response_json['payload'], dogs
                else:
                    print(f"{YELLOW}Attempt {attempt + 1}: Response does not contain 'payload'{RESET}")
            else:
                print(f"{YELLOW}Attempt {attempt + 1}: Failed to generate payload. Status: {response.status_code}{RESET}")
            
            if attempt < max_retries - 1:
                print(f"{YELLOW}Waiting {delay} seconds before retry...{RESET}")
                time.sleep(delay)
            else:
                print(f"{RED}Failed to generate payload after {max_retries} attempts. Stopping game...{RESET}")
                return None
                
        except Exception as e:
            print(f"{RED}Attempt {attempt + 1}: Payload generation error: {e}{RESET}")
            if attempt < max_retries - 1:
                print(f"{YELLOW}Waiting {delay} seconds before retry...{RESET}")
                time.sleep(delay)
            else:
                print(f"{RED}Failed to generate payload after {max_retries} attempts. Stopping game...{RESET}")
                return None
    
    return None
        
def claim_game(access_token, payload, max_retries=5, initial_delay=2):
    global should_exit
    game_url = "https://game-domain.blum.codes/api/v2/game/claim"
    headers = get_headers(access_token)
    game_data = {"payload": payload}
    
    for attempt in range(max_retries):
        if should_exit:
            return False
        try:
            game_response = requests.post(game_url, headers=headers, json=game_data)
            if game_response.status_code == 200:
                return True
            elif game_response.status_code == 400 and "game session not finished" in game_response.text.lower():
                print(f"{YELLOW}Game session not finished. Waiting before retry...{RESET}")
                time.sleep(initial_delay * (2 ** attempt))  
            else:
                print(f"{YELLOW}Unexpected response. Status: {game_response.status_code}, Content: {game_response.text}{RESET}")
                return False
        except Exception as e:
            print(f"{RED}Claim game error: {e}{RESET}")
        
        if attempt < max_retries - 1:
            print(f"{YELLOW}Retrying attempt {attempt + 2}...{RESET}")
            time.sleep(initial_delay * (2 ** attempt))  
    
    print(f"{RED}Max retries reached. Failed to claim game.{RESET}")
    return False

def calculate_profit(initial_balance, final_balance):
    initial_available = float(initial_balance.get('availableBalance', '0'))
    final_available = float(final_balance.get('availableBalance', '0'))
    
    profit = final_available - initial_available
    return round(profit, 2)

def simple_countdown(seconds, username):
    global should_exit
    start_time = time.time()
    while time.time() - start_time < seconds:
        if should_exit:
            return
        remaining = int(seconds - (time.time() - start_time))
        print(f"[{username}] : {CYAN}{remaining} seconds remaining...{RESET}", end='\r')
        time.sleep(0.1)  
    print(f"[{username}] : {CYAN}Countdown finished!            {RESET}")

def get_clover_amount():
    print("\nClover Amount Settings")
    print(f"Note: The points entered will be selected randomly, default points 200, maximum is 280 (some account got 324)\n{RESET}")
    try:
        min_amount = int(input(f"{GREEN}Enter minimum points   : {RESET}"))
        max_amount = int(input(f"{GREEN}Enter maximum points   : {RESET}"))
        if min_amount > max_amount:
            min_amount, max_amount = max_amount, min_amount 
        return min_amount, max_amount
    except ValueError:
        print(f"{RED}Input must be a number! Using default (200){RESET}")
        return 200, 200


def check_dogs_drop_eligibility(access_token, retries=3, delay=2):
    url = "https://game-domain.blum.codes/api/v2/game/eligibility/dogs_drop"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "authorization": f"Bearer {access_token}",
        "referer": "https://telegram.blum.codes/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            pass
        
        if attempt < retries - 1:
            time.sleep(delay)
    
    return None

def daily_reward(access_token, retries=3, delay=2):
    url = f"https://game-domain.blum.codes/api/v1/daily-reward?offset=-420"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "authorization": f"Bearer {access_token}",
        "referer": "https://telegram.blum.codes/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, timeout=10)
            if response.status_code == 400:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    if response.text == "OK":
                        return {"message": "OK"}
                    return None
            else:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"message": response.text}
        except (requests.RequestException, ValueError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return {"message": "Failed to check"}
    
    return None
    
def play_process(query):
    global should_exit
    if should_exit:
        return None

    auth_response = auth(query)
    if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
        return f"{RED}Failed to authenticate for query: {query}{RESET}"

    username = auth_response['token']['user']['username']
    refresh_token_str = auth_response['token']['refresh']
    bearer = auth_response['token']['access']

    def refresh_auth():
        nonlocal bearer, refresh_token_str
        try:
            refresh_response = refresh_token(refresh_token_str)
            if refresh_response and 'token' in refresh_response:
                bearer = refresh_response['token']['access']
                refresh_token_str = refresh_response['token']['refresh']
                print(f"[{username}] : {GREEN}Successfully refreshed token{RESET}")
                return True
            
            print(f"[{username}] : {YELLOW}Refresh token failed, trying full re-authentication...{RESET}")
            new_auth_response = auth(query)
            if new_auth_response and 'token' in new_auth_response:
                bearer = new_auth_response['token']['access']
                refresh_token_str = new_auth_response['token']['refresh']
                return True
            return False
        except Exception as e:
            print(f"[{username}] : {RED}Failed to refresh authentication: {e}{RESET}")
            return False

    account_profit = 0
    account_games_played = 0
    account_points = 0 

    dogs_eligible = False
    try:
        eligibility_response = check_dogs_drop_eligibility(bearer)
        if eligibility_response:  
            dogs_eligible = eligibility_response.get('eligible', False) 
            print(f"[{username}] : {CYAN}Dogs eligibility: {GREEN if dogs_eligible else RED}{dogs_eligible}{RESET}")
    except Exception as e:
        print(f"[{username}] : {RED}Failed to check dogs eligibility: {e}{RESET}")

    initial_balance = get_balance(bearer)
    if not initial_balance:
        return f"{RED}Failed to get current balance for {username}{RESET}"

    elif 'availableBalance' in initial_balance:
        update_farming_stats(
            username=username,
            points=float(initial_balance.get('availableBalance', '0')),
            tickets=0,
            profit=0,
            dogs=0
        )
        print(f"[{username}] : {CYAN}Balance : {initial_balance['availableBalance']}{RESET}")
        print(f"[{username}] : {CYAN}Available Ticket : {initial_balance.get('playPasses', 0)}{RESET}")

    if int(initial_balance.get('playPasses', 0)) <= 0:
        print(f"[{username}] : {YELLOW}No More Ticket available{RESET}")

    while not should_exit:
        try:
            current_balance = get_balance(bearer)
            if not current_balance:
                print(f"[{username}] : {YELLOW}Token might be expired, trying to refresh...{RESET}")
                if not refresh_auth():
                    return f"{RED}Failed to refresh authentication. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"
                current_balance = get_balance(bearer)
                if not current_balance:
                    return f"{RED}Failed to get balance even after token refresh{RESET}"

            play_passes = int(current_balance.get('playPasses', 0))
            available_balance = float(current_balance.get('availableBalance', '0'))
            if play_passes <= 0:   
                return f"{YELLOW}No more Ticket available for {username}. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"

            print(f"[{username}] : {CYAN}Available Balance : {available_balance}{RESET}")
            print(f"[{username}] : {CYAN}Remaining Ticket : {play_passes}{RESET}")

            game_id, assets = play_game(bearer, username)
            if not game_id:
                if not refresh_auth():
                    return f"{RED}Failed to refresh authentication{RESET}"
                game_id, assets = play_game(bearer, username)
                if not game_id:
                    return f"{RED}Failed to start game even after token refresh{RESET}"
            
            simple_countdown(30, username)  
            if should_exit:
                break

            clover_amount = str(random.randint(
                run_config['min_clover'], 
                run_config['max_clover']
            ))

            result = generate_payload(game_id, clover_amount, dogs_eligible)
            if result is None or result[0] is None: 
                print(f"[{username}] : {RED}Payload generation failed. Stopping game process.{RESET}")
                should_exit = True
                break

            payload, dogs = result  
            print(f"[{username}] : {CYAN}Using clover amount : {clover_amount}{RESET}")
            if dogs_eligible:
                print(f"[{username}] : {CYAN}Using dogs amount : {dogs}{RESET}")
            print(f"[{username}] : {CYAN}Claiming game...{RESET}")
                
            success = claim_game(bearer, payload)
            if not success:
                if not refresh_auth():
                    return f"{RED}Failed to refresh authentication{RESET}"
                success = claim_game(bearer, payload)
                if not success:
                    print(f"{YELLOW}Failed to claim game even after token refresh. Skipping...{RESET}")
                    continue
            else:
                print(f"[{username}] : {GREEN}Game claimed successfully!{RESET}")

            final_balance = get_balance(bearer)
            if final_balance:
                game_profit = calculate_profit(current_balance, final_balance)
                account_profit += game_profit
                account_games_played += 1
                current_dogs = float(dogs) if dogs_eligible and dogs is not None else 0
                
                update_farming_stats(
                    username=username,
                    points=float(final_balance.get('availableBalance', '0')),
                    tickets=1,
                    profit=game_profit,
                    dogs=current_dogs
                )
                
                
                print(f"[{username}] : {GREEN}Profit from this game : {game_profit}{RESET}")
                print(f"[{username}] : {GREEN}Account profit so far : {account_profit}{RESET}")
                print(f"[{username}] : {GREEN}Account games played : {account_games_played}{RESET}")
            else:
                print(f"[{username}] : {RED}Failed to get final balance.{RESET}")

            print(f"[{username}] : {CYAN}Waiting 3 seconds before next game...{RESET}")
            simple_countdown(3, username) 
            if should_exit:
                break

        except Exception as e:
            if "unauthorized" in str(e).lower() or "token expired" in str(e).lower():
                print(f"[{username}] : {YELLOW}Token error detected. Trying to refresh...{RESET}")
                if not refresh_auth():
                    return f"{RED}Failed to refresh authentication. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"
                continue
            else:
                print(f"[{username}] : {RED}Error during game process: {e}. Stopping game process.{RESET}")
                should_exit = True
                break

    return f"{CYAN}Account {username} finished. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"

def claim_farming(access_token, retries=3, delay=2):
    url = "https://game-domain.blum.codes/api/v1/farming/claim"
    headers = get_headers(access_token)
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers)
            response_json = response.json()
            return response_json
        except (requests.RequestException, ValueError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None

def start_farming(access_token, retries=3, delay=2):
    url = "https://game-domain.blum.codes/api/v1/farming/start"
    headers = get_headers(access_token)
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers)
            response_json = response.json()
            return response_json
        except (requests.RequestException, ValueError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None

def play_game_and_daily(query):
    auth_response  = auth(query)
    if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
        return f"{RED}Failed to authenticate for query: {query}{RESET}"
    
    username = auth_response['token']['user']['username']
    bearer = auth_response['token']['access']

    print(f"[{username}] : {CYAN}Claiming farming rewards...{RESET}")
    claim_response = claim_farming(bearer)
    if "message" in claim_response and "It's too early to claim":
        print(f"[{username}] : {YELLOW}Already Claimed{RESET}")
    else:
        print(f"[{username}] : {GREEN}Farming Claimed!{RESET}")

    print(f"[{username}] : {CYAN}Starting farming...{RESET}")
    start_response = start_farming(bearer)
    if start_response:
        if "endTime" in start_response:
            current_time_ms = int(time.time() * 1000)
            remaining_ms = start_response["endTime"] - current_time_ms
            
            if remaining_ms > 0:
                hours = remaining_ms // (1000 * 60 * 60)
                minutes = (remaining_ms % (1000 * 60 * 60)) // (1000 * 60)
                seconds = (remaining_ms % (1000 * 60)) // 1000
                print(f"[{username}] : {YELLOW}Farming Already Started, {hours:02d}:{minutes:02d}:{seconds:02d} Remaining Until Claim{RESET}")
            else:
                print(f"[{username}] : {GREEN}Farming Ready to Claim!{RESET}")
        else:
            print(f"[{username}] : {GREEN}Farming started!{RESET}")

    print(f"[{username}] : {CYAN}Checking daily...{RESET}")
    daily_reward_response = daily_reward(bearer)
    if daily_reward_response:
        if "message" in daily_reward_response and "same day" in daily_reward_response["message"].lower():
            print(f"[{username}] : {YELLOW}Daily reward already claimed today{RESET}")
        elif "message" in daily_reward_response and "OK" in daily_reward_response["message"]:
            print(f"[{username}] : {GREEN}Daily reward successfully claimed!{RESET}")
    else:
        print(f"[{username}] : {RED}Failed to claim daily reward{RESET}")

    return play_process(query)

def auto_loop_process(queries):
    global should_exit, farming_summary

    print(f"{CYAN}{'='*52}{RESET}")
    if bot_token and chat_id:
        print(f"{YELLOW}Telegram notifications Enabled{RESET}")
    else:
        print(f"{YELLOW}Telegram notifications Disabled{RESET}")

    min_points, max_points = get_clover_amount()
    run_config['min_clover'] = min_points
    run_config['max_clover'] = max_points
    print(f"{GREEN}Range points to be used : {RESET}{min_points} - {max_points}")
    
    try:
        num_threads = int(input(f"\nEnter the number of threads to use : {RESET}"))
        print(f"\n{BLUE}Starting process with {num_threads} threads\n{RESET}")
    except ValueError:
        print(f"{RED}Thread input must be a number! Using defaults (1){RESET}")
        num_threads = 1

    while not should_exit:
        try:
            farming_summary = {
                'total_points': 0,
                'total_tickets': 0,
                'total_profit': 0,
                'active_accounts': [],
                'start_time': time.time(),
                'duration': 0
            }
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                future_to_query = {executor.submit(play_game_and_daily, query): query for query in queries}
                completed_accounts = 0
                total_accounts = len(queries)
                try:
                    while future_to_query:
                        if should_exit:
                            break
                        done, not_done = concurrent.futures.wait(
                            future_to_query, timeout=0.1,
                            return_when=concurrent.futures.FIRST_COMPLETED
                        )
                        for future in done:
                            query = future_to_query[future]
                            try:
                                result = future.result(timeout=60)
                                completed_accounts += 1
                                if completed_accounts == total_accounts:
                                    send_farming_summary(bot_token, chat_id, farming_summary)
                                if should_exit:  
                                    raise Exception("Payload server is down")
                            except TimeoutError:
                                print(f"{RED}Timeout: {query}{RESET}")
                            except Exception as e:
                                for f in not_done:
                                    f.cancel()
                                executor.shutdown(wait=False)
                                should_exit = False  
                                return  
                                print(f"\n{RED}Error detected. Stopping all processes...{RESET}")
                            del future_to_query[future]
                        if should_exit:
                            break
                except KeyboardInterrupt:
                    should_exit = True
                finally:
                    for future in future_to_query:
                        future.cancel()
                    executor.shutdown(wait=False)
                    
            if not should_exit:
                print(f"\n{CYAN}Play game completed. Waiting 5 hours before next game...{RESET}")
                for remaining in range(180000, 0, -1):
                    if should_exit:
                        break
                    hours = remaining // 3600
                    minutes = (remaining % 3600) // 60
                    seconds = remaining % 60
                    print(f"Next game in: {hours:02d}:{minutes:02d}:{seconds:02d}", end='\r')
                    time.sleep(1)
                print("\n")

        except KeyboardInterrupt:
            should_exit = True
        except Exception as e:
            print(f"{RED}Error in auto loop: {e}{RESET}")
            if not should_exit:
                print(f"{YELLOW}Restarting loop in 5 minutes...{RESET}")
                time.sleep(300)
            else:
                break

    print(f"{YELLOW}Auto loop stopped{RESET}")


def show_menu():
    print(f"\n{CYAN}Menu Options:{RESET}")
    print(f"1. Play Game Every 5 Hours")
    print(f"2. Play Game")
    print(f"3. Check Account Info")
    print(f"4. Check Daily Reward")
    print(f"5. Exit")
    return input(f"\n{GREEN}Choose option (1-5): {RESET}")

def check_account_info(query):
    auth_response = auth(query)
    if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
        return f"{RED}Failed to authenticate for query: {query}{RESET}"

    username = auth_response['token']['user']['username']
    user_id = auth_response['token']['user'].get('id', {})
    full_id = user_id['id'] if isinstance(user_id, dict) and 'id' in user_id else 'N/A'
    
    bearer = auth_response['token']['access']

    current_balance = get_balance(bearer)
    if not current_balance:
        return f"{RED}Failed to get current balance for {username}{RESET}"

    play_passes = int(current_balance.get('playPasses', 0))
    available_balance = current_balance.get('availableBalance', '0')
    
    print(f"\n{CYAN}{'='*52}{RESET}")
    print(f"Account Information")
    print(f"{CYAN}{'='*52}{RESET}")
    print(f"Username     : {GREEN}{username}{RESET}")
    print(f"User ID      : {GREEN}{full_id}{RESET}")
    print(f"Blum Balance : {GREEN}{available_balance}{RESET}")
    print(f"Ticket       : {GREEN}{play_passes}{RESET}")
    print(f"{CYAN}{'='*52}{RESET}")
    

def main():
    print_header()
    global should_exit

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        queries = read_queries('query.txt')
        if not queries:
            print(f"{RED}No queries found in query.txt. Exiting...{RESET}")
            return

        while True:
            choice = show_menu()
            if choice == '1':
                try:
                    auto_loop_process(queries)
                except KeyboardInterrupt:
                    should_exit = True

            if choice == '2':
                print(f"{CYAN}{'='*52}{RESET}")
                if bot_token and chat_id:
                    print(f"{YELLOW}\nTelegram notifications Enabled{RESET}")
                else:
                    print(f"{YELLOW}\nTelegram notifications Disabled{RESET}")

                global farming_summary
                farming_summary = {
                    'total_points': 0,
                    'total_tickets': 0,
                    'total_profit': 0,
                    'active_accounts': [],
                    'start_time': time.time(),
                    'duration': 0
                }
                min_points, max_points = get_clover_amount()
                run_config['min_clover'] = min_points
                run_config['max_clover'] = max_points
                print(f"{GREEN}Range points to be used : {RESET}{min_points} - {max_points}")
                
                try:
                    num_threads = int(input(f"\nEnter the number of threads to use : {RESET}"))
                    print(f"\n{BLUE}Starting game process with {num_threads} threads\n{RESET}")
                except ValueError:
                    print(f"{RED}Thread input must be a number! Using defaults (1){RESET}")
                    num_threads = 1
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    future_to_query = {executor.submit(play_process, query): query for query in queries}
                    completed_accounts = 0
                    total_accounts = len(queries)
                    try:
                        while future_to_query:
                            if should_exit:
                                break
                            done, not_done = concurrent.futures.wait(
                                future_to_query, timeout=0.1,
                                return_when=concurrent.futures.FIRST_COMPLETED
                            )
                            for future in done:
                                query = future_to_query[future]
                                try:
                                    result = future.result(timeout=60)
                                    completed_accounts += 1
                                    if completed_accounts == total_accounts:
                                        send_farming_summary(bot_token, chat_id, farming_summary)
                                    if should_exit:  
                                        raise Exception("Payload server is down")
                                except TimeoutError:
                                    print(f"{RED}Timeout: {query}{RESET}")
                                except Exception as e:
                                    for f in not_done:
                                        f.cancel()
                                    executor.shutdown(wait=False)
                                    should_exit = False  
                                    return  
                                    print(f"\n{RED}Error detected. Stopping all processes...{RESET}")
                                del future_to_query[future]
                            if should_exit:
                                break
                    except KeyboardInterrupt:
                        should_exit = True
                    finally:
                        for future in future_to_query:
                            future.cancel()
                        executor.shutdown(wait=False)
            
            elif choice == '3':
                try:
                    print(f"\n{CYAN}Checking account information...{RESET}")
                    for query in queries:
                        check_account_info(query)
                except KeyboardInterrupt:
                    signal_handler(signal.SIGINT, None)
            
            elif choice == '4':
                try:
                    print(f"\n{CYAN}{'='*52}{RESET}")
                    print(f"Daily Reward Check")
                    print(f"{CYAN}{'='*52}{RESET}")
                    
                    for query in queries:
                        auth_response = auth(query)
                        if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
                            print(f"{RED}Failed to authenticate for query: {query}{RESET}")
                            continue

                        username = auth_response['token']['user']['username']
                        bearer = auth_response['token']['access']
                        
                        daily_status = daily_reward(bearer)
                        if daily_status:
                            if "message" in daily_status and "same day" in daily_status["message"].lower():
                                print(f"Username: {GREEN}{username}{RESET}")
                                print(f"Status  : {YELLOW}Already claimed today{RESET}")
                            elif "message" in daily_status and "OK" in daily_status["message"]:
                                print(f"Username: {GREEN}{username}{RESET}")
                                print(f"Status  : {GREEN}Successfully claimed!{RESET}")
                            else:
                                print(f"Username: {GREEN}{username}{RESET}")
                                print(f"Status  : {RED}Unknown status{RESET}")
                        else:
                            print(f"Username: {GREEN}{username}{RESET}")
                            print(f"Status  : {RED}Failed to check{RESET}")
                        print(f"{CYAN}{'='*52}{RESET}")
                except KeyboardInterrupt:
                    signal_handler(signal.SIGINT, None)
                except Exception as e:
                    print(f"{RED}An error occurred while checking daily rewards: {str(e)}{RESET}")
            
            elif choice == '5':
                print(f"\n{YELLOW}Exiting program...{RESET}")
                break
            
            else:
                print(f"\n{RED}Invalid option! Please choose 1-5{RESET}")

    except Exception as e:
        print(f"{RED}An unexpected error occurred: {e}{RESET}")

if __name__ == "__main__":
    main()