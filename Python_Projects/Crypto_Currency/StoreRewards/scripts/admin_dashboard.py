#!/usr/bin/env python3
"""
==============================================================
  admin_dashboard.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Admin Dashboard Script
  ----------------------
  Scans the entire blockchain history and prints a formatted
  system-wide summary, including:
    • Current contract admin
    • Total reward items in the store
    • Total Reward Point Coins minted (from on-chain events)
    • Total redemption transactions
    • Top 3 most active user addresses
    • Full reward items catalogue with popularity ranking
    • Pause status of the contract
==============================================================
"""

from collections import Counter

import blockchain as bc

SEPARATOR = "=" * 62
LINE      = "-" * 62


def print_header(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def print_section(title: str) -> None:
    print(f"\n  {title}")
    print(f"  {LINE[:len(title)+2]}")


# ──────────────────────────────────────────────────────────────
#  Main Dashboard
# ──────────────────────────────────────────────────────────────

def run_dashboard() -> None:
    print_header("ADMIN DASHBOARD — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    # Load deployment & connect
    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    # ── System Overview ──────────────────────────────────────
    print_section("System Overview")

    admin_addr   = sr.functions.getAdmin().call()
    paused       = sr.functions.paused().call()
    total_items  = sr.functions.getTotalItems().call()
    total_redeem = sr.functions.totalRedemptions().call()
    block_num    = w3.eth.block_number

    print(f"  {'Contract Admin':<30} {admin_addr}")
    print(f"  {'Contract Status':<30} {'PAUSED ⚠' if paused else 'ACTIVE ✓'}")
    print(f"  {'Current Block Number':<30} {block_num:,}")
    print(f"  {'Total Reward Items Created':<30} {total_items}")
    print(f"  {'Total Redemptions (all users)':<30} {total_redeem:,}")

    # ── Coin Supply (from on-chain mint events) ───────────────
    print_section("Reward Point Coin Supply")

    mint_events   = bc.scan_events(w3, rpc, "Minted")
    total_minted  = sum(e.get("amount", 0) for e in mint_events)
    total_minted_display = float(w3.from_wei(total_minted, "ether"))
    total_supply_live    = float(w3.from_wei(rpc.functions.totalSupply().call(), "ether"))

    print(f"  {'Total RPC Ever Minted':<30} {total_minted_display:,.2f} RPC")
    print(f"  {'Current Total Supply':<30} {total_supply_live:,.2f} RPC")
    print(f"  {'Mint Transactions':<30} {len(mint_events)}")

    # ── Transaction Count ─────────────────────────────────────
    print_section("Transaction Activity")

    sr_address  = deployment["StoreRewards"]["address"]
    rpc_address = deployment["RewardPointCoin"]["address"]
    sr_txs  = bc.get_all_transactions(w3, sr_address)
    rpc_txs = bc.get_all_transactions(w3, rpc_address)

    print(f"  {'StoreRewards Transactions':<30} {len(sr_txs):,}")
    print(f"  {'RewardPointCoin Transactions':<30} {len(rpc_txs):,}")
    print(f"  {'Combined On-Chain Transactions':<30} {len(sr_txs)+len(rpc_txs):,}")

    # ── Top 3 Most Active Users ───────────────────────────────
    print_section("Top 3 Most Active Users")

    redeem_events  = bc.scan_events(w3, sr, "RewardRedeemed")
    register_events= bc.scan_events(w3, sr, "UserRegistered")

    activity_counter: Counter = Counter()
    for e in redeem_events:
        activity_counter[e["user"]] += 1
    for e in register_events:
        activity_counter[e["user"]] += 1

    top3 = activity_counter.most_common(3)
    if top3:
        for rank, (addr, count) in enumerate(top3, 1):
            try:
                name = sr.functions.getUserName(addr).call()
            except Exception:
                name = "(unregistered)"
            eth_bal = bc.get_eth_balance(w3, addr)
            rpc_bal = bc.get_rpc_balance(rpc, addr, w3)
            print(f"  #{rank}  {addr}")
            print(f"       Name: {name:<20}  Actions: {count}")
            print(f"       ETH: {eth_bal:.4f}  |  RPC: {rpc_bal:,.2f}")
    else:
        print("  No user activity recorded yet.")

    # ── Reward Items Catalogue ────────────────────────────────
    print_section("Reward Items Catalogue (by Popularity)")

    # Count redemptions per item
    item_redeem_counter: Counter = Counter()
    for e in redeem_events:
        item_redeem_counter[e["itemId"]] += 1

    items = bc.get_all_reward_items(sr, w3)
    items.sort(key=lambda x: item_redeem_counter.get(x["id"], 0), reverse=True)

    print(f"\n  {'ID':<5} {'Name':<24} {'Cost(RPC)':<12} {'Stock':<8} {'Redeemed':<10} {'Status'}")
    print(f"  {LINE}")
    for item in items:
        redeemed = item_redeem_counter.get(item["id"], 0)
        status   = "Active" if item["active"] else "Delisted"
        print(f"  {item['id']:<5} {item['name']:<24} {item['pointCost']:<12} "
              f"{item['stock']:<8} {redeemed:<10} {status}")

    print(f"\n{SEPARATOR}")
    print("  Dashboard scan complete.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    run_dashboard()
