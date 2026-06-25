#!/usr/bin/env python3
"""
==============================================================
  scheduled_snapshots.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 3 — Scheduled Balance Snapshots
  ---------------------------------------------
  Periodically saves the RPC token balance of every registered
  user to a timestamped CSV file in the snapshots/ folder.

  Usage
  -----
    python scheduled_snapshots.py

  Run in a separate terminal. Press Ctrl+C to stop.
==============================================================
"""

import csv
import os
import time
from datetime import datetime

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
SNAPSHOT_INTERVAL = 120   # seconds between snapshots
SNAPSHOT_DIR      = os.path.join(os.path.dirname(__file__), "..", "snapshots")
SEPARATOR         = "=" * 60


def timestamp(fmt="%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(fmt)


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def take_snapshot(w3, sr, rpc) -> str:
    """Capture balances of all registered users and save to CSV."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    fname = datetime.now().strftime("snapshot_%Y%m%d_%H%M%S.csv")
    fpath = os.path.join(SNAPSHOT_DIR, fname)

    users = []
    try:
        users = sr.functions.getAllRegisteredUsers().call()
    except Exception as e:
        log(f"ERROR fetching users: {e}")
        return ""

    rows = []
    for addr in users:
        eth_bal = bc.get_eth_balance(w3, addr)
        rpc_bal = bc.get_rpc_balance(rpc, addr, w3)
        try:
            name = sr.functions.getUserName(addr).call()
        except Exception:
            name = ""
        try:
            redemptions = sr.functions.getUserTotalRedemptions(addr).call()
        except Exception:
            redemptions = 0
        rows.append({
            "timestamp":   timestamp(),
            "address":     addr,
            "name":        name,
            "eth_balance": f"{eth_bal:.6f}",
            "rpc_balance": f"{rpc_bal:.2f}",
            "redemptions": redemptions,
        })

    with open(fpath, "w", newline="") as fh:
        fieldnames = ["timestamp", "address", "name", "eth_balance", "rpc_balance", "redemptions"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return fpath


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  SCHEDULED SNAPSHOTS — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Snapshot interval : every {SNAPSHOT_INTERVAL}s")
    print(f"  Snapshot folder   : {SNAPSHOT_DIR}")
    print("  Press Ctrl+C to stop.\n")

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    snap_count = 0
    try:
        while True:
            snap_count += 1
            log(f"Taking snapshot #{snap_count}...")
            fpath = take_snapshot(w3, sr, rpc)
            if fpath:
                log(f"Saved → {os.path.basename(fpath)}")
            else:
                log("Snapshot skipped (no users or error).")
            log(f"Next snapshot in {SNAPSHOT_INTERVAL}s...\n")
            time.sleep(SNAPSHOT_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Snapshot scheduler stopped.")
        print(f"  Total snapshots taken : {snap_count - 1}\n")

def start_scheduler() -> None:
    main()
if __name__ == "__main__":
    main()
