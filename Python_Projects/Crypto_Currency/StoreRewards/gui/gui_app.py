#!/usr/bin/env python3
"""
==============================================================
  gui_app.py
  Project 4 — Store Rewards & Points
  Technologies of Cryptocurrencies — HNU
==============================================================
  BONUS — Tkinter GUI Application
  --------------------------------
  A fully interactive graphical front-end built with the Python
  standard library's tkinter module.  No additional GUI
  frameworks are required.

  Features
  --------
  • Account selector dropdown
  • Live ETH + RPC balance display (auto-refreshes)
  • Reward Items catalogue table
  • One-click redemption
  • Balance lookup panel
  • Activity history viewer
  • Admin panel (passphrase-protected)
    — Add item, batch add, delist, mint coins, pause/resume
  • Status bar with timestamped messages
==============================================================
"""
import sys
import os

# 🔴 مهم جداً: إضافة مسار scripts قبل أي import للبلوكشين
CURRENT_DIR = os.path.dirname(__file__)
SCRIPTS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'scripts'))
sys.path.insert(0, SCRIPTS_PATH)
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime

from web3.exceptions import ContractLogicError

import blockchain as bc

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────
ADMIN_SECRET   = "hnu2025admin"
REFRESH_MS     = 5000    # Balance refresh interval (ms)

# Colour palette
BG_DARK    = "#1e1e2e"
BG_PANEL   = "#2a2a3e"
BG_CARD    = "#313145"
FG_WHITE   = "#cdd6f4"
FG_DIM     = "#a6adc8"
ACCENT     = "#89b4fa"
SUCCESS    = "#a6e3a1"
DANGER     = "#f38ba8"
WARNING    = "#fab387"
FONT_HEAD  = ("Helvetica", 15, "bold")
FONT_BODY  = ("Helvetica", 11)
FONT_MONO  = ("Courier", 10)
FONT_SMALL = ("Helvetica", 9)


# ──────────────────────────────────────────────────────────────
#  Main Application Class
# ──────────────────────────────────────────────────────────────

class StoreRewardsApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Store Rewards & Points — HNU Blockchain Project")
        self.geometry("1080x720")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # ── Load blockchain ──────────────────────────────────
        try:
            self.deployment = bc.load_deployment()
            self.w3         = bc.connect(self.deployment)
            self.sr, self.rpc = bc.get_contracts(self.w3, self.deployment)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.destroy()
            return

        self.accounts      = self.w3.eth.accounts
        self.active_account = tk.StringVar(value=self.accounts[0])
        self.is_admin       = tk.BooleanVar(value=False)

        # ── Build UI ─────────────────────────────────────────
        self._build_header()
        self._build_paused_banner()
        self._build_main()
        self._build_status_bar()

        # ── Paused-state cache (updated by refresh loop) ─────
        self._contract_paused = False

        # ── Start refresh loop ───────────────────────────────
        self._refresh_balances()

    # ── Paused Banner ─────────────────────────────────────────

    def _build_paused_banner(self):
        self.paused_banner = tk.Frame(self, bg=DANGER, height=36)
        self.paused_banner_label = tk.Label(
            self.paused_banner,
            text="⚠  CONTRACT PAUSED — All transactions are disabled. Please wait for an admin to resume the system.",
            font=("Helvetica", 11, "bold"),
            bg=DANGER, fg=BG_DARK,
        )
        self.paused_banner_label.pack(pady=8)
        # Not packed yet — shown/hidden dynamically by _apply_paused_state()

    def _apply_paused_state(self, paused: bool):
        """Show or hide the paused banner and dis/enable action buttons."""
        self._contract_paused = paused
        if paused:
            self.paused_banner.pack(fill="x", side="top", after=self._header_frame)
        else:
            self.paused_banner.pack_forget()

    # ── Header ───────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_PANEL, height=70)
        hdr.pack(fill="x", side="top")
        self._header_frame = hdr  # keep ref for banner placement

        tk.Label(hdr, text="🏪  Store Rewards & Points",
                 font=FONT_HEAD, bg=BG_PANEL, fg=ACCENT).pack(side="left", padx=20, pady=16)

        # Account selector
        acc_frame = tk.Frame(hdr, bg=BG_PANEL)
        acc_frame.pack(side="right", padx=20, pady=10)

        tk.Label(acc_frame, text="Wallet:", font=FONT_BODY,
                 bg=BG_PANEL, fg=FG_DIM).pack(side="left")

        self.acc_menu = ttk.Combobox(
            acc_frame,
            textvariable=self.active_account,
            values=self.accounts,
            width=44,
            state="readonly",
            font=FONT_MONO,
        )
        self.acc_menu.pack(side="left", padx=(6, 0))
        self.acc_menu.bind("<<ComboboxSelected>>", self._on_account_change)

    # ── Main Layout ──────────────────────────────────────────

    def _build_main(self):
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Left sidebar
        left = tk.Frame(main, bg=BG_DARK, width=260)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)
        self._build_sidebar(left)

        # Right content area
        right = tk.Frame(main, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)
        self._build_notebook(right)

    # ── Sidebar ──────────────────────────────────────────────

    def _build_sidebar(self, parent):
        # Balance card
        card = tk.Frame(parent, bg=BG_CARD, relief="flat", bd=0)
        card.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="Your Balances", font=("Helvetica", 12, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(anchor="w", padx=14, pady=(12, 4))

        self.lbl_eth = tk.Label(card, text="ETH:  —", font=FONT_BODY,
                                 bg=BG_CARD, fg=FG_WHITE)
        self.lbl_eth.pack(anchor="w", padx=14, pady=2)

        self.lbl_rpc = tk.Label(card, text="RPC:  —", font=FONT_BODY,
                                 bg=BG_CARD, fg=SUCCESS)
        self.lbl_rpc.pack(anchor="w", padx=14, pady=(2, 12))

        # User info card
        card2 = tk.Frame(parent, bg=BG_CARD)
        card2.pack(fill="x", pady=(0, 10))
        tk.Label(card2, text="User Profile", font=("Helvetica", 12, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(anchor="w", padx=14, pady=(12, 4))
        self.lbl_name = tk.Label(card2, text="Name: —", font=FONT_BODY,
                                  bg=BG_CARD, fg=FG_WHITE)
        self.lbl_name.pack(anchor="w", padx=14, pady=2)
        self.lbl_status = tk.Label(card2, text="Status: —", font=FONT_BODY,
                                    bg=BG_CARD, fg=FG_DIM)
        self.lbl_status.pack(anchor="w", padx=14, pady=(2, 4))

        tk.Button(card2, text="Register / Update Name",
                  command=self._register_user,
                  font=FONT_SMALL, bg=ACCENT, fg=BG_DARK,
                  relief="flat", padx=10, pady=5).pack(padx=14, pady=8, fill="x")

        # Admin unlock
        card3 = tk.Frame(parent, bg=BG_CARD)
        card3.pack(fill="x", pady=(0, 10))
        tk.Label(card3, text="Admin Access", font=("Helvetica", 12, "bold"),
                 bg=BG_CARD, fg=WARNING).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Button(card3, text="🔐  Enter Admin Panel",
                  command=self._unlock_admin,
                  font=FONT_SMALL, bg=WARNING, fg=BG_DARK,
                  relief="flat", padx=10, pady=5).pack(padx=14, pady=8, fill="x")

        # Contract info
        card4 = tk.Frame(parent, bg=BG_CARD)
        card4.pack(fill="x")
        tk.Label(card4, text="Contract Info", font=("Helvetica", 12, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(anchor="w", padx=14, pady=(12, 4))
        self.lbl_paused = tk.Label(card4, text="Status: —", font=FONT_BODY,
                                    bg=BG_CARD, fg=FG_DIM)
        self.lbl_paused.pack(anchor="w", padx=14, pady=2)
        self.lbl_admin  = tk.Label(card4, text="Admin: —", font=FONT_SMALL,
                                    bg=BG_CARD, fg=FG_DIM, wraplength=220)
        self.lbl_admin.pack(anchor="w", padx=14, pady=(2, 12))

    # ── Notebook Tabs ─────────────────────────────────────────

    def _build_notebook(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",       background=BG_DARK,  borderwidth=0)
        style.configure("TNotebook.Tab",   background=BG_PANEL, foreground=FG_DIM,
                         padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT)])

        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill="both", expand=True)

        # Tab 1 — Catalogue
        tab1 = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(tab1, text="  Catalogue  ")
        self._build_catalogue_tab(tab1)

        # Tab 2 — Balance Checker
        tab2 = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(tab2, text="  Balance Checker  ")
        self._build_balance_tab(tab2)

        # Tab 3 — Activity History
        tab3 = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(tab3, text="  Activity History  ")
        self._build_history_tab(tab3)

    # ── Catalogue Tab ─────────────────────────────────────────

    def _build_catalogue_tab(self, parent):
        top = tk.Frame(parent, bg=BG_DARK)
        top.pack(fill="x", padx=8, pady=(10, 4))

        tk.Label(top, text="Available Reward Items", font=FONT_HEAD,
                 bg=BG_DARK, fg=ACCENT).pack(side="left")

        tk.Button(top, text="↻  Refresh", command=self._load_catalogue,
                  font=FONT_SMALL, bg=BG_PANEL, fg=ACCENT,
                  relief="flat", padx=10, pady=4).pack(side="right")

        tk.Button(top, text="✔  Redeem Selected", command=self._redeem_selected,
                  font=FONT_SMALL, bg=SUCCESS, fg=BG_DARK,
                  relief="flat", padx=10, pady=4).pack(side="right", padx=6)

        cols = ("ID", "Name", "Cost (RPC)", "Stock", "Status")
        self.cat_tree = ttk.Treeview(parent, columns=cols, show="headings",
                                      selectmode="browse")
        for col in cols:
            self.cat_tree.heading(col, text=col)
        self.cat_tree.column("ID",         width=50,  anchor="center")
        self.cat_tree.column("Name",       width=200)
        self.cat_tree.column("Cost (RPC)", width=100, anchor="center")
        self.cat_tree.column("Stock",      width=80,  anchor="center")
        self.cat_tree.column("Status",     width=80,  anchor="center")

        self.cat_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self._load_catalogue()

    def _load_catalogue(self):
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)

        # Tag colours: out-of-stock items shown in a muted colour
        self.cat_tree.tag_configure("out_of_stock", foreground="#888888")
        self.cat_tree.tag_configure("delisted",     foreground="#555555")

        items = bc.get_all_reward_items(self.sr, self.w3)
        for item in items:
            if not item["active"]:
                status = "Delisted"
                tag    = ("delisted",)
            elif item["stock"] == 0:
                status = "Out of Stock"
                tag    = ("out_of_stock",)
            else:
                status = "Active"
                tag    = ()
            self.cat_tree.insert("", "end",
                                  values=(item["id"], item["name"],
                                          item["pointCost"], item["stock"], status),
                                  tags=tag)

    def _redeem_selected(self):
        # ── Guard: block all actions while contract is paused ──
        if self._contract_paused:
            messagebox.showwarning(
                "System Paused",
                "The contract is currently PAUSED by an administrator.\n\n"
                "All transactions are disabled. Please try again later.",
            )
            return

        sel = self.cat_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a reward item first.")
            return

        values  = self.cat_tree.item(sel[0])["values"]
        item_id = int(values[0])
        cost    = int(values[2])
        name    = values[1]
        status  = values[4]          # "Active" | "Out of Stock" | "Delisted"
        stock   = int(values[3])
        addr    = self.active_account.get()

        # ── Guard: reject before any transaction is sent ──────
        if status == "Delisted":
            messagebox.showerror("Cannot Redeem",
                                 f"'{name}' has been delisted and is no longer available.")
            return
        if stock == 0 or status == "Out of Stock":
            messagebox.showerror("Out of Stock",
                                 f"'{name}' is currently out of stock.")
            return

        if not messagebox.askyesno("Confirm Redemption",
                                    f"Redeem '{name}' for {cost} RPC?"):
            return

        def do_redeem():
            try:
                # Check paused state live (may have changed since button press)
                live_paused = self.sr.functions.paused().call()
                if live_paused:
                    self.after(0, lambda: messagebox.showwarning(
                        "System Paused",
                        "The contract was paused before your transaction could be sent.\n"
                        "No tokens have been transferred. Please try again later.",
                    ))
                    return

                # Re-fetch live item state from the chain to protect against
                # race conditions (another user may have taken the last unit
                # between the UI load and this click).
                _live_id, _live_name, _live_cost, live_stock, live_active =                     self.sr.functions.getRewardItem(item_id).call()

                if not live_active:
                    self.after(0, lambda: messagebox.showerror(
                        "Cannot Redeem",
                        f"'{name}' was delisted while you were selecting."))
                    return
                if live_stock == 0:
                    self.after(0, lambda: (
                        messagebox.showerror("Out of Stock",
                            f"'{name}' just ran out of stock. Please refresh the catalogue."),
                        self._load_catalogue(),
                    ))
                    return

                admin_addr = self.sr.functions.getAdmin().call()
                cost_wei   = self.w3.to_wei(cost, "ether")
                bc.send_transaction(self.w3,
                                    self.rpc.functions.transfer(admin_addr, cost_wei),
                                    addr)
                bc.send_transaction(self.w3,
                                    self.sr.functions.redeemReward(item_id),
                                    addr)
                self.after(0, lambda: (
                    self._set_status(f"Redeemed '{name}' successfully!", SUCCESS),
                    self._load_catalogue(),
                    self._refresh_balances(),
                ))
            except (ContractLogicError, Exception) as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", DANGER))

        threading.Thread(target=do_redeem, daemon=True).start()

    # ── Balance Tab ───────────────────────────────────────────

    def _build_balance_tab(self, parent):
        tk.Label(parent, text="Check Any Wallet", font=FONT_HEAD,
                 bg=BG_DARK, fg=ACCENT).pack(anchor="w", padx=12, pady=(12, 6))

        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill="x", padx=12, pady=4)
        tk.Label(row, text="Address:", font=FONT_BODY, bg=BG_DARK, fg=FG_DIM).pack(side="left")
        self.bal_entry = tk.Entry(row, font=FONT_MONO, bg=BG_PANEL, fg=FG_WHITE,
                                   insertbackground=FG_WHITE, width=44, relief="flat")
        self.bal_entry.pack(side="left", padx=8, ipady=4)
        tk.Button(row, text="Check", command=self._check_balance,
                  font=FONT_SMALL, bg=ACCENT, fg=BG_DARK,
                  relief="flat", padx=14, pady=4).pack(side="left")

        self.bal_result = tk.Text(parent, font=FONT_BODY, bg=BG_CARD, fg=FG_WHITE,
                                   relief="flat", state="disabled", height=8)
        self.bal_result.pack(fill="x", padx=12, pady=10)

    def _check_balance(self):
        addr_raw = self.bal_entry.get().strip()
        if not addr_raw:
            return
        try:
            addr = self.w3.to_checksum_address(addr_raw)
        except Exception:
            messagebox.showerror("Error", "Invalid Ethereum address.")
            return

        eth_bal = bc.get_eth_balance(self.w3, addr)
        rpc_bal = bc.get_rpc_balance(self.rpc, addr, self.w3)
        try:
            name = self.sr.functions.getUserName(addr).call()
        except Exception:
            name = "(not registered)"

        text = (f"Address : {addr}\n"
                f"Name    : {name}\n"
                f"{'─'*52}\n"
                f"ETH Balance  :  {eth_bal:.6f} ETH\n"
                f"RPC Balance  :  {rpc_bal:,.4f} RPC\n")

        self.bal_result.config(state="normal")
        self.bal_result.delete("1.0", "end")
        self.bal_result.insert("end", text)
        self.bal_result.config(state="disabled")

    # ── History Tab ───────────────────────────────────────────

    def _build_history_tab(self, parent):
        tk.Label(parent, text="Activity History", font=FONT_HEAD,
                 bg=BG_DARK, fg=ACCENT).pack(anchor="w", padx=12, pady=(12, 6))

        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill="x", padx=12, pady=4)
        tk.Label(row, text="Address:", font=FONT_BODY, bg=BG_DARK, fg=FG_DIM).pack(side="left")
        self.hist_entry = tk.Entry(row, font=FONT_MONO, bg=BG_PANEL, fg=FG_WHITE,
                                    insertbackground=FG_WHITE, width=44, relief="flat")
        self.hist_entry.pack(side="left", padx=8, ipady=4)
        tk.Button(row, text="Scan", command=self._load_history,
                  font=FONT_SMALL, bg=ACCENT, fg=BG_DARK,
                  relief="flat", padx=14, pady=4).pack(side="left")

        cols = ("Block", "Action", "Transaction Hash")
        self.hist_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.hist_tree.heading(col, text=col)
        self.hist_tree.column("Block",            width=70,  anchor="center")
        self.hist_tree.column("Action",           width=200)
        self.hist_tree.column("Transaction Hash", width=360)
        self.hist_tree.pack(fill="both", expand=True, padx=12, pady=8)

    def _load_history(self):
        addr_raw = self.hist_entry.get().strip()
        if not addr_raw:
            return
        try:
            addr = self.w3.to_checksum_address(addr_raw)
        except Exception:
            messagebox.showerror("Error", "Invalid address.")
            return

        self._set_status("Scanning blockchain for activity...", ACCENT)

        def do_scan():
            events = bc.get_address_activity(self.w3, self.sr, self.rpc, addr)
            self.after(0, lambda: self._populate_history(events))

        threading.Thread(target=do_scan, daemon=True).start()

    def _populate_history(self, events):
        for row in self.hist_tree.get_children():
            self.hist_tree.delete(row)
        for ev in events:
            self.hist_tree.insert("", "end",
                                   values=(ev["block"], ev["action"], ev["tx"]))
        self._set_status(f"Found {len(events)} events.", SUCCESS)

    # ── Status Bar ────────────────────────────────────────────

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=BG_PANEL, height=28)
        bar.pack(fill="x", side="bottom")
        self.lbl_status_bar = tk.Label(bar, text="Ready.", font=FONT_SMALL,
                                        bg=BG_PANEL, fg=FG_DIM, anchor="w")
        self.lbl_status_bar.pack(side="left", padx=14)

    def _set_status(self, msg: str, colour: str = FG_DIM):
        ts = datetime.now().strftime("%H:%M:%S")
        self.lbl_status_bar.config(text=f"[{ts}]  {msg}", fg=colour)

    # ── Balance Refresh ───────────────────────────────────────

    def _refresh_balances(self):
        addr = self.active_account.get()
        try:
            eth = bc.get_eth_balance(self.w3, addr)
            rpc = bc.get_rpc_balance(self.rpc, addr, self.w3)
            self.lbl_eth.config(text=f"ETH:  {eth:.4f}")
            self.lbl_rpc.config(text=f"RPC:  {rpc:,.2f}")

            try:
                name = self.sr.functions.getUserName(addr).call()
                self.lbl_name.config(text=f"Name: {name}")
                self.lbl_status.config(text="Status: Registered", fg=SUCCESS)
            except Exception:
                self.lbl_name.config(text="Name: (not registered)")
                self.lbl_status.config(text="Status: Unregistered", fg=WARNING)

            paused = self.sr.functions.paused().call()
            admin  = self.sr.functions.getAdmin().call()
            self.lbl_paused.config(
                text=f"Status: {'PAUSED ⚠' if paused else 'ACTIVE ✓'}",
                fg=DANGER if paused else SUCCESS,
            )
            self.lbl_admin.config(text=f"Admin: {admin[:20]}...")
            self._apply_paused_state(paused)
        except Exception:
            pass

        self.after(REFRESH_MS, self._refresh_balances)

    # ── Account Change ────────────────────────────────────────

    def _on_account_change(self, _event=None):
        self.is_admin.set(False)
        self._refresh_balances()

    # ── User Registration ─────────────────────────────────────

    def _register_user(self):
        if self._contract_paused:
            messagebox.showwarning(
                "System Paused",
                "The contract is currently PAUSED.\n\nRegistration is disabled. Please try again later.",
            )
            return
        addr = self.active_account.get()
        name = simpledialog.askstring("Register", "Enter your display name:")
        if not name:
            return
        try:
            bc.send_transaction(self.w3, self.sr.functions.registerUser(name), addr)
            self._set_status(f"Registered as '{name}'.", SUCCESS)
            self._refresh_balances()
        except (ContractLogicError, Exception) as e:
            self._set_status(f"Registration failed: {e}", DANGER)

    # ── Admin Unlock ──────────────────────────────────────────

    def _unlock_admin(self):
        secret = simpledialog.askstring("Admin Access", "Enter Admin Passphrase:",
                                         show="*")
        if secret == ADMIN_SECRET:
            # Verify on-chain: passphrase alone is not enough after ownership transfer
            addr = self.active_account.get()
            if addr and not self.sr.functions.isAdmin(addr).call():
                messagebox.showerror(
                    "Access Denied",
                    "Your account no longer has admin privileges on-chain.",
                )
                return
            AdminWindow(self)
        else:
            messagebox.showerror("Access Denied", "Incorrect passphrase.")


# ──────────────────────────────────────────────────────────────
#  Admin Window
# ──────────────────────────────────────────────────────────────

class AdminWindow(tk.Toplevel):

    def __init__(self, master: StoreRewardsApp):
        super().__init__(master)
        self.app = master
        self.title("Admin Panel")
        self.geometry("540x480")
        self.configure(bg=BG_DARK)

        tk.Label(self, text="🔐  Admin Panel", font=FONT_HEAD,
                 bg=BG_DARK, fg=WARNING).pack(pady=(18, 10))

        btn_cfg = {"font": FONT_BODY, "bg": BG_PANEL, "fg": FG_WHITE,
                   "relief": "flat", "padx": 10, "pady": 8, "width": 34}

        tk.Button(self, text="➕  Add Reward Item",
                  command=self._add_item, **btn_cfg).pack(pady=4)
        tk.Button(self, text="📋  Batch Add Reward Items",
                  command=self._batch_add, **btn_cfg).pack(pady=4)
        tk.Button(self, text="❌  Delist Reward Item",
                  command=self._delist, **btn_cfg).pack(pady=4)
        tk.Button(self, text="💰  Mint Reward Point Coins",
                  command=self._mint, **btn_cfg).pack(pady=4)
        tk.Button(self, text="⏸   Pause / Resume Contract",
                  command=self._pause_resume, **btn_cfg).pack(pady=4)
        tk.Button(self, text="🔁  Transfer Ownership",
                  command=self._transfer_ownership, **btn_cfg).pack(pady=4)

        self.lbl_result = tk.Label(self, text="", font=FONT_BODY,
                                    bg=BG_DARK, fg=FG_DIM, wraplength=500)
        self.lbl_result.pack(pady=16)

    def _sender(self):
        return self.app.active_account.get()

    def _feedback(self, msg: str, colour: str = SUCCESS):
        self.lbl_result.config(text=msg, fg=colour)
        self.app._set_status(msg, colour)

    def _add_item(self):
        name  = simpledialog.askstring("Add Item", "Item Name:")
        if not name:
            return
        cost  = simpledialog.askinteger("Add Item", "Point Cost (RPC):")
        stock = simpledialog.askinteger("Add Item", "Stock Quantity:")
        if not cost or not stock:
            return
        try:
            bc.send_transaction(
                self.app.w3,
                self.app.sr.functions.addRewardItem(name, cost, stock),
                self._sender(),
            )
            self._feedback(f"'{name}' added successfully.")
            self.app._load_catalogue()
        except Exception as e:
            self._feedback(str(e), DANGER)

    def _batch_add(self):
        raw = simpledialog.askstring(
            "Batch Add",
            "Enter items as CSV lines:\nName, PointCost, Stock\n(separate lines with ';')"
        )
        if not raw:
            return
        names, costs, stocks = [], [], []
        for line in raw.split(";"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 3:
                try:
                    names.append(parts[0])
                    costs.append(int(parts[1]))
                    stocks.append(int(parts[2]))
                except ValueError:
                    pass
        if not names:
            self._feedback("No valid items parsed.", DANGER)
            return
        try:
            bc.send_transaction(
                self.app.w3,
                self.app.sr.functions.batchAddRewardItems(names, costs, stocks),
                self._sender(),
            )
            self._feedback(f"{len(names)} items added.")
            self.app._load_catalogue()
        except Exception as e:
            self._feedback(str(e), DANGER)

    def _delist(self):
        item_id = simpledialog.askinteger("Delist Item", "Enter Item ID:")
        if not item_id:
            return
        try:
            bc.send_transaction(
                self.app.w3,
                self.app.sr.functions.delistItem(item_id),
                self._sender(),
            )
            self._feedback(f"Item #{item_id} delisted.")
            self.app._load_catalogue()
        except Exception as e:
            self._feedback(str(e), DANGER)

    def _mint(self):
        to_raw = simpledialog.askstring("Mint", "Recipient Address:")
        amount = simpledialog.askfloat("Mint", "Amount (RPC):")
        if not to_raw or not amount:
            return
        try:
            to_addr    = self.app.w3.to_checksum_address(to_raw)
            amount_wei = self.app.w3.to_wei(amount, "ether")
            bc.send_transaction(
                self.app.w3,
                self.app.rpc.functions.mint(to_addr, amount_wei),
                self._sender(),
            )
            self._feedback(f"Minted {amount:,.2f} RPC to {to_addr[:16]}...")
        except Exception as e:
            self._feedback(str(e), DANGER)

    def _pause_resume(self):
        paused = self.app.sr.functions.paused().call()
        action = "resume" if paused else "pause"
        if not messagebox.askyesno("Confirm", f"Are you sure you want to {action} the contract?"):
            return
        try:
            fn = self.app.sr.functions.resume() if paused else self.app.sr.functions.pause()
            bc.send_transaction(self.app.w3, fn, self._sender())
            new_status = "ACTIVE" if paused else "PAUSED"
            self._feedback(f"Contract is now {new_status}.")
            # Immediately update the main window banner and sidebar status
            self.app._refresh_balances()
        except Exception as e:
            self._feedback(str(e), DANGER)

    def _transfer_ownership(self):
        new_admin_raw = simpledialog.askstring("Transfer Ownership", "New Admin Address:")
        if not new_admin_raw:
            return
        if not messagebox.askyesno("WARNING",
                                    "This permanently transfers admin rights. Proceed?\n\n"
                                    "You will lose all admin privileges immediately."):
            return
        try:
            new_admin = self.app.w3.to_checksum_address(new_admin_raw)
            bc.send_transaction(
                self.app.w3,
                self.app.sr.functions.transferOwnership(new_admin),
                self._sender(),
            )
            bc.send_transaction(
                self.app.w3,
                self.app.rpc.functions.transferAdminship(new_admin),
                self._sender(),
            )
            # Revoke admin flag in the GUI session and close admin window
            self.app.is_admin.set(False)
            messagebox.showinfo(
                "Ownership Transferred",
                f"Ownership transferred to {new_admin[:16]}...\n\n"
                "You are now a regular user.",
            )
            self.destroy()   # close the admin window — access revoked
        except Exception as e:
            self._feedback(str(e), DANGER)


# ──────────────────────────────────────────────────────────────
#  Entry Point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = StoreRewardsApp()
    app.mainloop()
