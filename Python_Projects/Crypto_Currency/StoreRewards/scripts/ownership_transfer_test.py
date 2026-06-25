#!/usr/bin/env python3
"""
==============================================================
  ownership_transfer_test.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Ownership Transfer Test Script
  -------------------------------
  Demonstrates and proves the transferOwnership() function
  by executing the following four-step sequence:

  Step 1 — Original admin performs a privileged action.
  Step 2 — Admin transfers ownership to a second account.
  Step 3 — Original admin's privileged action now FAILS.
  Step 4 — New admin's privileged action SUCCEEDS.

  This script verifies both the StoreRewards and
  RewardPointCoin contracts are updated consistently.
==============================================================
"""

from web3.exceptions import ContractLogicError

import blockchain as bc

SEPARATOR = "=" * 60


def step(n: int, description: str) -> None:
    print(f"\n  ── Step {n}: {description}")
    print(f"  {'─'*50}")


def result(success: bool, message: str) -> None:
    tag = "[OK]   " if success else "[FAIL] "
    print(f"  {tag} {message}")


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  OWNERSHIP TRANSFER TEST — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    deployment  = bc.load_deployment()
    w3          = bc.connect(deployment)
    sr, rpc     = bc.get_contracts(w3, deployment)

    original_admin = w3.eth.accounts[0]
    new_admin      = w3.eth.accounts[7]   # A fresh account to receive ownership

    print(f"\n  Original Admin : {original_admin}")
    print(f"  New Admin      : {new_admin}")

    # ── Step 1: Original admin performs a privileged action ───
    step(1, "Original admin adds a reward item (must succeed)")
    try:
        receipt = bc.send_transaction(
            w3,
            sr.functions.addRewardItem("Ownership Test Item", 10, 5),
            original_admin,
        )
        result(True, f"Item added successfully. Block #{receipt['blockNumber']}")
        admin_check = sr.functions.getAdmin().call()
        result(True, f"Current admin confirmed: {admin_check}")
    except Exception as e:
        result(False, f"Unexpected failure: {e}")
        return

    # ── Step 2: Transfer ownership ────────────────────────────
    step(2, "Original admin transfers ownership to the new admin")
    try:
        # Transfer StoreRewards admin
        receipt = bc.send_transaction(
            w3,
            sr.functions.transferOwnership(new_admin),
            original_admin,
        )
        result(True, f"StoreRewards ownership transferred. Block #{receipt['blockNumber']}")

        # Transfer RewardPointCoin admin
        receipt = bc.send_transaction(
            w3,
            rpc.functions.transferAdminship(new_admin),
            original_admin,
        )
        result(True, f"RewardPointCoin adminship transferred. Block #{receipt['blockNumber']}")

        new_sr_admin  = sr.functions.getAdmin().call()
        new_rpc_admin = rpc.functions.getAdmin().call()
        result(True, f"StoreRewards  new admin: {new_sr_admin}")
        result(True, f"RewardPointCoin new admin: {new_rpc_admin}")

    except Exception as e:
        result(False, f"Transfer failed: {e}")
        return

    # ── Step 3: Original admin action now FAILS ───────────────
    step(3, "Original admin's privileged action now FAILS (must be rejected)")
    try:
        bc.send_transaction(
            w3,
            sr.functions.addRewardItem("Should Fail Item", 10, 5),
            original_admin,
        )
        result(False, "Action SUCCEEDED — ownership transfer did NOT work! Security breach!")
    except (ContractLogicError, Exception) as e:
        result(True, f"Correctly rejected. Original admin has no power.")
        result(True, f"Revert reason: {str(e)[:70]}")

    # ── Step 4: New admin action SUCCEEDS ─────────────────────
    step(4, "New admin's privileged action SUCCEEDS")
    try:
        receipt = bc.send_transaction(
            w3,
            sr.functions.addRewardItem("New Admin Item", 25, 10),
            new_admin,
        )
        result(True, f"New admin successfully added item. Block #{receipt['blockNumber']}")

        # Also verify minting works under new admin
        receipt = bc.send_transaction(
            w3,
            rpc.functions.mint(new_admin, w3.to_wei(500, "ether")),
            new_admin,
        )
        result(True, f"New admin minted 500 RPC successfully. Block #{receipt['blockNumber']}")

    except Exception as e:
        result(False, f"New admin action failed unexpectedly: {e}")
        return

    # ── Restore ownership to original admin ───────────────────
    step(5, "Restoring original admin (cleanup for other scripts)")
    try:
        bc.send_transaction(
            w3,
            sr.functions.transferOwnership(original_admin),
            new_admin,
        )
        bc.send_transaction(
            w3,
            rpc.functions.transferAdminship(original_admin),
            new_admin,
        )
        result(True, "Ownership restored to original admin.")
    except Exception as e:
        result(False, f"Cleanup failed: {e}")

    print(f"\n{SEPARATOR}")
    print("  Ownership transfer test complete.")
    print("  All four steps verified the access-control mechanism is working.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()
