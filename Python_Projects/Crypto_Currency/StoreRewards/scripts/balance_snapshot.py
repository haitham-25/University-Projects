#!/usr/bin/env python3
"""
==============================================================
  balance_snapshot.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Balance Snapshot CSV Exporter
  ------------------------------
  Scans every block on the chain, collects every unique address
  that has ever appeared in a transaction (sender or receiver),
  queries their current ETH balance and Reward Point Coin
  balance, and exports the results to a timestamped CSV file.

  Output CSV Columns
  ------------------
  Account Address | Reward Point Coin Balance | ETH Balance

  Usage
  -----
    python balance_snapshot.py
==============================================================
"""

import csv
import os
from datetime import datetime

import blockchain as bc

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
SEPARATOR  = "=" * 60


def collect_unique_addresses(w3) -> set:
    """
    Walk every mined block and collect every address that has
    appeared as a sender (from) or receiver (to) in any
    transaction.
    """
    addresses = set()
    latest    = w3.eth.block_number

    print(f"  Scanning {latest + 1} blocks for unique addresses...")

    for block_num in range(0, latest + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx.get("from"):
                addresses.add(tx["from"])
            if tx.get("to"):
                addresses.add(tx["to"])

    # Also include all Ganache accounts even if they haven't transacted
    for acc in w3.eth.accounts:
        addresses.add(acc)

    return addresses


def build_snapshot(w3, sr, rpc, addresses: set) -> list[dict]:
    """
    For each address, query live ETH and RPC balances and
    collect registration name if available.
    """
    rows = []
    for addr in sorted(addresses):
        eth_bal = bc.get_eth_balance(w3, addr)
        rpc_bal = bc.get_rpc_balance(rpc, addr, w3)

        try:
            name = sr.functions.getUserName(addr).call()
        except Exception:
            name = ""

        rows.append({
            "Account Address":            addr,
            "Registered Name":            name,
            "Reward Point Coin Balance":  f"{rpc_bal:.6f}",
            "ETH Balance":                f"{eth_bal:.6f}",
        })

    return rows


def export_csv(rows: list[dict]) -> str:
    """Write the snapshot rows to a timestamped CSV file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = os.path.join(OUTPUT_DIR, f"balance_snapshot_{timestamp}.csv")

    fieldnames = ["Account Address", "Registered Name",
                  "Reward Point Coin Balance", "ETH Balance"]

    with open(filename, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return filename


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  BALANCE SNAPSHOT EXPORTER — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    addresses = collect_unique_addresses(w3)
    print(f"  Found {len(addresses)} unique addresses.\n")

    print("  Querying balances...")
    rows = build_snapshot(w3, sr, rpc, addresses)

    print(f"\n  {'Address':<44} {'Name':<20} {'RPC Balance':>14}  {'ETH Balance':>12}")
    print(f"  {'-'*56}")
    for row in rows:
        addr_short = row["Account Address"][:42]
        name       = row["Registered Name"][:18] if row["Registered Name"] else "-"
        rpc_bal    = row["Reward Point Coin Balance"]
        eth_bal    = row["ETH Balance"]
        print(f"  {addr_short:<44} {name:<20} {rpc_bal:>14}  {eth_bal:>12}")

    output_path = export_csv(rows)

    print(f"\n  {'-'*56}")
    print(f"  Snapshot exported → {output_path}")
    print(f"  Rows written      : {len(rows)}")
    print(f"\n{SEPARATOR}\n")

def run_snapshot() -> None:
    main()
    
if __name__ == "__main__":
    main()
