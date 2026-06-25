#!/usr/bin/env python3
"""
==============================================================
  terminal_app.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Full Terminal Application — Two Menus
  ----------------------------------------
  ADMIN MENU  (6 Admin Tasks):
    1. Add User
    2. Remove User
    3. Mint Reward Tokens
    4. Burn Tokens
    5. Pause / Unpause System
    6. Transfer Ownership

  USER MENU  (5 Normal User Tasks):
    1. Earn Rewards (view catalogue & earn)
    2. Redeem Rewards
    3. Transfer Tokens
    4. View Balance
    5. View Transaction History (event logs)

  All blockchain calls are routed through blockchain.py.
==============================================================
"""

import getpass
import os
import sys

from web3.exceptions import ContractLogicError

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
ADMIN_SECRET = "hnu2025admin"

SEPARATOR = "=" * 60
LINE      = "-" * 60


# ──────────────────────────────────────────────────────────────
#  Utility helpers
# ──────────────────────────────────────────────────────────────

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def header(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def success(msg: str) -> None:
    print(f"\n  [OK]    {msg}")


def error(msg: str) -> None:
    print(f"\n  [ERROR] {msg}")


def info(msg: str) -> None:
    print(f"  {msg}")


def pause_prompt() -> None:
    input("\n  Press ENTER to continue...")


# ──────────────────────────────────────────────────────────────
#  Session State
# ──────────────────────────────────────────────────────────────

class Session:
    def __init__(self, address: str, name: str = ""):
        self.address  = address
        self.name     = name
        self.is_admin = False


# ──────────────────────────────────────────────────────────────
#  Registration
# ──────────────────────────────────────────────────────────────

def check_and_register(w3, sr, session: Session) -> None:
    registered = sr.functions.registeredUsers(session.address).call()
    if registered:
        session.name = sr.functions.getUserName(session.address).call()
        return

    header("Welcome — First-Time Registration")
    info("Your wallet address is not yet registered.")
    name = input("\n  Display Name: ").strip()
    if not name:
        error("Registration cancelled — no name entered.")
        return

    try:
        receipt = bc.send_transaction(w3, sr.functions.registerUser(name), session.address)
        session.name = name
        success(f"Registered as '{name}' in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Registration failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER TASK 1 — Earn Rewards (view catalogue & earn notification)
# ──────────────────────────────────────────────────────────────

def earn_rewards(w3, sr, rpc, session: Session) -> None:
    """User Task 1 — Earn Rewards: show catalogue and record earning event."""
    header("Earn Rewards — View Available Items")
    items  = bc.get_all_reward_items(sr, w3)
    active = [i for i in items if i["active"]]

    if not active:
        info("No reward items are currently available.")
        pause_prompt()
        return

    print(f"\n  {'ID':<5} {'Name':<24} {'Cost (RPC)':<12} {'Stock'}")
    print(f"  {LINE}")
    for item in active:
        print(f"  {item['id']:<5} {item['name']:<24} {item['pointCost']:<12} {item['stock']}")

    rpc_bal = bc.get_rpc_balance(rpc, session.address, w3)
    print(f"\n  Your RPC Balance : {rpc_bal:,.2f} RPC")
    info("Rewards are earned by the Admin minting tokens to your wallet.")
    info("Contact admin to earn more RPC reward points.")

    # Record earn event on-chain (calls earnRewards if caller is admin; otherwise info only)
    try:
        owner_addr = sr.functions.owner().call()
        if session.address.lower() == owner_addr.lower():
            amount_input = input("\n  Award RPC amount to self (0 to skip): ").strip()
            if amount_input and int(amount_input) > 0:
                amount_wei = w3.to_wei(int(amount_input), "ether")
                bc.send_transaction(w3, rpc.functions.mint(session.address, amount_wei), session.address)
                bc.send_transaction(w3, sr.functions.earnRewards(session.address, amount_wei), session.address)
                success(f"Earned {amount_input} RPC — recorded on-chain.")
    except Exception:
        pass

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER TASK 2 — Redeem Rewards
# ──────────────────────────────────────────────────────────────

def redeem_reward(w3, sr, rpc, session: Session) -> None:
    """User Task 2 — Redeem Rewards."""
    header("Redeem a Reward")

    items  = bc.get_all_reward_items(sr, w3)
    active = [i for i in items if i["active"] and i["stock"] > 0]

    if not active:
        error("No items are currently available for redemption.")
        pause_prompt()
        return

    print(f"\n  {'ID':<5} {'Name':<24} {'Cost (RPC)'}")
    print(f"  {LINE}")
    for item in active:
        print(f"  {item['id']:<5} {item['name']:<24} {item['pointCost']}")

    rpc_bal = bc.get_rpc_balance(rpc, session.address, w3)
    print(f"\n  Your RPC Balance : {rpc_bal:,.2f} RPC")

    try:
        choice = int(input("\n  Enter Item ID to redeem (0 to cancel): ").strip())
    except ValueError:
        error("Invalid input.")
        pause_prompt()
        return

    if choice == 0:
        return

    selected = next((i for i in active if i["id"] == choice), None)
    if not selected:
        error("Item not found or unavailable.")
        pause_prompt()
        return

    cost_wei = w3.to_wei(selected["pointCost"], "ether")
    if rpc_bal < selected["pointCost"]:
        error(f"Insufficient RPC. You need {selected['pointCost']} RPC but have {rpc_bal:,.2f}.")
        pause_prompt()
        return

    info(f"Redeeming '{selected['name']}' for {selected['pointCost']} RPC...")

    try:
        admin_addr = sr.functions.getAdmin().call()
        bc.send_transaction(w3, rpc.functions.transfer(admin_addr, cost_wei), session.address)
        receipt = bc.send_transaction(w3, sr.functions.redeemReward(choice), session.address)
        success(f"Redemption recorded in block {receipt['blockNumber']}.")
        info(f"You redeemed: {selected['name']}")
    except ContractLogicError as e:
        error(f"Redemption failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER TASK 3 — Transfer Tokens
# ──────────────────────────────────────────────────────────────

def transfer_tokens(w3, rpc, session: Session) -> None:
    """User Task 3 — Transfer Tokens to another wallet."""
    header("Transfer Reward Point Coins")
    to_addr = input("  Recipient Address : ").strip()

    try:
        to_addr = w3.to_checksum_address(to_addr)
    except Exception:
        error("Invalid Ethereum address.")
        pause_prompt()
        return

    try:
        amount = float(input("  Amount (RPC)      : ").strip())
    except ValueError:
        error("Invalid amount.")
        pause_prompt()
        return

    rpc_bal = bc.get_rpc_balance(rpc, session.address, w3)
    if amount <= 0 or amount > rpc_bal:
        error(f"Invalid amount. Your balance: {rpc_bal:,.2f} RPC.")
        pause_prompt()
        return

    amount_wei = w3.to_wei(amount, "ether")
    try:
        receipt = bc.send_transaction(w3, rpc.functions.transfer(to_addr, amount_wei), session.address)
        success(f"Transferred {amount:,.2f} RPC to {to_addr} in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Transfer failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER TASK 4 — View Balance
# ──────────────────────────────────────────────────────────────

def view_balance(w3, sr, rpc, session: Session) -> None:
    """User Task 4 — View Balance for any wallet."""
    header("View Wallet Balance")
    addr = input("  Enter wallet address (blank = your own): ").strip()

    if not addr:
        addr = session.address

    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid Ethereum address.")
        pause_prompt()
        return

    eth_bal = bc.get_eth_balance(w3, addr)
    rpc_bal = bc.get_rpc_balance(rpc, addr, w3)

    try:
        name = sr.functions.getUserName(addr).call()
    except Exception:
        name = "(not registered)"

    print(f"\n  Address  : {addr}")
    print(f"  Name     : {name}")
    print(f"  {LINE[:40]}")
    print(f"  ETH Balance  :  {eth_bal:.6f} ETH")
    print(f"  RPC Balance  :  {rpc_bal:,.2f} RPC")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER TASK 5 — View Transaction History (event logs)
# ──────────────────────────────────────────────────────────────

def view_transaction_history(w3, sr, rpc) -> None:
    """User Task 5 — View Transaction History via on-chain event logs."""
    header("Transaction History — Event Logs")
    addr = input("  Enter wallet address: ").strip()

    if not addr:
        info("No address entered.")
        pause_prompt()
        return

    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid Ethereum address.")
        pause_prompt()
        return

    info("Scanning blockchain for events... (this may take a moment)")
    events = bc.get_address_activity(w3, sr, rpc, addr)

    if not events:
        info("No activity found for this address.")
    else:
        print(f"\n  {'Block':<8} {'Action':<30} {'Transaction Hash':<20}")
        print(f"  {LINE}")
        for ev in events:
            tx_short = ev["tx"][:18] + "..."
            print(f"  {ev['block']:<8} {ev['action']:<30} {tx_short}")
        print(f"\n  Total Events : {len(events)}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  View Personal Activity History — full blockchain event scan
# ──────────────────────────────────────────────────────────────

def view_personal_activity_history(w3, sr, rpc) -> None:
    """Scan ALL blocks on-chain and display a full activity table for a wallet."""
    header("View Personal Activity History — Full Blockchain Scan")
    addr = input("  Enter wallet address: ").strip()

    if not addr:
        info("No address entered.")
        pause_prompt()
        return

    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid Ethereum address.")
        pause_prompt()
        return

    info("Scanning all blocks on-chain... (this may take a moment)")

    rows = []

    # ── StoreRewards events ────────────────────────────────────
    sr_event_map = {
        "UserRegistered":   ("User Registered",   "user",  None),
        "RewardEarned":     ("Reward Earned",      "user",  "amount"),
        "RewardRedeemed":   ("Reward Redeemed",    "user",  "pointsSpent"),
        "UserAdded":        ("User Added",         "user",  None),
        "UserRemoved":      ("User Removed",       "user",  None),
        "ContractPaused":   ("System Paused",      "by",    None),
        "ContractResumed":  ("System Resumed",     "by",    None),
        "OwnershipTransferred": ("Ownership Transferred", "oldOwner", None),
        "BatchItemsAdded":  ("Batch Items Added",  "by",    "count"),
    }
    for ev_name, (label, actor_key, value_key) in sr_event_map.items():
        try:
            logs = getattr(sr.events, ev_name).get_logs(from_block=0)
            for log in logs:
                args   = dict(log["args"])
                actor  = args.get(actor_key, "")
                if not actor or actor.lower() != addr.lower():
                    continue
                raw_val = args.get(value_key, 0) if value_key else 0
                if value_key == "amount" or value_key == "pointsSpent":
                    display_val = f"{w3.from_wei(int(raw_val), 'ether'):,.2f} RPC"
                elif value_key == "count":
                    display_val = f"{raw_val} items"
                else:
                    display_val = "—"
                rows.append({
                    "block":  log["blockNumber"],
                    "action": label,
                    "value":  display_val,
                    "tx":     log["transactionHash"].hex(),
                })
        except Exception:
            pass

    # ── RewardPointCoin events ─────────────────────────────────
    rpc_event_map = {
        "Transfer": ("Token Transfer", "from", "to", "value"),
        "Minted":   ("Mint",           None,   "to", "amount"),
        "Burned":   ("Burn",           "from", None, "amount"),
    }
    for ev_name, (label, from_key, to_key, val_key) in rpc_event_map.items():
        try:
            logs = getattr(rpc.events, ev_name).get_logs(from_block=0)
            for log in logs:
                args   = dict(log["args"])
                from_  = args.get(from_key, "") if from_key else ""
                to_    = args.get(to_key,   "") if to_key   else ""
                involved = (from_ and from_.lower() == addr.lower()) or \
                           (to_   and to_.lower()   == addr.lower())
                if not involved:
                    continue
                raw_val = args.get(val_key, 0)
                display_val = f"{w3.from_wei(int(raw_val), 'ether'):,.2f} RPC"
                if from_ and from_.lower() == addr.lower() and to_:
                    direction = f"Token Transfer OUT"
                elif to_ and to_.lower() == addr.lower() and from_:
                    direction = f"Token Transfer IN"
                else:
                    direction = label
                rows.append({
                    "block":  log["blockNumber"],
                    "action": direction,
                    "value":  display_val,
                    "tx":     log["transactionHash"].hex(),
                })
        except Exception:
            pass

    rows.sort(key=lambda x: x["block"])

    if not rows:
        info("No on-chain activity found for this address.")
    else:
        print(f"\n  {'Block':<8} {'Action Type':<26} {'Value':<20} {'Tx Hash'}")
        print(f"  {LINE}")
        for r in rows:
            tx_short = r["tx"][:18] + "..."
            print(f"  {r['block']:<8} {r['action']:<26} {r['value']:<20} {tx_short}")
        print(f"\n  Total Events : {len(rows)}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  Check Address Balances — ETH + RPC
# ──────────────────────────────────────────────────────────────

def check_address_balances(w3, sr, rpc) -> None:
    """Enter any address and display ETH balance + RewardPointCoin balance."""
    header("Check Address Balances")
    addr = input("  Enter wallet address: ").strip()

    if not addr:
        info("No address entered.")
        pause_prompt()
        return

    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid Ethereum address.")
        pause_prompt()
        return

    # ETH balance via web3.eth.get_balance
    eth_wei = w3.eth.get_balance(addr)
    eth_bal = w3.from_wei(eth_wei, "ether")

    # RPC (RewardPointCoin) balance
    rpc_bal = bc.get_rpc_balance(rpc, addr, w3)

    try:
        name = sr.functions.getUserName(addr).call()
    except Exception:
        name = "(not registered)"

    print(f"\n  Address              : {addr}")
    print(f"  Registered Name      : {name}")
    print(f"  {LINE[:50]}")
    print(f"  ETH Balance          : {float(eth_bal):,.6f} ETH")
    print(f"  RewardPointCoin (RPC): {rpc_bal:,.2f} RPC")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 1 — Add User
# ──────────────────────────────────────────────────────────────

def admin_add_user(w3, sr, session: Session) -> None:
    """Admin Task 1 — Add User (on-chain role grant)."""
    header("Admin — Add User")
    addr = input("  User Address to add: ").strip()
    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid address.")
        pause_prompt()
        return

    try:
        receipt = bc.send_transaction(w3, sr.functions.addUser(addr), session.address)
        success(f"User {addr} added in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 2 — Remove User
# ──────────────────────────────────────────────────────────────

def admin_remove_user(w3, sr, session: Session) -> None:
    """Admin Task 2 — Remove User (on-chain role revoke)."""
    header("Admin — Remove User")
    addr = input("  User Address to remove: ").strip()
    try:
        addr = w3.to_checksum_address(addr)
    except Exception:
        error("Invalid address.")
        pause_prompt()
        return

    try:
        receipt = bc.send_transaction(w3, sr.functions.removeUser(addr), session.address)
        success(f"User {addr} removed in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 3 — Mint Reward Tokens
# ──────────────────────────────────────────────────────────────

def admin_mint_coins(w3, sr, rpc, session: Session) -> None:
    """Admin Task 3 — Mint Reward Tokens."""
    header("Admin — Mint Reward Point Coins")
    to_addr = input("  Recipient Address : ").strip()
    try:
        amount  = float(input("  Amount (RPC)      : ").strip())
        to_addr = w3.to_checksum_address(to_addr)
    except Exception:
        error("Invalid input.")
        pause_prompt()
        return

    amount_wei = w3.to_wei(amount, "ether")
    try:
        receipt = bc.send_transaction(w3, rpc.functions.mint(to_addr, amount_wei), session.address)
        success(f"Minted {amount:,.2f} RPC to {to_addr} in block {receipt['blockNumber']}.")
        # Record earn event if recipient is registered
        try:
            if sr.functions.registeredUsers(to_addr).call():
                bc.send_transaction(w3, sr.functions.earnRewards(to_addr, amount_wei), session.address)
        except Exception:
            pass
    except ContractLogicError as e:
        error(f"Mint failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 4 — Burn Tokens
# ──────────────────────────────────────────────────────────────

def admin_burn_coins(w3, rpc, session: Session) -> None:
    """Admin Task 4 — Burn Tokens from any address."""
    header("Admin — Burn Reward Point Coins")
    from_addr = input("  Burn from Address : ").strip()
    try:
        amount    = float(input("  Amount (RPC)      : ").strip())
        from_addr = w3.to_checksum_address(from_addr)
    except Exception:
        error("Invalid input.")
        pause_prompt()
        return

    bal = bc.get_rpc_balance(rpc, from_addr, w3)
    if amount > bal:
        error(f"Insufficient balance. Address has {bal:,.2f} RPC.")
        pause_prompt()
        return

    amount_wei = w3.to_wei(amount, "ether")
    try:
        receipt = bc.send_transaction(w3, rpc.functions.burn(from_addr, amount_wei), session.address)
        success(f"Burned {amount:,.2f} RPC from {from_addr} in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Burn failed: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 5 — Pause / Unpause System
# ──────────────────────────────────────────────────────────────

def admin_pause_resume(w3, sr, session: Session) -> None:
    """Admin Task 5 — Pause / Unpause System."""
    paused = sr.functions.paused().call()
    header(f"Admin — {'Unpause' if paused else 'Pause'} System")
    info(f"Current status : {'PAUSED' if paused else 'ACTIVE'}")

    confirm = input(f"  {'Unpause' if paused else 'Pause'} the system? (yes/no): ").strip().lower()
    if confirm != "yes":
        info("Cancelled.")
        pause_prompt()
        return

    try:
        fn = sr.functions.unpauseSystem() if paused else sr.functions.pauseSystem()
        receipt = bc.send_transaction(w3, fn, session.address)
        new_status = "ACTIVE" if paused else "PAUSED"
        success(f"System is now {new_status}. Block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Transaction reverted: {e}")

    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN TASK 6 — Transfer Ownership
# ──────────────────────────────────────────────────────────────

def admin_transfer_ownership(w3, sr, rpc, session: Session) -> None:
    """Admin Task 6 — Transfer Ownership (on-chain)."""
    header("Admin — Transfer Ownership")
    info("WARNING: This permanently hands owner rights to another address.")
    new_owner = input("  New Owner Address : ").strip()

    try:
        new_owner = w3.to_checksum_address(new_owner)
    except Exception:
        error("Invalid address.")
        pause_prompt()
        return

    confirm = input("  Type CONFIRM to proceed: ").strip()
    if confirm != "CONFIRM":
        info("Cancelled.")
        pause_prompt()
        return

    try:
        receipt = bc.send_transaction(w3, sr.functions.transferOwnership(new_owner), session.address)
        success(f"StoreRewards ownership transferred in block {receipt['blockNumber']}.")
        bc.send_transaction(w3, rpc.functions.transferAdminship(new_owner), session.address)
        success(f"RewardPointCoin adminship transferred.")
        info(f"New Owner: {new_owner}")
        # Demote current session — this account is no longer owner or admin
        session.is_admin = False
        info("You have been demoted to a regular user. Returning to main menu.")
    except ContractLogicError as e:
        error(f"Transfer failed: {e}")

    pause_prompt()
    # Return sentinel so the caller knows to exit the admin menu
    return "ownership_transferred"


# ──────────────────────────────────────────────────────────────
#  Extra Admin Helpers
# ──────────────────────────────────────────────────────────────

def admin_add_item(w3, sr, session: Session) -> None:
    header("Admin — Add Reward Item")
    name = input("  Item Name   : ").strip()
    try:
        cost  = int(input("  Point Cost  : ").strip())
        stock = int(input("  Stock       : ").strip())
    except ValueError:
        error("Invalid numeric input.")
        pause_prompt()
        return
    try:
        receipt = bc.send_transaction(w3, sr.functions.addRewardItem(name, cost, stock), session.address)
        success(f"Item '{name}' added in block {receipt['blockNumber']}.")
    except ContractLogicError as e:
        error(f"Transaction reverted: {e}")
    pause_prompt()


def show_catalogue(sr, w3) -> None:
    header("Reward Items Catalogue")
    items  = bc.get_all_reward_items(sr, w3)
    active = [i for i in items if i["active"]]
    if not active:
        info("No reward items are currently available.")
    else:
        print(f"\n  {'ID':<5} {'Name':<24} {'Cost (RPC)':<12} {'Stock'}")
        print(f"  {LINE}")
        for item in active:
            print(f"  {item['id']:<5} {item['name']:<24} {item['pointCost']:<12} {item['stock']}")
    pause_prompt()


# ──────────────────────────────────────────────────────────────
#  ADMIN MENU  (6 Admin Tasks)
# ──────────────────────────────────────────────────────────────

def admin_menu(w3, sr, rpc, session: Session) -> None:
    """Admin Menu — 6 Admin Tasks enforced on-chain."""
    while True:
        clear()
        header(f"ADMIN PANEL  |  {session.address[:14]}...")
        print()
        print(f"  ── Admin Tasks (on-chain role enforced) ──")
        print(f"  [1]  Add User                (Task 1)")
        print(f"  [2]  Remove User             (Task 2)")
        print(f"  [3]  Mint Reward Tokens      (Task 3)")
        print(f"  [4]  Burn Tokens             (Task 4)")
        print(f"  [5]  Pause / Unpause System  (Task 5)")
        print(f"  [6]  Transfer Ownership      (Task 6)")
        print()
        print(f"  ── Extras ──")
        print(f"  [7]  Add Reward Item")
        print(f"  [8]  View All Items (Catalogue)")
        print(f"  [0]  Return to User Menu")
        print()

        choice = input("  Selection: ").strip()

        if choice == "1":
            admin_add_user(w3, sr, session)
        elif choice == "2":
            admin_remove_user(w3, sr, session)
        elif choice == "3":
            admin_mint_coins(w3, sr, rpc, session)
        elif choice == "4":
            admin_burn_coins(w3, rpc, session)
        elif choice == "5":
            admin_pause_resume(w3, sr, session)
        elif choice == "6":
            result = admin_transfer_ownership(w3, sr, rpc, session)
            if result == "ownership_transferred":
                break   # kick old owner out of admin menu immediately
        elif choice == "7":
            admin_add_item(w3, sr, session)
        elif choice == "8":
            show_catalogue(sr, w3)
        elif choice == "0":
            break
        else:
            error("Invalid selection.")
            pause_prompt()


# ──────────────────────────────────────────────────────────────
#  USER MENU  (5 Normal User Tasks)
# ──────────────────────────────────────────────────────────────

def user_menu(w3, sr, rpc, session: Session) -> None:
    """User Menu — 5 Normal User Tasks."""
    while True:
        clear()
        greeting = f"Welcome, {session.name}" if session.name else f"{session.address[:14]}..."
        paused   = sr.functions.paused().call()
        status   = "  [SYSTEM PAUSED — redemptions disabled]" if paused else ""

        header(f"STORE REWARDS  |  {greeting}")
        if status:
            print(status)

        rpc_bal = bc.get_rpc_balance(rpc, session.address, w3)
        eth_bal = bc.get_eth_balance(w3, session.address)
        print(f"\n  Your Balances:  {rpc_bal:,.2f} RPC   |   {eth_bal:.4f} ETH")
        print()
        print(f"  ── User Tasks ──")
        print(f"  [1]  Earn Rewards            (Task 1)")
        print(f"  [2]  Redeem Rewards          (Task 2)")
        print(f"  [3]  Transfer Tokens         (Task 3)")
        print(f"  [4]  View Balance            (Task 4)")
        print(f"  [5]  View Transaction History (Task 5)")
        print()
        print(f"  ── Extras ──")
        print(f"  [7]  View Personal Activity History")
        print(f"  [8]  Check Address Balances")
        print()
        print(f"  [6]  Admin Panel (passphrase required)")
        print(f"  [0]  Exit")
        print()

        choice = input("  Selection: ").strip()

        if choice == "1":
            earn_rewards(w3, sr, rpc, session)
        elif choice == "2":
            redeem_reward(w3, sr, rpc, session)
        elif choice == "3":
            transfer_tokens(w3, rpc, session)
        elif choice == "4":
            view_balance(w3, sr, rpc, session)
        elif choice == "5":
            view_transaction_history(w3, sr, rpc)
        elif choice == "7":
            view_personal_activity_history(w3, sr, rpc)
        elif choice == "8":
            check_address_balances(w3, sr, rpc)
        elif choice == "6":
            secret = getpass.getpass("\n  Admin Passphrase: ")
            if secret == ADMIN_SECRET:
                # Double-check on-chain: user must still be an admin/owner
                if not sr.functions.isAdmin(session.address).call():
                    error("Access denied — your account no longer has admin privileges on-chain.")
                    pause_prompt()
                else:
                    success("Access granted. Entering Admin Panel.")
                    pause_prompt()
                    admin_menu(w3, sr, rpc, session)
            else:
                error("Incorrect passphrase. Access denied.")
                pause_prompt()
        elif choice == "0":
            print("\n  Goodbye.\n")
            sys.exit(0)
        else:
            error("Invalid selection.")
            pause_prompt()


# ──────────────────────────────────────────────────────────────
#  Startup
# ──────────────────────────────────────────────────────────────

def choose_account(w3) -> str:
    header("Account Selection")
    accounts = w3.eth.accounts
    for i, acc in enumerate(accounts):
        bal = bc.get_eth_balance(w3, acc)
        print(f"  [{i}]  {acc}   ({bal:.2f} ETH)")

    try:
        idx = int(input("\n  Select account index: ").strip())
        return accounts[idx]
    except (ValueError, IndexError):
        error("Invalid selection. Defaulting to account 0.")
        return accounts[0]


def main() -> None:
    clear()
    print(f"\n{SEPARATOR}")
    print("  STORE REWARDS & POINTS")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    address = choose_account(w3)
    session = Session(address)

    check_and_register(w3, sr, session)
    user_menu(w3, sr, rpc, session)


if __name__ == "__main__":
    main()
