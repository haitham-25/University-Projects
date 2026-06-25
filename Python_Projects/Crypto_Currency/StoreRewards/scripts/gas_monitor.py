#!/usr/bin/env python3
"""
==============================================================
  gas_monitor.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task 5 — Gas Usage Monitor
  ------------------------------------
  Monitors and records the gas usage of all transactions
  interacting with the StoreRewards and RewardPointCoin
  contracts. Saves a rolling report to logs/gas_report.json.

  Usage
  -----
    python gas_monitor.py

  Run in a separate terminal. Press Ctrl+C to stop.
==============================================================
"""

import json
import os
import time
from datetime import datetime
from collections import defaultdict

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
POLL_INTERVAL  = 5
LOG_DIR        = os.path.join(os.path.dirname(__file__), "..", "logs")
GAS_REPORT     = os.path.join(LOG_DIR, "gas_report.json")
SEPARATOR      = "=" * 60


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"  [{timestamp()}]  {msg}")


def get_contract_txs(w3, contract_address: str, from_block: int, to_block: int) -> list:
    """Return receipts of transactions TO a contract address in block range."""
    results = []
    for block_num in range(from_block, to_block + 1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block["transactions"]:
                if tx.get("to") and tx["to"].lower() == contract_address.lower():
                    receipt = w3.eth.get_transaction_receipt(tx["hash"])
                    results.append({
                        "block":     block_num,
                        "tx":        tx["hash"].hex(),
                        "from":      tx["from"],
                        "to":        tx["to"],
                        "gas_used":  receipt["gasUsed"],
                        "gas_price": tx.get("gasPrice", 0),
                        "cost_wei":  receipt["gasUsed"] * tx.get("gasPrice", 0),
                        "timestamp": timestamp(),
                    })
        except Exception:
            pass
    return results


def load_report() -> dict:
    if os.path.exists(GAS_REPORT):
        try:
            with open(GAS_REPORT, "r") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {"transactions": [], "summary": {}}


def save_report(report: dict) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    txs = report["transactions"]
    if txs:
        total_gas   = sum(t["gas_used"] for t in txs)
        total_cost  = sum(t["cost_wei"] for t in txs)
        avg_gas     = total_gas // len(txs)
        report["summary"] = {
            "total_transactions": len(txs),
            "total_gas_used":     total_gas,
            "average_gas_used":   avg_gas,
            "total_cost_wei":     total_cost,
            "last_updated":       timestamp(),
        }
    with open(GAS_REPORT, "w") as fh:
        json.dump(report, fh, indent=2)


def print_summary(report: dict) -> None:
    s = report.get("summary", {})
    if not s:
        return
    print(f"\n  ── Gas Summary ──────────────────────────────────────")
    print(f"  Total Transactions : {s.get('total_transactions', 0):,}")
    print(f"  Total Gas Used     : {s.get('total_gas_used', 0):,}")
    print(f"  Average Gas/Tx     : {s.get('average_gas_used', 0):,}")
    print(f"  Total Cost (wei)   : {s.get('total_cost_wei', 0):,}")
    print(f"  ────────────────────────────────────────────────────\n")


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  GAS MONITOR — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)
    print(f"  Poll interval : {POLL_INTERVAL}s")
    print(f"  Report file   : {GAS_REPORT}")
    print("  Press Ctrl+C to stop.\n")

    deployment   = bc.load_deployment()
    w3           = bc.connect(deployment)
    sr_addr      = deployment["StoreRewards"]["address"]
    rpc_addr     = deployment["RewardPointCoin"]["address"]
    last_block   = w3.eth.block_number
    report       = load_report()

    log(f"Existing transactions : {len(report['transactions'])}")
    log(f"Monitoring from block #{last_block}")

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_block = w3.eth.block_number

            if current_block <= last_block:
                continue

            new_sr  = get_contract_txs(w3, sr_addr,  last_block + 1, current_block)
            new_rpc = get_contract_txs(w3, rpc_addr, last_block + 1, current_block)
            new_all = new_sr + new_rpc

            if new_all:
                report["transactions"].extend(new_all)
                save_report(report)
                log(f"Recorded {len(new_all)} new transaction(s).")
                print_summary(report)

            last_block = current_block

    except KeyboardInterrupt:
        print(f"\n\n  [{timestamp()}]  Gas monitor stopped.")
        save_report(report)
        print_summary(report)
        print(f"  Report saved to : {GAS_REPORT}\n")


if __name__ == "__main__":
    main()
