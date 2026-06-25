#!/usr/bin/env python3
"""
==============================================================
  auto_setup.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Auto-Setup Script
  -----------------
  Connects to a local Ganache network, compiles both smart
  contracts, deploys them, seeds demo data, and saves all
  deployment metadata to:
    • scripts/deployment.json          (runtime loader)
    • deployment/contracts.json        (address summary)
    • deployment/StoreRewards_ABI.json
    • deployment/RewardPointCoin_ABI.json

  Prerequisites
  -------------
  • Ganache running on http://127.0.0.1:7545
  • pip install web3 py-solc-x
==============================================================
"""

import json
import os
import sys
import balance_snapshot
import scheduled_snapshots


from web3 import Web3
from solcx import compile_source, install_solc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
GANACHE_URL   = "http://127.0.0.1:7545"
SOLC_VERSION  = "0.8.0"
CONTRACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "contracts")
DEPLOY_FILE   = os.path.join(os.path.dirname(__file__), "deployment.json")
DEPLOY_DIR    = os.path.join(os.path.dirname(__file__), "..", "deployment")

SEPARATOR = "=" * 60


def banner(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


# ──────────────────────────────────────────────────────────────
#  Step 1 — Connect to Ganache
# ──────────────────────────────────────────────────────────────
def connect_to_ganache() -> Web3:
    banner("Step 1 — Connecting to Ganache")
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

    if not w3.is_connected():
        print(f"  [ERROR] Cannot reach Ganache at {GANACHE_URL}")
        print("          Ensure Ganache is running and retry.")
        sys.exit(1)

    print(f"  Connected      : {GANACHE_URL}")
    print(f"  Chain ID       : {w3.eth.chain_id}")
    print(f"  Block Number   : {w3.eth.block_number}")
    print(f"  Accounts Found : {len(w3.eth.accounts)}")
    print(f"  Admin Account  : {w3.eth.accounts[0]}")
    return w3


# ──────────────────────────────────────────────────────────────
#  Step 2 — Compile Contracts
# ──────────────────────────────────────────────────────────────
def compile_contract(source_path: str, contract_name: str):
    with open(source_path, "r") as fh:
        source_code = fh.read()

    compiled = compile_source(
        source_code,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )

    key = f"<stdin>:{contract_name}"
    interface = compiled[key]
    return interface["abi"], interface["bin"]


def compile_all_contracts():
    banner("Step 2 — Compiling Smart Contracts")
    install_solc(SOLC_VERSION)
    print(f"  Solidity {SOLC_VERSION} compiler ready.")

    rpc_abi, rpc_bin = compile_contract(
        os.path.join(CONTRACTS_DIR, "RewardPointCoin.sol"),
        "RewardPointCoin",
    )
    print("  RewardPointCoin.sol  compiled successfully.")

    sr_abi, sr_bin = compile_contract(
        os.path.join(CONTRACTS_DIR, "StoreRewards.sol"),
        "StoreRewards",
    )
    print("  StoreRewards.sol     compiled successfully.")

    return rpc_abi, rpc_bin, sr_abi, sr_bin


# ──────────────────────────────────────────────────────────────
#  Step 3 — Deploy Contracts
# ──────────────────────────────────────────────────────────────
def deploy_contract(w3: Web3, abi, bytecode, deployer: str, label: str, *constructor_args):
    factory = w3.eth.contract(abi=abi, bytecode=bytecode)

    if constructor_args:
        tx_hash = factory.constructor(*constructor_args).transact({"from": deployer})
    else:
        tx_hash = factory.constructor().transact({"from": deployer})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    address = receipt.contractAddress

    print(f"  {label}")
    print(f"    Address  : {address}")
    print(f"    Gas Used : {receipt.gasUsed:,}")
    print(f"    Block    : {receipt.blockNumber}")
    return address


def deploy_all(w3: Web3, rpc_abi, rpc_bin, sr_abi, sr_bin):
    banner("Step 3 — Deploying Contracts to Ganache")
    admin = w3.eth.accounts[0]

    rpc_address = deploy_contract(w3, rpc_abi, rpc_bin, admin, "RewardPointCoin deployed →")
    sr_address  = deploy_contract(w3, sr_abi,  sr_bin,  admin, "StoreRewards deployed     →")

    return rpc_address, sr_address


# ──────────────────────────────────────────────────────────────
#  Step 4 — Seed Demo Data
# ──────────────────────────────────────────────────────────────
DEMO_ITEMS = {
    "names":      ["Free Coffee",    "10% Discount Coupon", "Free Dessert",
                   "Loyalty Tote Bag", "VIP Early Access",  "Birthday Cake Slice"],
    "pointCosts": [50,               100,                   150,
                   200,               500,                  75],
    "stocks":     [100,              200,                   80,
                   50,               20,                    120],
}


def seed_demo_data(w3: Web3, sr_address: str, rpc_address: str, sr_abi, rpc_abi):
    banner("Step 4 — Seeding Demo Reward Items")
    admin = w3.eth.accounts[0]
    sr    = w3.eth.contract(address=sr_address, abi=sr_abi)
    rpc   = w3.eth.contract(address=rpc_address, abi=rpc_abi)

    tx_hash = sr.functions.batchAddRewardItems(
        DEMO_ITEMS["names"],
        DEMO_ITEMS["pointCosts"],
        DEMO_ITEMS["stocks"],
    ).transact({"from": admin})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"  Batch transaction mined — {len(DEMO_ITEMS['names'])} items added.")
    print(f"  Gas used : {receipt.gasUsed:,}  |  Block : {receipt.blockNumber}")

    for i, name in enumerate(DEMO_ITEMS["names"], start=1):
        print(f"    [{i}] {name:<25}  Cost: {DEMO_ITEMS['pointCosts'][i-1]} RPC  "
              f"Stock: {DEMO_ITEMS['stocks'][i-1]}")

    INITIAL_MINT = 100_000
    mint_amount  = w3.to_wei(INITIAL_MINT, "ether")
    tx_hash = rpc.functions.mint(admin, mint_amount).transact({"from": admin})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n  Minted {INITIAL_MINT:,} RPC to admin wallet.")

    test_accounts = w3.eth.accounts[1:6]
    distribute_amount = w3.to_wei(1_000, "ether")
    for acc in test_accounts:
        tx_hash = rpc.functions.mint(acc, distribute_amount).transact({"from": admin})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  Distributed 1,000 RPC → {acc}")


# ──────────────────────────────────────────────────────────────
#  Step 5 — Save Deployment Metadata (scripts/ + deployment/)
# ──────────────────────────────────────────────────────────────
def save_deployment(w3: Web3, rpc_address: str, rpc_abi, sr_address: str, sr_abi) -> None:
    banner("Step 5 — Saving Deployment Metadata")

    # ── 5a: scripts/deployment.json (runtime loader used by all scripts) ──
    data = {
        "ganache_url": GANACHE_URL,
        "admin":       w3.eth.accounts[0],
        "accounts":    w3.eth.accounts,
        "RewardPointCoin": {
            "address": rpc_address,
            "abi":     rpc_abi,
        },
        "StoreRewards": {
            "address": sr_address,
            "abi":     sr_abi,
        },
    }

    with open(DEPLOY_FILE, "w") as fh:
        json.dump(data, fh, indent=2)
    print(f"  Runtime metadata saved → {DEPLOY_FILE}")

    # ── 5b: deployment/ directory artifacts ────────────────────
    os.makedirs(DEPLOY_DIR, exist_ok=True)

    # contracts.json  — address summary
    contracts_json = {
        "StoreRewards":    sr_address,
        "RewardPointCoin": rpc_address,
    }
    contracts_path = os.path.join(DEPLOY_DIR, "contracts.json")
    with open(contracts_path, "w") as fh:
        json.dump(contracts_json, fh, indent=2)
    print(f"  contracts.json saved          → {contracts_path}")

    # StoreRewards_ABI.json
    sr_abi_path = os.path.join(DEPLOY_DIR, "StoreRewards_ABI.json")
    with open(sr_abi_path, "w") as fh:
        json.dump(sr_abi, fh, indent=2)
    print(f"  StoreRewards_ABI.json saved   → {sr_abi_path}")

    # RewardPointCoin_ABI.json
    rpc_abi_path = os.path.join(DEPLOY_DIR, "RewardPointCoin_ABI.json")
    with open(rpc_abi_path, "w") as fh:
        json.dump(rpc_abi, fh, indent=2)
    print(f"  RewardPointCoin_ABI.json saved → {rpc_abi_path}")


# ──────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────
def main():
    print("\n" + SEPARATOR)
    print("  AUTO-SETUP SCRIPT — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    w3 = connect_to_ganache()

    rpc_abi, rpc_bin, sr_abi, sr_bin = compile_all_contracts()

    rpc_address, sr_address = deploy_all(w3, rpc_abi, rpc_bin, sr_abi, sr_bin)

    # Create deployment/ folder and save artifact files immediately after deployment
    os.makedirs(DEPLOY_DIR, exist_ok=True)

    with open(os.path.join(DEPLOY_DIR, "contracts.json"), "w") as f:
        json.dump({
            "StoreRewards": sr_address,
            "RewardPointCoin": rpc_address
        }, f, indent=4)

    with open(os.path.join(DEPLOY_DIR, "StoreRewards_ABI.json"), "w") as f:
        json.dump(sr_abi, f, indent=4)

    with open(os.path.join(DEPLOY_DIR, "RewardPointCoin_ABI.json"), "w") as f:
        json.dump(rpc_abi, f, indent=4)

    seed_demo_data(w3, sr_address, rpc_address, sr_abi, rpc_abi)

    save_deployment(w3, rpc_address, rpc_abi, sr_address, sr_abi)
    banner("Step 6 — Generating Initial Balance Snapshot")

    try:
        balance_snapshot.run_snapshot()
        print("  Initial balance snapshot created successfully.")
    except Exception as e:
        print(f"  Snapshot error: {e}")

    banner("Step 7 — Starting Scheduled Snapshots Service")

    try:
        scheduled_snapshots.start_scheduler()
        print("  Scheduled snapshot service started.")
    except Exception as e:
        print(f"  Scheduler error: {e}")
    banner("Setup Complete")
    print("  Both contracts are deployed and seeded.")
    print("  Deployment artifacts saved to deployment/ folder.")
    print("  Run   python terminal_app.py   to launch the main application.")
    print(SEPARATOR + "\n")


if __name__ == "__main__":
    main()
