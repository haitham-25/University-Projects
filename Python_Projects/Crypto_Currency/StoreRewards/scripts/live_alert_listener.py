#!/usr/bin/env python3
"""
==============================================================
  live_alert_listener.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Live Alert System
  -----------------
  A background script that polls the blockchain every 2 seconds
  and prints a live alert to the terminal whenever a new event
  is detected on either the StoreRewards or RewardPointCoin
  contract.

  Alerts emitted:
    • ALERT: A reward purchase just happened!
    • ALERT: New coins were minted!
    • ALERT: A new user just registered!
    • ALERT: The contract was PAUSED / RESUMED!
    • ALERT: Admin ownership was transferred!
    • ALERT: A reward item was delisted!

  Usage
  -----
    python live_alert_listener.py

  Keep this running in a separate terminal while using the
  main terminal_app.py to see real-time notifications.
==============================================================
"""

import time
from datetime import datetime

import blockchain as bc

POLL_INTERVAL = 2    # Seconds between each blockchain poll
SEPARATOR     = "=" * 60


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def alert(message: str) -> None:
    print(f"  [{timestamp()}]  ⚡  {message}")


def check_and_report(new_logs: list, event_name: str) -> None:
    """Print an alert message for each new event log."""
    for log in new_logs:
        if event_name == "RewardRedeemed":
            item  = log.get("itemName", "Unknown Item")
            user  = log.get("user", "Unknown")[:14] + "..."
            pts   = log.get("pointsSpent", 0)
            alert(f"ALERT: A reward purchase just happened!  "
                  f"| Item: {item}  | User: {user}  | Cost: {pts} RPC")

        elif event_name == "Minted":
            to_  = log.get("to", "Unknown")[:14] + "..."
            amt  = log.get("amount", 0) / 10**18
            alert(f"ALERT: New coins were minted!  "
                  f"| To: {to_}  | Amount: {amt:,.2f} RPC")

        elif event_name == "UserRegistered":
            name = log.get("name", "Unknown")
            user = log.get("user", "Unknown")[:14] + "..."
            alert(f"ALERT: A new user just registered!  "
                  f"| Name: {name}  | Address: {user}")

        elif event_name == "ContractPaused":
            alert("ALERT: The contract has been PAUSED by the admin!  "
                  "All user operations are blocked.")

        elif event_name == "ContractResumed":
            alert("ALERT: The contract has been RESUMED.  "
                  "Normal operations are restored.")

        elif event_name == "AdminChanged":
            new = log.get("newAdmin", "Unknown")[:14] + "..."
            alert(f"ALERT: Admin ownership was transferred!  "
                  f"| New Admin: {new}")

        elif event_name == "RewardItemDelisted":
            item_id = log.get("id", "?")
            alert(f"ALERT: Reward item #{item_id} was delisted by the admin.")

        elif event_name == "RewardItemAdded":
            name = log.get("name", "Unknown")
            cost = log.get("pointCost", 0)
            alert(f"ALERT: New reward item added!  "
                  f"| Name: {name}  | Cost: {cost} RPC")


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  LIVE ALERT LISTENER — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(f"{SEPARATOR}")
    print(f"  Polling blockchain every {POLL_INTERVAL}s for events...")
    print("  Press Ctrl+C to stop.\n")

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    # Record the starting block so we only catch NEW events
    last_block = w3.eth.block_number
    print(f"  Listening from block #{last_block}\n")

    # Events to watch on StoreRewards
    sr_events = [
        "RewardRedeemed", "UserRegistered", "RewardItemAdded",
        "RewardItemDelisted", "ContractPaused", "ContractResumed",
        "AdminChanged",
    ]
    # Events to watch on RewardPointCoin
    rpc_events = ["Minted", "AdminChanged"]

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_block = w3.eth.block_number

            if current_block <= last_block:
                continue   # No new blocks, keep waiting

            # Scan only new blocks since the last check
            for event_name in sr_events:
                try:
                    event = getattr(sr.events, event_name)
                    logs  = event.get_logs(from_block=last_block + 1,
                                           to_block=current_block)
                    new_logs = [dict(l["args"]) for l in logs]
                    check_and_report(new_logs, event_name)
                except Exception:
                    pass

            for event_name in rpc_events:
                try:
                    event = getattr(rpc.events, event_name)
                    logs  = event.get_logs(from_block=last_block + 1,
                                           to_block=current_block)
                    new_logs = [dict(l["args"]) for l in logs]
                    check_and_report(new_logs, event_name)
                except Exception:
                    pass

            last_block = current_block

    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Listener stopped. Goodbye.\n")


if __name__ == "__main__":
    main()
