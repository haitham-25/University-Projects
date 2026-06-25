"""
==============================================================
  blockchain.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Blockchain Interaction Layer
  ----------------------------
  Centralised helper module imported by every script.
  Handles connection, contract loading, transaction sending,
  balance queries, and block scanning.  All raw web3.py calls
  are isolated here so the CLI and GUI layers stay clean.
==============================================================
"""

import json
import os
from typing import Any

from web3 import Web3
from web3.exceptions import ContractLogicError

# ──────────────────────────────────────────────────────────────
#  Deployment metadata path
# ──────────────────────────────────────────────────────────────
DEPLOY_FILE = os.path.join(os.path.dirname(__file__), "deployment.json")


# ──────────────────────────────────────────────────────────────
#  Connection & Contract Loading
# ──────────────────────────────────────────────────────────────

def load_deployment() -> dict:
    """Load the deployment.json written by auto_setup.py."""
    if not os.path.exists(DEPLOY_FILE):
        raise FileNotFoundError(
            "deployment.json not found. Run auto_setup.py first."
        )
    with open(DEPLOY_FILE, "r") as fh:
        return json.load(fh)


def connect(deployment: dict) -> Web3:
    """Create and verify a Web3 connection to Ganache."""
    w3 = Web3(Web3.HTTPProvider(deployment["ganache_url"]))
    if not w3.is_connected():
        raise ConnectionError(
            f"Cannot connect to Ganache at {deployment['ganache_url']}. "
            "Ensure Ganache is running."
        )
    return w3


def get_contracts(w3: Web3, deployment: dict):
    """Return bound StoreRewards and RewardPointCoin contract instances."""
    sr = w3.eth.contract(
        address=deployment["StoreRewards"]["address"],
        abi=deployment["StoreRewards"]["abi"],
    )
    rpc = w3.eth.contract(
        address=deployment["RewardPointCoin"]["address"],
        abi=deployment["RewardPointCoin"]["abi"],
    )
    return sr, rpc


# ──────────────────────────────────────────────────────────────
#  Transaction Sending
# ──────────────────────────────────────────────────────────────

def send_transaction(w3: Web3, fn, sender: str, value_wei: int = 0) -> dict:
    """
    Build, send, and wait for a contract function transaction.

    Parameters
    ----------
    w3        : Active Web3 instance.
    fn        : A bound contract function ready to call, e.g.
                sr.functions.registerUser("Alice").
    sender    : The Ethereum address that signs the transaction.
    value_wei : Optional ETH value to attach (in wei).

    Returns
    -------
    The mined transaction receipt as a dict.

    Raises
    ------
    ContractLogicError if the EVM reverts the transaction.
    """
    tx_params: dict[str, Any] = {"from": sender}
    if value_wei:
        tx_params["value"] = value_wei

    tx_hash = fn.transact(tx_params)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return dict(receipt)


# ──────────────────────────────────────────────────────────────
#  Balance Queries
# ──────────────────────────────────────────────────────────────

def get_eth_balance(w3: Web3, address: str) -> float:
    """Return the ETH balance of an address as a human-readable float."""
    raw = w3.eth.get_balance(address)
    return float(w3.from_wei(raw, "ether"))


def get_rpc_balance(rpc, address: str, w3: Web3) -> float:
    """Return the Reward Point Coin balance of an address (whole units)."""
    raw = rpc.functions.balanceOf(address).call()
    return float(w3.from_wei(raw, "ether"))


# ──────────────────────────────────────────────────────────────
#  Block Scanning
# ──────────────────────────────────────────────────────────────

def scan_events(w3: Web3, contract, event_name: str,
                from_block: int = 0) -> list:
    """
    Retrieve all past events of a given name from a contract.

    Parameters
    ----------
    w3          : Active Web3 instance.
    contract    : Bound contract instance.
    event_name  : The exact Solidity event name, e.g. 'RewardRedeemed'.
    from_block  : Starting block (default 0 = genesis).

    Returns
    -------
    List of event log attribute dicts.
    """
    event = getattr(contract.events, event_name)
    logs  = event.get_logs(from_block=from_block)
    return [dict(log["args"]) | {"blockNumber": log["blockNumber"],
                                 "transactionHash": log["transactionHash"].hex()}
            for log in logs]


def get_all_transactions(w3: Web3, contract_address: str) -> list[dict]:
    """
    Scan every mined block and collect all transactions that
    were sent to the given contract address.

    Returns a list of simplified transaction dicts.
    """
    results    = []
    latest     = w3.eth.block_number
    target     = contract_address.lower()

    for block_num in range(0, latest + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx.get("to") and tx["to"].lower() == target:
                results.append({
                    "block":  block_num,
                    "hash":   tx["hash"].hex(),
                    "from":   tx["from"],
                    "to":     tx["to"],
                    "value":  float(w3.from_wei(tx["value"], "ether")),
                    "gas":    tx["gas"],
                })
    return results


def get_address_activity(w3: Web3, sr, rpc, address: str) -> list[dict]:
    """
    Collect every on-chain action linked to a specific address
    across both contracts.

    Returns a unified list sorted by block number.
    """
    activity = []

    # StoreRewards events
    for event_name in ["UserRegistered", "RewardRedeemed"]:
        try:
            logs = getattr(sr.events, event_name).get_logs(from_block=0)
            for log in logs:
                args = dict(log["args"])
                actor = args.get("user", args.get("from", ""))
                if actor and actor.lower() == address.lower():
                    activity.append({
                        "block":  log["blockNumber"],
                        "action": event_name,
                        "detail": str(args),
                        "tx":     log["transactionHash"].hex(),
                    })
        except Exception:
            pass

    # RPC events (minting / transfers)
    for event_name in ["Minted", "Transfer"]:
        try:
            logs = getattr(rpc.events, event_name).get_logs(from_block=0)
            for log in logs:
                args  = dict(log["args"])
                to_   = args.get("to",   "")
                from_ = args.get("from", "")
                if (to_   and to_.lower()   == address.lower()) or \
                   (from_ and from_.lower() == address.lower()):
                    activity.append({
                        "block":  log["blockNumber"],
                        "action": f"RPC:{event_name}",
                        "detail": str(args),
                        "tx":     log["transactionHash"].hex(),
                    })
        except Exception:
            pass

    activity.sort(key=lambda x: x["block"])
    return activity


# ──────────────────────────────────────────────────────────────
#  Reward Item Helpers
# ──────────────────────────────────────────────────────────────

def get_all_reward_items(sr, w3: Web3) -> list[dict]:
    """
    Iterate item IDs from 1 up to getNextItemId() and return
    the full data for every item.
    """
    items      = []
    next_id    = sr.functions.getNextItemId().call()

    for item_id in range(1, next_id):
        try:
            id_, name, cost, stock, active = sr.functions.getRewardItem(item_id).call()
            items.append({
                "id":        id_,
                "name":      name,
                "pointCost": cost,
                "stock":     stock,
                "active":    active,
            })
        except ContractLogicError:
            pass   # Skips gaps if any item was deleted at the mapping level

    return items
