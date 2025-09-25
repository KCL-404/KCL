import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from rich.console import Console
from rich.panel import Panel
from threading import Lock
from rich.align import Align
from rich.text import Text

console = Console()
TOKEN_FILE = "tokens.txt"
DELAY = 0.10  # fixed tiny delay between submission rounds
MAX_WORKER_MULT = 8  # multiplier to produce reasonable max_workers

# -------------------------
# Utility: clear screen
# -------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# -------------------------
# Approval system
# -------------------------
def approval():
    try:
        uid = os.geteuid()
    except AttributeError:
        uid = os.getlogin() if hasattr(os, "getlogin") else "user"

    uuid = str(uid) + "DS" + str(uid)
    user_key = "WADE-SHARE-TOOL-" + "".join(uuid)

    clear()
    print(f"\033[1;37m[{chr(27)}[36m•] \033[0;32mYou Need Approval To Use This Tool\033[1;37m")
    print(f"\033[1;37m[{chr(27)}[36m•] \033[0;32mYour Key :\033[0;31m {user_key}")
    time.sleep(0.1)
    print("\033[0;37m──────────────────────────────────────────────────────────")

    try:
        httpCaht = requests.get("https://github.com/KCL-404/KCL/blob/main/key.txt", timeout=6).text
        if user_key in httpCaht:
            print("\033[0;32m >> Your Key Has Been Approved !!!")
            time.sleep(1)
        else:
            print("\033[0;32m >> Send Key on Facebook")
            time.sleep(0.1)
            input(" >> Click Enter To Send Your Key ")
            tks = "Hello%20Sir%20!%20Please%20Approve%20My%20Token%20The%20Token%20Is%20:" + user_key
            os.system("xdg-open https://www.facebook.com/61573982738672" + tks)
            approval()
            time.sleep(1)
            exit()
    except Exception:
        print(" >> Unable To Fetch Data From Server ")
        time.sleep(2)
        exit()

# -------------------------
# Logo/menu (MEL4W perfectly centered)
# -------------------------
def logo_menu():
    clear()

    ascii_text = """\
╔═╗╔═╦═══╦╗─╔╗─╔╦╗╔╗╔╗
║║╚╝║║╔══╣║─║║─║║║║║║║
║╔╗╔╗║╚══╣║─║╚═╝║║║║║║
║║║║║║╔══╣║─╠╦═╗║╚╝╚╝║
║║║║║║╚══╣╚═╝║─║╠╗╔╗╔╝
╚╝╚╝╚╩═══╩═══╝─╚╝╚╝╚╝
"""

    # Create a Text renderable so we can style the ascii art
    text_banner = Text(ascii_text, style="bold red")

    # Align the ASCII both horizontally and vertically (keep as renderable, do NOT convert to string)
    ascii_centered = Align.center(text_banner, vertical="middle")

    # Pass the Align object directly to Panel (no f-strings). Panel will render the object correctly.
    banner = Panel(
        ascii_centered,
        border_style="green",
        expand=True,
        padding=(1, 2),
        title="[cyan]Facebook Spam Share Tool[/cyan]"
    )
    console.clear()
    console.print(banner)

    # Footer section (centered)
    console.print("♦ [cyan]Facebook Spam Share Tool[/cyan] ♦", justify="center")
    console.print("\n[red][ AUTHOR / OWNER ][/red]", justify="center")
    console.print("[green]Admin : ISMAEL[/green]", justify="center")    

# -------------------------
# Token management
# -------------------------
def read_tokens_file():
    if not os.path.exists(TOKEN_FILE):
        return []
    with open(TOKEN_FILE, "r") as fh:
        tokens = [ln.strip() for ln in fh if ln.strip()]
    return tokens

def write_tokens_file(tokens):
    with open(TOKEN_FILE, "w") as fh:
        fh.write("\n".join(tokens))

def prompt_add_tokens(existing_tokens):
    tokens = list(existing_tokens)
    if existing_tokens:
        console.print(f"[cyan]Loaded {len(existing_tokens)} token(s) from {TOKEN_FILE}[/cyan]")
    else:
        console.print("[yellow]No tokens found in tokens.txt.[/yellow]")

    choice = input("\nDo you want to add another token? (y/n): ").lower()
    if choice == "y":
        while True:
            new_token = input("Enter a new Facebook token (leave blank to finish): ").strip()
            if not new_token:
                break
            tokens.append(new_token)
            with open(TOKEN_FILE, "a") as fa:
                if os.path.getsize(TOKEN_FILE) > 0:
                    fa.write("\n")
                fa.write(new_token)
            console.print(f"[green]Token added and saved to {TOKEN_FILE}[/green]")
    return tokens

def validate_token_quick(token):
    try:
        r = requests.get("https://graph.facebook.com/me", params={"access_token": token}, timeout=6)
        return r.status_code == 200
    except requests.RequestException:
        return False

def validate_and_prune_tokens(tokens):
    alive = []
    dead = []
    console.print("[blue]Validating tokens...[/blue]")
    for idx, t in enumerate(tokens, start=1):
        ok = validate_token_quick(t)
        if ok:
            alive.append(t)
        else:
            dead.append((idx, t))
            console.print(f"[red]Token #{idx} invalid or suspended — removed[/red]")
    if dead:
        write_tokens_file(alive)
    return alive, dead

# -------------------------
# Worker
# -------------------------
def share_post(token, link):
    url = "https://graph.facebook.com/me/feed"
    try:
        resp = requests.post(
            url,
            params={"access_token": token},
            data={"link": link, "published": "false"},
            timeout=6
        )
    except requests.RequestException:
        return ("failed", token)

    if resp.status_code in (200, 201):
        return ("ok", token)
    if resp.status_code in (400, 401, 403):
        return ("dead", token)
    return ("failed", token)

# -------------------------
# Fast share loop with corrected batching
# -------------------------
def fast_share_target(link, target_shares):
    tokens = read_tokens_file()
    tokens = prompt_add_tokens(tokens)
    if not tokens:
        console.print("[red]No tokens available. Add tokens to tokens.txt first.[/red]")
        return

    tokens, removed = validate_and_prune_tokens(tokens)
    if not tokens:
        console.print("[red]No valid tokens after validation. Exiting.[/red]")
        return
    console.print(f"[green]Using {len(tokens)} valid token(s).[/green]")

    max_workers = max(8, len(tokens) * MAX_WORKER_MULT)
    start_time = time.time()
    successful = 0
    lock = Lock()
    active_tokens = list(tokens)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        round_index = 0

        while successful < target_shares and active_tokens:
            round_index += 1
            remaining = target_shares - successful

            # Only queue as many tasks as needed
            for token in list(active_tokens)[:remaining]:
                futures.append(executor.submit(share_post, token, link))

            time.sleep(DELAY)

            done, not_done = wait(futures, timeout=0, return_when=FIRST_COMPLETED)
            processed = []
            for fut in done:
                try:
                    status, token = fut.result()
                except Exception:
                    status, token = ("failed", None)

                if status == "ok":
                    with lock:
                        successful += 1
                    console.print(f"[green]✔ Share successful ({successful}/{target_shares})[/green]")
                elif status == "dead" and token:
                    console.print(f"[red]✘ Dead token removed[/red]")
                    with lock:
                        active_tokens = [t for t in active_tokens if t != token]
                        current_tokens = read_tokens_file()
                        current_tokens = [t for t in current_tokens if t != token]
                        write_tokens_file(current_tokens)
                    console.print(f"[yellow]Remaining tokens: {len(active_tokens)}[/yellow]")
                else:
                    console.print("[yellow]✘ Share attempt failed[/yellow]")

                processed.append(fut)

                if successful >= target_shares or not active_tokens:
                    break            

            futures = [f for f in futures if f not in processed]

    elapsed = round(time.time() - start_time, 2)
    console.print(Panel.fit(
        f"[bold white]🏁 COMPLETED[/bold white]\n\n"
        f"[cyan]Target Shares: [bold]{target_shares}[/bold][/cyan]\n"
        f"[cyan]Successful Shares: {successful}[/cyan]\n"
        f"[cyan]Remaining Tokens: {len(read_tokens_file())}[/cyan]\n"
        f"[cyan]Elapsed: {elapsed}s[/cyan]",
        title="RESULT", style="magenta"
    ))

# -------------------------
# Interactive bot entry
# -------------------------
def bot_share():
    clear()
    logo_menu()
    link = input("Enter the post link: ").strip()
    try:
        target = int(input("Enter number of shares to achieve: ").strip())
    except ValueError:
        console.print("[red]Invalid number entered.[/red]")
        return
    fast_share_target(link, target)

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    approval()
    while True:
        bot_share()
        again = input("\nDo you want to share another link? (y/n): ").lower()
        if again != "y":
            break