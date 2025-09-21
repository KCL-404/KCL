import requests, os, re, sys, json, time, threading
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

ses = requests.Session()
log_file = "spamshare_log.txt"
cookie_file = "cookies.txt"

success_count = 0
fail_count = 0
BOX_WIDTH = 52

# Lock for clean printing
print_lock = threading.Lock()

# ================= Approval =================
def check_approval():
    try:
        uid = str(os.geteuid()) + os.getlogin()
    except:
        uid = str(os.getpid()) + os.name
    local_key = "KCL-" + uid
    
    # Clear screen for clean UI
    os.system("clear")
    
    # Banner style
    print("\033[1;32m" + "═" * 50)
    print("      🔑 KCL APPROVAL SYSTEM 🔑")
    print("═" * 50 + "\033[0m")
    print(f"\033[1;36m[KEY GENERATED]\033[0m : \033[1;33m{local_key}\033[0m\n")
    
    try:
        url = "https://github.com/KCL-404/KCL/blob/main/key.txt"
        keys = requests.get(url).text
        if local_key in keys:
            print("\033[1;32m✅ Key Approved! Welcome to KCL Tool.\033[0m\n")
            time.sleep(2)
            return True
        else:
            print("\033[1;31m❌ Key not approved!\033[0m")
            print("\033[1;37mRequest approval here: \033[1;36mhttps://www.facebook.com/100003380109076\033[0m")
            input("\nPress Enter to exit...")
            sys.exit()
    except:
        print("\033[1;31m[x] Failed to validate key. Avail key to Krausen Chronault.\033[0m")
        sys.exit()

# ================= Helpers =================
def log_result(message):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

def save_cookie(cookie):
    with open(cookie_file, "a") as f:
        f.write(cookie.strip() + "\n")

def get_token(cookie):
    try:
        headers = {"user-agent": "Mozilla/5.0 (Linux; Android 8.1.0)", "accept-language": "en-US"}
        res = ses.get("https://business.facebook.com/business_locations", headers=headers, cookies={"cookie": cookie})
        token = re.search(r"(EAAG\w+)", res.text).group(1)
        return token
    except:
        return None

# ================= UI Helpers =================
def message_box(message, color=Fore.GREEN, icon="✔️"):
    print(Fore.CYAN + "\n╔" + "═" * BOX_WIDTH + "╗")
    line = f" {icon} {message} "
    padding = BOX_WIDTH - len(line)
    print(Fore.CYAN + "║" + color + line + " " * padding + Fore.CYAN + "║")
    print(Fore.CYAN + "╚" + "═" * BOX_WIDTH + "╝")

# ================= Cookie Management =================
def clear_all_cookies():
    try:
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            message_box("All cookies have been cleared.", Fore.GREEN, "✔️")
        else:
            message_box("No cookie file found.", Fore.RED, "❌")
    except Exception as e:
        message_box(f"Error clearing cookies: {str(e)}", Fore.RED, "❌")

def clean_cookies():
    try:
        if not os.path.exists(cookie_file):
            message_box("No cookie file found.", Fore.RED, "❌")
            return

        valid_cookies = []
        with open(cookie_file, "r") as f:
            cookies = [c.strip() for c in f if c.strip()]

        for cookie in cookies:
            token = get_token(cookie)
            if token:
                valid_cookies.append(cookie)

        with open(cookie_file, "w") as f:
            for vc in valid_cookies:
                f.write(vc + "\n")

        removed = len(cookies) - len(valid_cookies)
        message_box(f"Cleanup done. Removed {removed} dead cookies.", Fore.GREEN, "✔️")
    except Exception as e:
        message_box(f"Error cleaning cookies: {str(e)}", Fore.RED, "❌")


# ================= Add Cookies =================
def add_cookies():
    try:
        while True:
            cookie = input("Enter cookie (or type 'done' to finish): ").strip()
            if cookie.lower() == "done":
                break
            if cookie:
                save_cookie(cookie)
                message_box("Cookie added successfully.", Fore.GREEN, "✔️")
            else:
                message_box("No cookie entered.", Fore.RED, "❌")
    except Exception as e:
        message_box(f"Error adding cookie: {str(e)}", Fore.RED, "❌")

# ================= Share Function =================
def share_worker(api, payload, headers, cookies, post_url):
    global success_count, fail_count
    try:
        res = ses.post(api, data=payload, headers=headers, cookies=cookies)
        res_json = res.json()
        with print_lock:
            if 'id' in res_json:
                success_count += 1
                print(Fore.GREEN + f"Sent Successful Share! Total: {success_count+fail_count}")
                log_result(f"SUCCESS: {post_url}")
            else:
                fail_count += 1
                print(Fore.RED + f"Sent Failed Share! Total: {success_count+fail_count}")
                log_result(f"FAIL: {res_json}")
    except:
        with print_lock:
            fail_count += 1
            print(Fore.RED + f"Sent Failed Share! Total: {success_count+fail_count}")

def spam_share():
    global success_count, fail_count
    success_count = 0
    fail_count = 0
    start_time = time.time()

    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "╔" + "═" * BOX_WIDTH + "╗")
    print(Fore.CYAN + "║" + Fore.YELLOW + " 🚀 FACEBOOK SPAM SHARE TOOL ".center(BOX_WIDTH) + Fore.CYAN + "║")
    print(Fore.CYAN + "╚" + "═" * BOX_WIDTH + "╝\n")

    # Load cookies
    try:
        with open(cookie_file, "r") as f:
            cookies = [c.strip() for c in f if c.strip()]
    except:
        message_box("No cookies found. Use option [2] to login.", Fore.RED, "❌")
        return

    accounts = []
    for idx, cookie in enumerate(cookies, 1):
        token = get_token(cookie)
        if token:
            user = ses.get(f"https://graph.facebook.com/me?fields=name&access_token={token}", cookies={"cookie": cookie}).json()
            name = user.get("name", "Unknown")
            with print_lock:
                print(Fore.GREEN + f"   [{idx}] ✅ {name}")
            accounts.append((token, cookie))
        else:
            with print_lock:
                print(Fore.RED + f"   [{idx}] ❌ Invalid cookie")

    if not accounts:
        message_box("No valid accounts found", Fore.RED, "❌")
        return

    # Get target links
    print(Fore.CYAN + "\nEnter multiple post URLs (type 'done' to finish):")
    urls = []
    while True:
        link = input(Fore.MAGENTA + "Post URL: ").strip()
        if link.lower() == 'done':
            break
        if link:
            urls.append(link)

    if not urls:
        message_box("No URLs provided", Fore.RED, "❌")
        return

    # Total target
    try:
        target_total = int(input(Fore.YELLOW + "Shares Per Account: " + Fore.WHITE))
    except:
        message_box("Invalid number", Fore.RED, "❌")
        return

    headers = {"user-agent": "Mozilla/5.0 (Linux; Android 10) Chrome/123.0.0.0 Mobile Safari/537.36"}
    total_done = 0
    threads = []

    # Launch shares in parallel using threads
    while total_done < target_total:
        for token, cookie in accounts:
            for post_url in urls:
                if total_done >= target_total:
                    break
                t = threading.Thread(
                    target=share_worker,
                    args=(
                        "https://graph.facebook.com/me/feed",
                        {"link": post_url, "published": "false", "access_token": token},
                        headers,
                        {"cookie": cookie},
                        post_url
                    )
                )
                t.start()
                threads.append(t)
                total_done = success_count + fail_count

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Summary
    elapsed = int(time.time() - start_time)
    with print_lock:
        print(Fore.MAGENTA + "\n╔" + "═" * 30 + "╗")
        print(Fore.MAGENTA + "║" + Fore.RED + " 🎯 COMPLETED".center(30) + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "╠" + "═" * 30 + "╣")
        print(Fore.MAGENTA + "║" + Fore.GREEN + f" Total Shares: {success_count+fail_count}".ljust(30) + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "║" + Fore.GREEN + f" Success: {success_count}".ljust(30) + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "║" + Fore.RED   + f" Failed : {fail_count}".ljust(30) + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "║" + Fore.CYAN  + f" Time: {elapsed}s".ljust(30) + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "╚" + "═" * 30 + "╝")
# ================= Fancy Menu =================
def fancy_menu():
    os.system("clear")
    banner = [
"┏━━━┳━━━┳┓╋╋┏┳━━┳━━━┓",
"┃┏━┓┃┏━┓┃┗┓┏┛┣┫┣┻┓┏┓┃",
"┃┃╋┗┫┃╋┃┣┓┃┃┏┛┃┃╋┃┃┃┃",
"┃┃╋┏┫┃╋┃┃┃┗┛┃╋┃┃╋┃┃┃┃",
"┃┗━┛┃┗━┛┃┗┓┏┛┏┫┣┳┛┗┛┃",
"┗━━━┻━━━┛╋┗┛╋┗━━┻━━━┛",
    ]
    print(Fore.GREEN + "┌" + "─" * BOX_WIDTH + "┐")
    for line in banner:
        print(Fore.GREEN + "│" + Fore.RED + line.center(BOX_WIDTH) + Fore.GREEN + "│")
    print(Fore.GREEN + "└" + "─" * BOX_WIDTH + "┘")

    print("\n" + Fore.CYAN + "♦ Facebook Spam Share Tool ♦\n")
    print(Fore.YELLOW + "[ AUTHOR / OWNER ]")
    print(Fore.WHITE + " Admin   : " + Fore.GREEN + "KRAUSEN CHRONAULT")
    print(Fore.WHITE + " Overview: " + Fore.CYAN + "Stored Accounts\n")

    print(Fore.RED + "═" * BOX_WIDTH)
    print(Fore.WHITE + "                  TOOLS SERVICES")
    print(Fore.RED + "═" * BOX_WIDTH + "\n")

    print(Fore.GREEN + "[01]" + Fore.WHITE + " Start Share        " + Fore.CYAN + "  - [ ACCOUNT ]")
    print(Fore.GREEN + "[02]" + Fore.WHITE + " Add Cookies        " + Fore.CYAN + "  - [ COOKIE LOGIN ]")
    print(Fore.GREEN + "[03]" + Fore.WHITE + " Remove ALL Cookies " + Fore.CYAN + "  - [ RESET ]")
    print(Fore.GREEN + "[04]" + Fore.WHITE + " Remove Dead Cookies" + Fore.CYAN + "  - [ CLEANUP ]")
    print(Fore.GREEN + "[05]" + Fore.WHITE + " Exit               " + Fore.CYAN + "  - [ QUIT PROGRAM ]\n")

    choice = input(Fore.YELLOW + "CHOICE : " + Fore.WHITE)
    return choice

# ================= Main =================
def main():
    while True:
        choice = fancy_menu()
        if choice == "1":
            spam_share()
        elif choice == "2":
            add_cookies()
        elif choice == "3":
            clear_all_cookies()
        elif choice == "4":
            clean_cookies()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("[x] Invalid choice.")
            time.sleep(1)

if __name__ == '__main__':
    if check_approval():
        main()