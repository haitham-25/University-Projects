#!/usr/bin/env python3
"""
==============================================================
  activity_logger.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 4 — Activity Logger
  ---------------------------------
  Continuously polls both contracts for new events and appends
  them to a persistent JSON log file (logs/activity_log.json).
  Every event type from both contracts is captured.

  Usage
  -----
    python activity_logger.py

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
POLL_INTERVAL   = 3
LOG_DIR         = os.path.join(os.path.dirname(__file__), "..", "logs")
ACTIVITY_LOG    = os.path.join(LOG_DIR, "activity_log.json")
SEPARATOR       = "=" * 60

SR_EVENTS  = [
    "UserRegistered", "RewardRedeemed", "RewardEarned",
    "RewardItemAdded", "RewardItemUpdated", "RewardItemDelisted",
    "ContractPaused", "ContractResumed",
    "OwnershipTransferred", "AdminAdded", "AdminRemoved",
    "UserAdded", "UserRemoved", "BatchItemsAdded",
]
RPC_EVENTS = ["Transfer", "Minted", "Burned", "AdminChanged", "Approval"]


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def load_existing_log() -> list:
    if os.path.exists(ACTIVITY_LOG):
        try:
            with open(ACTIVITY_LOG, "r") as fh:
                return json.load(fh)
        except Exception:
            return []
    return []


def save_log(records: list) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(ACTIVITY_LOG, "w") as fh:
        json.dump(records, fh, indent=2)


def collect_events(contract, event_names: list, from_block: int, to_block: int,
                   source: str, records: list) -> int:
    """Scan events and append new entries to records. Returns count added."""
    added = 0
    for event_name in event_names:
        try:
            event = getattr(contract.events, event_name)
            logs  = event.get_logs(from_block=from_block, to_block=to_block)
            for ev in logs:
                entry = {
                    "timestamp":  timestamp(),
                    "source":     source,
                    "event":      event_name,
                    "block":      ev["blockNumber"],
                    "tx":         ev["transactionHash"].hex(),
                    "args":       {k: str(v) for k, v in dict(ev["args"]).items()},
                }
                records.append(entry)
                added += 1
                log(f"  Logged [{source}] {event_name}  block={ev['blockNumber']}")
        except Exception:
            pass
    return added


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  ACTIVITY LOGGER — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Poll interval : {POLL_INTERVAL}s")
    print(f"  Log file      : {ACTIVITY_LOG}")
    print("  Press Ctrl+C to stop.\n")

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)
    last_block = w3.eth.block_number
    records    = load_existing_log()

    log(f"Loaded {len(records)} existing log entries.")
    log(f"Monitoring from block #{last_block}")

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_block = w3.eth.block_number

            if current_block <= last_block:
                continue

            added  = collect_events(sr,  SR_EVENTS,  last_block + 1, current_block, "StoreRewards",    records)
            added += collect_events(rpc, RPC_EVENTS, last_block + 1, current_block, "RewardPointCoin", records)

            if added:
                save_log(records)
                log(f"Saved {added} new event(s) — total: {len(records)}")

            last_block = current_block

    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Activity logger stopped.")
        print(f"  Total events logged : {len(records)}")
        save_log(records)
        print(f"  Log saved to        : {ACTIVITY_LOG}\n")


if __name__ == "__main__":
    main()
