import requests
import json, os
import time
import random
import signal
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Color codes
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
GREEN = "\033[92m"

PAYLOAD_SERVER_URL = "https://ggtog.live/api/generate-payload"
should_exit = False
run_config = {
    'min_clover': 200,
    'max_clover': 200
}

def print_header():
    # ASCII art untuk "Myeong Tools"
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
    
    # Warna ANSI
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    # Animasi sederhana
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
                    print(f"[{username}]{CYAN} : Game started. ID: {GREEN}{game_id}{RESET}")
                    return game_id, assets
            else:
                print(f"[{username}] : {YELLOW}Failed to start game. Status: {response.status_code}{RESET}")
        except Exception as e:
            print(f"[{username}] : {RED}Start game error: {e}{RESET}")
        if attempt < retries - 1:
            time.sleep(delay)
    return None, None

def generate_payload(game_id, clover_amount):
    global should_exit
    payload_data = {
        "gameId": game_id,
        "cloverAmount": clover_amount
    }
    try:
        response = requests.post(PAYLOAD_SERVER_URL, json=payload_data)
        if response.status_code == 200:
            response_json = response.json()
            if 'hash' in response_json:
                return response_json['hash']
            else:
                print(f"{YELLOW}Response does not contain 'hash'{RESET}")
                return None
        else:
            print(f"{YELLOW}Failed to generate payload. Status: {response.status_code}{RESET}")
            return None
    except Exception as e:
        print(f"{RED}Payload generation error: {e}{RESET}")
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
            print(f"{BLUE}Sending payload to game server...{RESET}")
            
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
        time.sleep(0.1)  # Check for interrupts frequently, but don't update display as often
    print(f"[{username}] : {CYAN}Countdown finished!            {RESET}")

def get_clover_amount():
    print("\nClover Amount Settings")
    print(f"Note: The points entered will be selected randomly, default points 200, maximum is 280 (several account got 324)\n{RESET}")
    try:
        min_amount = int(input(f"{GREEN}Enter minimum points   : {RESET}"))
        max_amount = int(input(f"{GREEN}Enter maximum points   : {RESET}"))
        if min_amount > max_amount:
            min_amount, max_amount = max_amount, min_amount  # Swap jika min lebih besar dari max
        return min_amount, max_amount
    except ValueError:
        print(f"{RED}Input must be a number! Using default (200){RESET}")
        return 200, 200

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
    
def process_query(query):
    global should_exit
    if should_exit:
        return None

    auth_response = auth(query)
    if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
        return f"{RED}Failed to authenticate for query: {query}{RESET}"

    username = auth_response['token']['user']['username']
    bearer = auth_response['token']['access']

    account_profit = 0
    account_games_played = 0

    while not should_exit:
        current_balance = get_balance(bearer)
        if not current_balance:
            return f"{RED}Failed to get current balance for {username}{RESET}"

        play_passes = int(current_balance.get('playPasses', 0))
        available_balance = current_balance.get('availableBalance', '0')
        if play_passes <= 0:
            return f"{YELLOW}No more Ticket available for {username}. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"

        print(f"[{username}] : {CYAN}Available Balance: {available_balance}{RESET}")
        print(f"[{username}] : {CYAN}Remaining Ticket: {play_passes}{RESET}")

        game_id, assets = play_game(bearer, username)
        if not game_id:
            return f"{RED}Failed to start the game for {username}. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"
        
        simple_countdown(30, username)  # Wait for game to finish
        if should_exit:
            break

        clover_amount = str(random.randint(
            run_config['min_clover'], 
            run_config['max_clover']
        ))
        print(f"[{username}] : {CYAN}Using clover amount: {clover_amount}{RESET}")

        payload = generate_payload(game_id, clover_amount)
        if not payload:
            print(f"[{username}] : {YELLOW}Failed to generate payload. Skipping this game...{RESET}")
            continue

        success = claim_game(bearer, payload)
        if success:
            print(f"[{username}] : {GREEN}Game claimed successfully{RESET}")
        else:
            print(f"{YELLOW}[{username}] Failed to claim game after multiple attempts. Skipping...{RESET}")
            continue

        final_balance = get_balance(bearer)
        if final_balance:
            game_profit = calculate_profit(current_balance, final_balance)
            account_profit += game_profit
            account_games_played += 1
            print(f"[{username}] : {GREEN}Profit from this game: {game_profit}{RESET}")
            print(f"[{username}] : {GREEN}Account profit so far: {account_profit}{RESET}")
            print(f"[{username}] : {GREEN}Account games played: {account_games_played}{RESET}")
        else:
            print(f"[{username}] : {RED}Failed to get final balance.{RESET}")

        print(f"[{username}] : {CYAN}Waiting 3 seconds before next game...{RESET}")
        simple_countdown(3, username)  # Wait before next game
        if should_exit:
            break

    return f"{CYAN}Account {username} finished. Total profit: {account_profit}, Games played: {account_games_played}{RESET}"

def show_menu():
    print(f"\n{CYAN}Menu Options:{RESET}")
    print(f"1. Play Game{RESET}")
    print(f"2. Check Account Info{RESET}")
    print(f"3. Check Daily Reward{RESET}")
    print(f"4. Exit{RESET}")
    return input(f"\n{GREEN}Choose option (1-4): {RESET}")

def check_account_info(query):
    auth_response = auth(query)
    if not auth_response or 'token' not in auth_response or 'access' not in auth_response['token']:
        return f"{RED}Failed to authenticate for query: {query}{RESET}"

    username = auth_response['token']['user']['username']
    # Mengambil user ID dengan benar dari struktur response
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
                # Input clover amount sebelum thread
                min_points, max_points = get_clover_amount()
                run_config['min_clover'] = min_points
                run_config['max_clover'] = max_points
                print(f"{GREEN}Range points to be used : {RESET}{min_points} - {max_points}")
                
                try:
                    num_threads = int(input(f"\nEnter the number of threads to use: {RESET}"))
                    print(f"\n{BLUE}Starting game process with {num_threads} threads\n{RESET}")
                except ValueError:
                    print(f"{RED}Thread input must be a number! Using defaults (1){RESET}")
                    num_threads = 1
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    future_to_query = {executor.submit(process_query, query): query for query in queries}
                    try:
                        while future_to_query:
                            if should_exit:
                                break
                            done, _ = concurrent.futures.wait(
                                future_to_query, timeout=0.1,
                                return_when=concurrent.futures.FIRST_COMPLETED
                            )
                            for future in done:
                                query = future_to_query[future]
                                try:
                                    result = future.result(timeout=60)
                                    if result:
                                        print(result)
                                except TimeoutError:
                                    print(f"{RED}Timeout: {query}{RESET}")
                                except Exception as e:
                                    print(f"{RED}Error processing {query}: {str(e)}{RESET}")
                                del future_to_query[future]
                            if should_exit:
                                break
                    except KeyboardInterrupt:
                        should_exit = True
                    finally:
                        for future in future_to_query:
                            future.cancel()
                        executor.shutdown(wait=False)
            
            elif choice == '2':
                try:
                    print(f"\n{CYAN}Checking account information...{RESET}")
                    for query in queries:
                        check_account_info(query)
                except KeyboardInterrupt:
                    signal_handler(signal.SIGINT, None)
            
            elif choice == '3':
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
            
            elif choice == '4':
                print(f"\n{YELLOW}Exiting program...{RESET}")
                break
            
            else:
                print(f"\n{RED}Invalid option! Please choose 1-3{RESET}")

    except Exception as e:
        print(f"{RED}An unexpected error occurred: {e}{RESET}")

if __name__ == "__main__":
    main()