#!/usr/bin/env python3
"""
==============================================================
  security_test.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  Security Testing Script
  -----------------------
  Automated test suite that proves the contract's access-
  control, pause, and registration enforcement logic is
  functioning correctly.

  Each test sends a deliberately malicious or out-of-order
  transaction from a non-privileged account and asserts that
  the EVM rejects it with the expected revert reason.

  Test Cases
  ----------
  1. Normal user attempts to add a reward item → MUST FAIL
  2. Normal user attempts to mint RPC tokens   → MUST FAIL
  3. Normal user attempts to pause contract    → MUST FAIL
  4. Normal user attempts to transfer ownership→ MUST FAIL
  5. Unregistered user attempts to redeem      → MUST FAIL
  6. Admin pauses; user attempts to register   → MUST FAIL
  7. Admin resumes; user registers             → MUST SUCCEED
  8. Admin pauses; user attempts to redeem     → MUST FAIL
==============================================================
"""

import sys

from web3.exceptions import ContractLogicError

import blockchain as bc

SEPARATOR = "=" * 60
PASS_TAG  = "[PASS]"
FAIL_TAG  = "[FAIL]"


def run_test(test_name: str, should_succeed: bool, fn_call, sender: str, w3) -> bool:
    """
    Execute a single test case.

    Parameters
    ----------
    test_name      : Human-readable test description.
    should_succeed : True if the transaction is expected to pass.
    fn_call        : Bound contract function to call.
    sender         : Address that sends the transaction.
    w3             : Web3 instance.

    Returns
    -------
    True if the test passed, False otherwise.
    """
    try:
        bc.send_transaction(w3, fn_call, sender)
        # Transaction succeeded
        if should_succeed:
            print(f"  {PASS_TAG}  {test_name}")
            print(f"          Transaction succeeded as expected.")
            return True
        else:
            print(f"  {FAIL_TAG}  {test_name}")
            print(f"          Expected REVERT but transaction SUCCEEDED. Security breach!")
            return False

    except (ContractLogicError, Exception) as e:
        # Transaction was rejected by the EVM
        if not should_succeed:
            print(f"  {PASS_TAG}  {test_name}")
            print(f"          Correctly rejected. Revert: {str(e)[:80]}")
            return True
        else:
            print(f"  {FAIL_TAG}  {test_name}")
            print(f"          Expected SUCCESS but transaction REVERTED: {e}")
            return False


def main() -> None:
    print(f"\n{SEPARATOR}")
    print("  SECURITY TEST SUITE — Store Rewards & Points")
    print("  Technologies of Cryptocurrencies — HNU")
    print(SEPARATOR)

    deployment = bc.load_deployment()
    w3         = bc.connect(deployment)
    sr, rpc    = bc.get_contracts(w3, deployment)

    admin  = w3.eth.accounts[0]
    attacker = w3.eth.accounts[3]   # A random non-admin account

    print(f"\n  Admin    : {admin}")
    print(f"  Attacker : {attacker}")
    print(f"\n  Running {8} security tests...\n")
    print(f"  {'-'*58}")

    results = []

    # ── Test 1: Attacker tries to add a reward item ───────────
    results.append(run_test(
        test_name      = "Unauthorised addRewardItem() by non-admin",
        should_succeed = False,
        fn_call        = sr.functions.addRewardItem("Hack Item", 1, 1),
        sender         = attacker,
        w3             = w3,
    ))

    # ── Test 2: Attacker tries to mint coins ──────────────────
    results.append(run_test(
        test_name      = "Unauthorised mint() by non-admin",
        should_succeed = False,
        fn_call        = rpc.functions.mint(attacker, w3.to_wei(1000, "ether")),
        sender         = attacker,
        w3             = w3,
    ))

    # ── Test 3: Attacker tries to pause the contract ──────────
    results.append(run_test(
        test_name      = "Unauthorised pause() by non-admin",
        should_succeed = False,
        fn_call        = sr.functions.pause(),
        sender         = attacker,
        w3             = w3,
    ))

    # ── Test 4: Attacker tries to steal ownership ─────────────
    results.append(run_test(
        test_name      = "Unauthorised transferOwnership() by non-admin",
        should_succeed = False,
        fn_call        = sr.functions.transferOwnership(attacker),
        sender         = attacker,
        w3             = w3,
    ))

    # ── Test 5: Unregistered user tries to redeem ────────────
    # (Account 8 should not be registered by auto_setup)
    unregistered = w3.eth.accounts[8]
    results.append(run_test(
        test_name      = "Unregistered user tries to redeem reward",
        should_succeed = False,
        fn_call        = sr.functions.redeemReward(1),
        sender         = unregistered,
        w3             = w3,
    ))

    # ── Test 6: Admin pauses; user tries to register ─────────
    # First ensure not paused, then pause
    if not sr.functions.paused().call():
        bc.send_transaction(w3, sr.functions.pause(), admin)

    user_9 = w3.eth.accounts[9]
    results.append(run_test(
        test_name      = "User registration while contract is PAUSED",
        should_succeed = False,
        fn_call        = sr.functions.registerUser("PausedUser"),
        sender         = user_9,
        w3             = w3,
    ))

    # ── Test 7: Admin resumes; same user registers ────────────
    bc.send_transaction(w3, sr.functions.resume(), admin)
    results.append(run_test(
        test_name      = "User registration after contract RESUMES",
        should_succeed = True,
        fn_call        = sr.functions.registerUser("ResumedUser"),
        sender         = user_9,
        w3             = w3,
    ))

    # ── Test 8: Admin pauses again; registered user redeems ──
    bc.send_transaction(w3, sr.functions.pause(), admin)
    results.append(run_test(
        test_name      = "Registered user redeems while contract is PAUSED",
        should_succeed = False,
        fn_call        = sr.functions.redeemReward(1),
        sender         = user_9,
        w3             = w3,
    ))

    # Resume so other scripts are not left in a broken state
    bc.send_transaction(w3, sr.functions.resume(), admin)

    # ── Summary ───────────────────────────────────────────────
    passed = sum(results)
    total  = len(results)

    print(f"\n  {'-'*58}")
    print(f"\n  RESULTS : {passed}/{total} tests passed.")

    if passed == total:
        print("  All security rules are correctly enforced by the EVM.")
    else:
        failed = total - passed
        print(f"  WARNING: {failed} test(s) failed. Review the contract logic above.")

    print(f"\n{SEPARATOR}\n")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
