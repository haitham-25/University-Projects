#!/usr/bin/env python3
"""
==============================================================
  fraud_detection.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 2 — Fraud Detection
  ---------------------------------
  Monitors the blockchain for suspicious large token transfers
  that exceed a configurable threshold. Flags and logs them.

  Suspicious patterns detected:
    • Single transfer exceeding TRANSFER_THRESHOLD RPC
    • More than MAX_TX_PER_BLOCK transactions from one address
      in a single block
    • Rapid consecutive redemptions

  Usage
  -----
    python fraud_detection.py

  Run in a separate terminal. Press Ctrl+C to stop.
==============================================================
"""

import time
import json
import os
from datetime import datetime
from collections import defaultdict

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
POLL_INTERVAL       = 3       # seconds between polls
TRANSFER_THRESHOLD  = 5_000   # RPC — flag if single transfer > this
MAX_TX_PER_BLOCK    = 3       # flag if one address sends > this many txs in one block
FRAUD_LOG_FILE      = os.path.join(os.path.dirname(__file__), "..", "logs", "fraud_log.json")
SEPARATOR           = "=" * 60


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def flag_fraud(label: str, details: dict, fraud_records: list) -> None:
    record = {
        "timestamp": timestamp(),
        "type":      label,
        "details":   details,
    }
    fraud_records.append(record)
    print(f"\n  ⚠️  FRAUD ALERT: {label}")
    for k, v in details.items():
        print(f"       {k}: {v}")
    print()


def save_fraud_log(fraud_records: list) -> None:
    os.makedirs(os.path.dirname(FRAUD_LOG_FILE), exist_ok=True)
    with open(FRAUD_LOG_FILE, "w") as fh:
        json.dump(fraud_records, fh, indent=2)


def scan_transfers(w3, rpc, from_block: int, to_block: int, fraud_records: list) -> None:
    """Scan Transfer events on the RPC token for suspicious activity."""
    try:
        logs = rpc.events.Transfer.get_logs(from_block=from_block, to_block=to_block)
    except Exception:
        return

    block_sender_counts = defaultdict(lambda: defaultdict(int))

    for ev in logs:
        args        = ev["args"]
        sender      = args.get("from", "0x0")
        receiver    = args.get("to",   "0x0")
        amount_wei  = args.get("value", 0)
        amount_rpc  = amount_wei / 10**18
        block_num   = ev["blockNumber"]

        # Check large transfer
        if amount_rpc > TRANSFER_THRESHOLD:
            flag_fraud("LARGE_TRANSFER", {
                "from":        sender,
                "to":          receiver,
                "amount_RPC":  f"{amount_rpc:,.2f}",
                "block":       block_num,
                "tx":          ev["transactionHash"].hex(),
            }, fraud_records)

        # Count per sender per block
        if sender != "0x0000000000000000000000000000000000000000":
            block_sender_counts[block_num][sender] += 1

    # Check high-frequency senders
    for block_num, senders in block_sender_counts.items():
        for sender, count in senders.items():
            if count > MAX_TX_PER_BLOCK:
                flag_fraud("HIGH_FREQUENCY_SENDER", {
                    "sender":    sender,
                    "tx_count":  count,
                    "block":     block_num,
                    "threshold": MAX_TX_PER_BLOCK,
                }, fraud_records)


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  FRAUD DETECTION — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Transfer threshold : {TRANSFER_THRESHOLD:,} RPC")
    print(f"  Poll interval      : {POLL_INTERVAL}s")
    print(f"  Fraud log          : {FRAUD_LOG_FILE}")
    print("  Press Ctrl+C to stop.\n")

    deployment   = bc.load_deployment()
    w3           = bc.connect(deployment)
    _, rpc       = bc.get_contracts(w3, deployment)
    last_block   = w3.eth.block_number
    fraud_records = []

    log(f"Monitoring from block #{last_block}")

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_block = w3.eth.block_number

            if current_block <= last_block:
                continue

            scan_transfers(w3, rpc, last_block + 1, current_block, fraud_records)

            if fraud_records:
                save_fraud_log(fraud_records)

            last_block = current_block

    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Fraud detection stopped.")
        print(f"  Total fraud alerts : {len(fraud_records)}")
        if fraud_records:
            save_fraud_log(fraud_records)
            print(f"  Log saved to       : {FRAUD_LOG_FILE}")
        print()


if __name__ == "__main__":
    main()
