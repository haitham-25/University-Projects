#!/usr/bin/env python3
"""
==============================================================
  auto_reward_distribution.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 1 — Automatic Reward Distribution
  -----------------------------------------------
  Periodically distributes reward tokens to all registered
  users. The admin wallet mints a configurable amount to each
  registered address at each interval.

  Usage
  -----
    python auto_reward_distribution.py

  Run in a separate terminal. Press Ctrl+C to stop.
==============================================================
"""

import time
import sys
from datetime import datetime

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
DISTRIBUTION_INTERVAL = 60   # seconds between each distribution round
REWARD_PER_USER       = 10   # RPC tokens to mint per registered user
SEPARATOR = "=" * 60


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def distribute(w3, sr, rpc, admin: str) -> None:
    """Mint REWARD_PER_USER RPC to every registered user."""
    try:
        users = sr.functions.getAllRegisteredUsers().call()
    except Exception as e:
        log(f"ERROR fetching users: {e}")
        return

    if not users:
        log("No registered users found — skipping distribution.")
        return

    amount_wei = w3.to_wei(REWARD_PER_USER, "ether")
    log(f"Distributing {REWARD_PER_USER} RPC to {len(users)} user(s)...")

    success_count = 0
    for user in users:
        try:
            tx_hash = rpc.functions.mint(user, amount_wei).transact({"from": admin})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            log(f"  ✓ Minted {REWARD_PER_USER} RPC → {user[:16]}... (block {receipt['blockNumber']})")
            # Emit on-chain earn event
            try:
                sr.functions.earnRewards(user, amount_wei).transact({"from": admin})
                w3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception:
                pass
            success_count += 1
        except Exception as e:
            log(f"  ✗ Failed for {user[:16]}...: {e}")

    log(f"Distribution complete — {success_count}/{len(users)} successful.")


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  AUTO REWARD DISTRIBUTION — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Interval       : every {DISTRIBUTION_INTERVAL}s")
    print(f"  Reward/User    : {REWARD_PER_USER} RPC")
    print("  Press Ctrl+C to stop.\n")

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)
    admin      = deployment["admin"]

    log(f"Admin wallet : {admin}")
    log(f"StoreRewards : {deployment['StoreRewards']['address']}")
    log(f"RPC Token    : {deployment['RewardPointCoin']['address']}")
    print()

    round_num = 0
    try:
        while True:
            round_num += 1
            log(f"=== Distribution Round #{round_num} ===")
            distribute(w3, sr, rpc, admin)
            log(f"Next distribution in {DISTRIBUTION_INTERVAL}s...\n")
            time.sleep(DISTRIBUTION_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Auto-distribution stopped.\n")


if __name__ == "__main__":
    main()
