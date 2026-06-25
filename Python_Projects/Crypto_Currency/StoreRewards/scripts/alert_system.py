#!/usr/bin/env python3
"""
==============================================================
  alert_system.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 6 — Alert System
  ------------------------------
  Monitors the blockchain and sends alerts (printed to
  terminal and logged to logs/alerts.json) when:
    • A transfer exceeds LARGE_TRANSFER_THRESHOLD RPC
    • More than REDEMPTION_SPIKE_THRESHOLD redemptions occur
      in a single block
    • The contract is paused or ownership transferred
    • More than MINT_SPIKE_THRESHOLD RPC minted in one tx

  Usage
  -----
    python alert_system.py

  Run in a separate terminal. Press Ctrl+C to stop.
==============================================================
"""

import json
import os
import time
from datetime import datetime

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
POLL_INTERVAL              = 3
LARGE_TRANSFER_THRESHOLD   = 1_000    # RPC
MINT_SPIKE_THRESHOLD       = 10_000   # RPC
REDEMPTION_SPIKE_THRESHOLD = 5        # redemptions per block
LOG_DIR    = os.path.join(os.path.dirname(__file__), "..", "logs")
ALERTS_LOG = os.path.join(LOG_DIR, "alerts.json")
SEPARATOR  = "=" * 60


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def alert(level: str, msg: str, details: dict, alerts: list) -> None:
    record = {
        "timestamp": timestamp(),
        "level":     level,
        "message":   msg,
        "details":   details,
    }
    alerts.append(record)
    icon = "🔴" if level == "CRITICAL" else "🟡"
    print(f"\n  {icon}  [{level}] {msg}")
    for k, v in details.items():
        print(f"         {k}: {v}")
    print()


def load_alerts() -> list:
    if os.path.exists(ALERTS_LOG):
        try:
            with open(ALERTS_LOG, "r") as fh:
                return json.load(fh)
        except Exception:
            return []
    return []


def save_alerts(alerts: list) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(ALERTS_LOG, "w") as fh:
        json.dump(alerts, fh, indent=2)


def check_events(w3, sr, rpc, from_block: int, to_block: int, alerts: list) -> None:
    # ── Large transfers ──────────────────────────────────────
    try:
        transfer_logs = rpc.events.Transfer.get_logs(from_block=from_block, to_block=to_block)
        for ev in transfer_logs:
            amount_rpc = ev["args"]["value"] / 10**18
            if amount_rpc >= LARGE_TRANSFER_THRESHOLD:
                alert("WARNING", "Large token transfer detected", {
                    "from":   ev["args"]["from"],
                    "to":     ev["args"]["to"],
                    "amount": f"{amount_rpc:,.2f} RPC",
                    "block":  ev["blockNumber"],
                    "tx":     ev["transactionHash"].hex(),
                }, alerts)
    except Exception:
        pass

    # ── Mint spike ───────────────────────────────────────────
    try:
        mint_logs = rpc.events.Minted.get_logs(from_block=from_block, to_block=to_block)
        for ev in mint_logs:
            amount_rpc = ev["args"]["amount"] / 10**18
            if amount_rpc >= MINT_SPIKE_THRESHOLD:
                alert("CRITICAL", "Large mint detected", {
                    "to":     ev["args"]["to"],
                    "amount": f"{amount_rpc:,.2f} RPC",
                    "block":  ev["blockNumber"],
                    "tx":     ev["transactionHash"].hex(),
                }, alerts)
    except Exception:
        pass

    # ── Redemption spike ─────────────────────────────────────
    try:
        redeem_logs = sr.events.RewardRedeemed.get_logs(from_block=from_block, to_block=to_block)
        block_counts = {}
        for ev in redeem_logs:
            b = ev["blockNumber"]
            block_counts[b] = block_counts.get(b, 0) + 1
        for block_num, count in block_counts.items():
            if count >= REDEMPTION_SPIKE_THRESHOLD:
                alert("WARNING", "Redemption spike detected", {
                    "block":      block_num,
                    "count":      count,
                    "threshold":  REDEMPTION_SPIKE_THRESHOLD,
                }, alerts)
    except Exception:
        pass

    # ── Contract paused ──────────────────────────────────────
    try:
        pause_logs = sr.events.ContractPaused.get_logs(from_block=from_block, to_block=to_block)
        for ev in pause_logs:
            alert("CRITICAL", "Contract PAUSED — all user ops blocked", {
                "by":    ev["args"]["by"],
                "block": ev["blockNumber"],
            }, alerts)
    except Exception:
        pass

    # ── Ownership transferred ────────────────────────────────
    try:
        owner_logs = sr.events.OwnershipTransferred.get_logs(from_block=from_block, to_block=to_block)
        for ev in owner_logs:
            alert("CRITICAL", "Ownership transferred", {
                "old_owner": ev["args"]["oldOwner"],
                "new_owner": ev["args"]["newOwner"],
                "block":     ev["blockNumber"],
            }, alerts)
    except Exception:
        pass


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  ALERT SYSTEM — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Large transfer threshold   : {LARGE_TRANSFER_THRESHOLD:,} RPC")
    print(f"  Mint spike threshold       : {MINT_SPIKE_THRESHOLD:,} RPC")
    print(f"  Redemption spike threshold : {REDEMPTION_SPIKE_THRESHOLD} per block")
    print(f"  Alert log                  : {ALERTS_LOG}")
    print("  Press Ctrl+C to stop.\n")

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)
    last_block = w3.eth.block_number
    alerts     = load_alerts()

    log(f"Existing alerts : {len(alerts)}")
    log(f"Monitoring from block #{last_block}")

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_block = w3.eth.block_number

            if current_block <= last_block:
                continue

            prev_count = len(alerts)
            check_events(w3, sr, rpc, last_block + 1, current_block, alerts)

            if len(alerts) > prev_count:
                save_alerts(alerts)

            last_block = current_block

    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Alert system stopped.")
        print(f"  Total alerts fired : {len(alerts)}")
        save_alerts(alerts)
        print(f"  Log saved to       : {ALERTS_LOG}\n")


if __name__ == "__main__":
    main()
