#!/usr/bin/env python3
"""
==============================================================
  data_history_report.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  System Task — Data History Report
  -----------------------------------
  Reads the ENTIRE blockchain history by scanning all
  on-chain RewardRedeemed events, then prints a clean text
  table showing every reward item ranked by popularity.

  Data gathered EXCLUSIVELY from blockchain history — no
  off-chain storage or databases are used.

  Output includes:
    • Item ID, Name, Point Cost, Current Stock, Status
    • Total times redeemed (from blockchain events)
    • Unique redeemers (distinct wallet addresses)
    • Popularity rank and percentage share

  Usage
  -----
    python data_history_report.py

  Prerequisites: auto_setup.py must have been run first.
==============================================================
"""

from collections import Counter, defaultdict

import blockchain as bc

SEPARATOR = "=" * 72
LINE      = "-" * 72
THIN      = "·" * 72


def print_banner() -> None:
    print(f"\n{SEPARATOR}")
    print("  DATA HISTORY REPORT — Most Popular Reward Items")
    print("  Store Rewards & Points  |  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)


def scan_redemption_history(w3, sr) -> tuple[list[dict], Counter, dict]:
    """
    Scan ALL blocks from genesis to current for RewardRedeemed events.

    Returns
    -------
    events        : Raw list of every redemption event dict.
    item_counter  : Counter mapping itemId → total redemptions.
    redeemers     : dict mapping itemId → set of unique user addresses.
    """
    print(f"\n  Scanning blockchain history for redemption events...")
    print(f"  Current block : {w3.eth.block_number:,}")
    print(f"  Scanning from : block 0\n")

    raw_logs = sr.events.RewardRedeemed.get_logs(from_block=0)

    events       = []
    item_counter = Counter()
    redeemers    = defaultdict(set)

    for log in raw_logs:
        args = dict(log["args"])
        item_id   = args["itemId"]
        user_addr = args["user"]
        pts_spent = args["pointsSpent"]
        item_name = args.get("itemName", "")

        events.append({
            "block":      log["blockNumber"],
            "tx":         log["transactionHash"].hex(),
            "itemId":     item_id,
            "itemName":   item_name,
            "user":       user_addr,
            "pointsSpent": pts_spent,
        })

        item_counter[item_id] += 1
        redeemers[item_id].add(user_addr)

    print(f"  Found {len(events)} total redemption event(s) across the chain.")
    return events, item_counter, redeemers


def fetch_item_catalogue(sr, w3) -> dict:
    """
    Pull current item data from the contract for every item ever created.
    Returns a dict mapping itemId → item info dict.
    """
    catalogue = {}
    total     = sr.functions.getTotalItems().call()

    for item_id in range(1, total + 1):
        try:
            id_, name, cost, stock, active = sr.functions.getRewardItem(item_id).call()
            catalogue[id_] = {
                "id":        id_,
                "name":      name,
                "pointCost": cost,
                "stock":     stock,
                "active":    active,
            }
        except Exception:
            pass  # item was removed or never existed

    return catalogue


def print_summary_stats(events: list, item_counter: Counter) -> None:
    """Print high-level statistics before the main table."""
    total_redemptions = len(events)
    unique_users      = len({e["user"] for e in events})
    total_rpc_spent   = sum(e["pointsSpent"] for e in events)
    most_popular_id   = item_counter.most_common(1)[0][0] if item_counter else None

    print(f"\n{SEPARATOR}")
    print("  SYSTEM OVERVIEW")
    print(SEPARATOR)
    print(f"  {'Total redemptions recorded on-chain':<40} {total_redemptions:>6,}")
    print(f"  {'Unique users who redeemed':<40} {unique_users:>6,}")
    print(f"  {'Distinct reward items redeemed':<40} {len(item_counter):>6,}")
    print(f"  {'Total RPC points spent (all-time)':<40} {total_rpc_spent:>6,}")
    if most_popular_id is not None:
        print(f"  {'Most redeemed item ID':<40} {most_popular_id:>6}")


def print_popularity_table(catalogue: dict, item_counter: Counter,
                            redeemers: dict, total_events: int) -> None:
    """Print the main ranked popularity table."""

    print(f"\n{SEPARATOR}")
    print("  REWARD ITEM POPULARITY RANKING  (sorted by redemption count)")
    print(SEPARATOR)

    # Merge catalogue with all item IDs ever seen in events
    all_ids = set(catalogue.keys()) | set(item_counter.keys())

    # Build rows — every item that ever existed
    rows = []
    for item_id in all_ids:
        info        = catalogue.get(item_id, {})
        redemptions = item_counter.get(item_id, 0)
        unique_rdmrs= len(redeemers.get(item_id, set()))
        pct         = (redemptions / total_events * 100) if total_events > 0 else 0.0
        status      = "Active  " if info.get("active") else "Delisted"
        name        = info.get("name", f"[Item #{item_id}]")
        cost        = info.get("pointCost", "?")
        stock       = info.get("stock", "?")

        rows.append({
            "rank":        0,           # filled after sort
            "id":          item_id,
            "name":        name,
            "cost":        cost,
            "stock":       stock,
            "status":      status,
            "redemptions": redemptions,
            "unique":      unique_rdmrs,
            "pct":         pct,
        })

    # Sort by redemptions descending, then by item id ascending as tiebreak
    rows.sort(key=lambda r: (-r["redemptions"], r["id"]))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    # Column header
    col = {
        "rank":  4,
        "id":    4,
        "name":  22,
        "cost":  9,
        "stock": 7,
        "redeem":9,
        "unique":8,
        "pct":   7,
        "status":8,
    }

    header = (
        f"  {'#':<{col['rank']}}"
        f"  {'ID':<{col['id']}}"
        f"  {'Item Name':<{col['name']}}"
        f"  {'Cost(RPC)':>{col['cost']}}"
        f"  {'Stock':>{col['stock']}}"
        f"  {'Redeemed':>{col['redeem']}}"
        f"  {'Unique':>{col['unique']}}"
        f"  {'Share%':>{col['pct']}}"
        f"  {'Status':<{col['status']}}"
    )
    print(header)
    print(f"  {LINE}")

    if not rows:
        print("  No reward items found on-chain.")
        return

    for row in rows:
        # Visual bar (max 20 chars wide)
        bar_len  = int(row["pct"] / 5) if total_events > 0 else 0
        bar      = "█" * bar_len + "░" * (20 - bar_len)

        name_trunc = row["name"][:20] if len(row["name"]) > 20 else row["name"]
        cost_str   = str(row["cost"]) if row["cost"] != "?" else "?"
        stock_str  = str(row["stock"]) if row["stock"] != "?" else "?"

        line = (
            f"  {row['rank']:<{col['rank']}}"
            f"  {row['id']:<{col['id']}}"
            f"  {name_trunc:<{col['name']}}"
            f"  {cost_str:>{col['cost']}}"
            f"  {stock_str:>{col['stock']}}"
            f"  {row['redemptions']:>{col['redeem']}}"
            f"  {row['unique']:>{col['unique']}}"
            f"  {row['pct']:>{col['pct']}.1f}"
            f"  {row['status']:<{col['status']}}"
        )
        print(line)
        # Progress bar on the next sub-line
        print(f"       {' ' * col['id']}  {' ' * col['name']}  {bar}  ({row['pct']:.1f}%)")

    print(f"  {LINE}")
    print(f"  Total rows: {len(rows)}  |  Redeemed items: {len(item_counter)}"
          f"  |  Never redeemed: {len(rows) - len(item_counter)}")


def print_block_by_block(events: list, w3) -> None:
    """Print a chronological redemption log — raw blockchain history."""

    print(f"\n{SEPARATOR}")
    print("  CHRONOLOGICAL REDEMPTION LOG  (raw blockchain history)")
    print(SEPARATOR)

    if not events:
        print("  No redemption events found on-chain.")
        print(f"\n{SEPARATOR}\n")
        return

    sorted_events = sorted(events, key=lambda e: e["block"])

    print(f"\n  {'Block':<9} {'Item':<22} {'Points':>8}  {'User (truncated)'}")
    print(f"  {LINE}")

    for ev in sorted_events:
        user_short = ev["user"][:16] + "..."
        name_trunc = ev["itemName"][:20] if ev["itemName"] else f"ID#{ev['itemId']}"
        print(f"  {ev['block']:<9} {name_trunc:<22} {ev['pointsSpent']:>8}  {user_short}")

    print(f"  {LINE}")
    print(f"  {len(sorted_events)} events shown  "
          f"|  blocks {sorted_events[0]['block']} → {sorted_events[-1]['block']}")


def main() -> None:
    print_banner()

    # ── Connect & load contracts ───────────────────────────────
    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, _rpc   = bc.get_contracts(w3, deployment)

    # ── Scan blockchain history ────────────────────────────────
    events, item_counter, redeemers = scan_redemption_history(w3, sr)

    # ── Pull item catalogue from contract ──────────────────────
    catalogue = fetch_item_catalogue(sr, w3)
    print(f"  Catalogue items on-chain: {len(catalogue)}")

    # ── Print reports ──────────────────────────────────────────
    print_summary_stats(events, item_counter)
    print_popularity_table(catalogue, item_counter, redeemers, len(events))
    print_block_by_block(events, w3)

    print(f"\n{SEPARATOR}")
    print("  Report complete.  All data read directly from blockchain history.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()