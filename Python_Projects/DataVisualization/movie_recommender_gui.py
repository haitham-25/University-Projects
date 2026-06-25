"""
🎬 Movie Recommendation System — GUI
====================================
Based on: Netflix-inspired Watch History Dataset (DM.ipynb)

Requirements (install once):
    pip install pandas numpy matplotlib networkx apyori mlxtend sentence-transformers scikit-learn

Run:
    python movie_recommender_gui.py

The app auto-generates a synthetic dataset if 'movies_dataset.csv' is not found.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os, pickle, math, warnings
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE  (dark Netflix-style)
# ─────────────────────────────────────────────────────────────
BG        = "#141414"
PANEL     = "#1f1f1f"
CARD      = "#2a2a2a"
ACCENT    = "#e50914"       # Netflix red
ACCENT2   = "#f5c518"       # IMDb yellow
TEXT      = "#ffffff"
TEXT_SUB  = "#aaaaaa"
GREEN     = "#2a9d8f"
BLUE      = "#457b9d"

FONT_H1   = ("Helvetica", 20, "bold")
FONT_H2   = ("Helvetica", 14, "bold")
FONT_BODY = ("Helvetica", 11)
FONT_MONO = ("Courier", 10)

# ─────────────────────────────────────────────────────────────
# GENRE MAP  (from notebook)
# ─────────────────────────────────────────────────────────────
GENRE_MAP = {
    'Inception':'Sci-Fi','The Dark Knight':'Action','Interstellar':'Sci-Fi',
    'The Matrix':'Sci-Fi','Iron Man':'Action','Joker':'Drama',
    'Parasite':'Thriller','The Godfather':'Crime','Pulp Fiction':'Crime',
    'Fight Club':'Drama','Forrest Gump':'Drama','The Lion King':'Animation',
    'Titanic':'Romance','Avatar':'Sci-Fi','Toy Story':'Animation',
    'The Avengers':'Action','Black Panther':'Action',
    'Guardians of the Galaxy':'Action','Spider-Man':'Action',
    'Doctor Strange':'Action','Thor':'Action','Captain America':'Action',
    'Ant-Man':'Action','Shrek':'Animation','Finding Nemo':'Animation',
    'Up':'Animation','WALL-E':'Animation','Coco':'Animation','Frozen':'Animation',
    'Harry Potter':'Fantasy','Lord of the Rings':'Fantasy','Star Wars':'Sci-Fi',
    'Jurassic Park':'Sci-Fi','The Hunger Games':'Sci-Fi','Twilight':'Romance',
    'Deadpool':'Action','Logan':'Action','Venom':'Action',
    'Aquaman':'Action','Wonder Woman':'Action','Batman v Superman':'Action',
    'Man of Steel':'Action','The Social Network':'Drama','Gone Girl':'Thriller',
    'Whiplash':'Drama','La La Land':'Romance','Mad Max: Fury Road':'Action',
    'John Wick':'Action','Mission: Impossible':'Action',
}

ALL_MOVIES = sorted(GENRE_MAP.keys())


# ═══════════════════════════════════════════════════════════════
# DATA  LAYER
# ═══════════════════════════════════════════════════════════════
class DataEngine:
    """Loads / generates dataset, runs all mining algorithms."""

    def __init__(self, status_cb=None):
        self.status = status_cb or (lambda m: None)
        self.transactions = []
        self.rules_apriori = pd.DataFrame()
        self.rules_fp      = pd.DataFrame()
        self.pagerank_df   = pd.DataFrame()
        self.combined_df   = pd.DataFrame()
        self.co_watch      = defaultdict(lambda: defaultdict(int))
        self.pop_df        = pd.DataFrame()
        self.genre_df      = pd.DataFrame()
        self.top20_df      = pd.DataFrame()
        self.similarity_matrix = None
        self.movies_list   = []
        self._ready        = False

    # ── dataset ──────────────────────────────────────────────
    def _load_or_generate(self):
        csv = "movies_dataset.csv"
        if os.path.exists(csv):
            self.status("📂  Loading movies_dataset.csv …")
            dataset = pd.read_csv(csv, header=None)
        else:
            self.status("🎲  Generating synthetic watch-history dataset …")
            dataset = self._generate_dataset()

        dataset = dataset.replace('Avengers', 'The Avengers')
        self.transactions = []
        for i in range(len(dataset)):
            row = [str(dataset.values[i, j])
                   for j in range(dataset.shape[1])
                   if pd.notna(dataset.values[i, j]) and str(dataset.values[i, j]) != 'nan']
            if row:
                self.transactions.append(row)

    def _generate_dataset(self, n=7501, max_per_session=10):
        rng = np.random.default_rng(42)
        movies = ALL_MOVIES
        weights = rng.dirichlet(np.ones(len(movies)) * 0.5)
        rows = []
        for _ in range(n):
            k = rng.integers(2, max_per_session + 1)
            session = rng.choice(movies, size=k, replace=False, p=weights).tolist()
            session += [np.nan] * (max_per_session - len(session))
            rows.append(session)
        return pd.DataFrame(rows)

    # ── genre stats ──────────────────────────────────────────
    def _compute_genre(self):
        self.status("📊  Computing genre distribution …")
        counts = defaultdict(int)
        for session in self.transactions:
            for m in session:
                counts[GENRE_MAP.get(m, 'Other')] += 1
        self.genre_df = (pd.DataFrame(list(counts.items()), columns=['Genre','Count'])
                          .sort_values('Count', ascending=False))

    # ── top20 ────────────────────────────────────────────────
    def _compute_top20(self):
        self.status("📈  Computing top-20 movies …")
        all_m = [m for s in self.transactions for m in s]
        mc = Counter(all_m)
        self.top20_df = pd.DataFrame(mc.most_common(20), columns=['Movie','Count'])
        self.pop_df   = pd.DataFrame(list(mc.items()), columns=['Movie','Watch_Count'])

    # ── co-watch graph + PageRank ─────────────────────────────
    def _compute_pagerank(self):
        self.status("🔗  Building co-watch graph …")
        co = defaultdict(lambda: defaultdict(int))
        for session in self.transactions:
            unique = list(set(session))
            for a, b in combinations(unique, 2):
                co[a][b] += 1
                co[b][a] += 1
        self.co_watch = co

        G = nx.DiGraph()
        for a in co:
            for b, w in co[a].items():
                G.add_edge(a, b, weight=w)

        self.status("📐  Running PageRank …")
        pr = nx.pagerank(G, alpha=0.85, weight='weight')
        self.pagerank_df = (pd.DataFrame(list(pr.items()), columns=['Movie','PageRank'])
                             .sort_values('PageRank', ascending=False)
                             .reset_index(drop=True))

    # ── combined score ───────────────────────────────────────
    def _compute_combined(self):
        self.status("⚡  Computing combined score …")
        pop = self.pop_df.copy()
        pop['Watch_Count_Norm'] = pop['Watch_Count'] / pop['Watch_Count'].max()
        comb = self.pagerank_df.merge(pop, on='Movie')
        comb['PageRank_Norm'] = comb['PageRank'] / comb['PageRank'].max()
        comb['Combined_Score'] = 0.5*comb['PageRank_Norm'] + 0.5*comb['Watch_Count_Norm']
        self.combined_df = comb.sort_values('Combined_Score', ascending=False).reset_index(drop=True)

    # ── Apriori ──────────────────────────────────────────────
    def _compute_apriori(self):
        try:
            from apyori import apriori
            self.status("🔁  Running Apriori (fast mode) …")
            # higher min_support = much faster
            rules = list(apriori(self.transactions, min_support=0.01,
                                 min_confidence=0.2, min_lift=1.5, min_length=2))
            rows = []
            for item in rules:
                for stat in item[2]:
                    rows.append({
                        'LHS': ', '.join(stat[0]),
                        'RHS': ', '.join(stat[1]),
                        'Support':    round(item[1], 4),
                        'Confidence': round(stat[2], 4),
                        'Lift':       round(stat[3], 4),
                    })
            self.rules_apriori = pd.DataFrame(rows).sort_values('Lift', ascending=False)
        except ImportError:
            self.status("ℹ️  apyori not installed — skipping Apriori.")
            self.rules_apriori = pd.DataFrame()

    # ── FP-Growth ────────────────────────────────────────────
    def _compute_fpgrowth(self):
        try:
            from mlxtend.preprocessing import TransactionEncoder
            from mlxtend.frequent_patterns import fpgrowth, association_rules
            self.status("🌲  Running FP-Growth …")
            te = TransactionEncoder()
            arr = te.fit(self.transactions).transform(self.transactions)
            df_enc = pd.DataFrame(arr, columns=te.columns_)
            fi = fpgrowth(df_enc, min_support=0.01, use_colnames=True)
            rules = association_rules(fi, metric="lift", min_threshold=1)
            rules['LHS'] = rules['antecedents'].apply(lambda x: ', '.join(sorted(x)))
            rules['RHS'] = rules['consequents'].apply(lambda x: ', '.join(sorted(x)))
            self.rules_fp = (rules[['LHS','RHS','support','confidence','lift']]
                             .rename(columns={'support':'Support','confidence':'Confidence','lift':'Lift'})
                             .sort_values('Lift', ascending=False)
                             .reset_index(drop=True))
        except ImportError:
            self.status("ℹ️  mlxtend not installed — skipping FP-Growth.")
            self.rules_fp = pd.DataFrame()

    # ── Sentence-BERT similarity ─────────────────────────────
    def _compute_similarity(self):
        """Fast co-watch cosine similarity — no heavy models needed."""
        self.status("🧮  Computing movie similarity matrix …")
        movies = list(self.co_watch.keys())
        self.movies_list = movies
        n = len(movies)
        idx = {m: i for i, m in enumerate(movies)}
        mat = np.zeros((n, n))
        for a, nbrs in self.co_watch.items():
            for b, w in nbrs.items():
                if b in idx:
                    mat[idx[a]][idx[b]] = w
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1
        mat = mat / norms
        self.similarity_matrix = mat @ mat.T

    # ── main entry ───────────────────────────────────────────
    def run(self):
        steps = [
            ("📂  Loading dataset …",          self._load_or_generate),
            ("📊  Genre distribution …",        self._compute_genre),
            ("📈  Top-20 movies …",             self._compute_top20),
            ("🔗  PageRank …",                  self._compute_pagerank),
            ("⚡  Combined score …",            self._compute_combined),
            ("🔁  Apriori rules …",             self._compute_apriori),
            ("🌲  FP-Growth rules …",           self._compute_fpgrowth),
            ("🧮  Similarity matrix …",         self._compute_similarity),
        ]
        total = len(steps)
        for i, (msg, fn) in enumerate(steps, 1):
            self.status(f"[{i}/{total}]  {msg}")
            fn()
        self._ready = True
        self.status("✅  All models ready! — Select movies and click Get Recommendations")

    # ── recommendation ───────────────────────────────────────
    def recommend(self, watched: list, top_n=10):
        """
        Given a list of watched movies, return top_n recommendations.
        Strategy: average of co-watch scores + combined_score.
        """
        recs = defaultdict(float)

        # 1. co-watch signal
        for m in watched:
            for nb, w in self.co_watch.get(m, {}).items():
                if nb not in watched:
                    recs[nb] += w

        # 2. SBERT / fallback similarity signal
        if self.similarity_matrix is not None and self.movies_list:
            mi = {m: i for i, m in enumerate(self.movies_list)}
            for m in watched:
                if m in mi:
                    sims = self.similarity_matrix[mi[m]]
                    for i, score in enumerate(sims):
                        nb = self.movies_list[i]
                        if nb not in watched:
                            recs[nb] += score * 50   # scale to co-watch range

        # 3. normalize by combined popularity
        comb_lookup = dict(zip(self.combined_df['Movie'], self.combined_df['Combined_Score']))
        scored = {m: v * (1 + comb_lookup.get(m, 0)) for m, v in recs.items()}

        top = sorted(scored.items(), key=lambda x: -x[1])[:top_n]
        results = []
        for movie, score in top:
            results.append({
                'Movie': movie,
                'Genre': GENRE_MAP.get(movie, 'Other'),
                'Score': round(score, 2),
                'PageRank': round(self.pagerank_df.set_index('Movie')
                                   .get('PageRank', pd.Series()).get(movie, 0), 5),
            })
        return results


# ═══════════════════════════════════════════════════════════════
# GUI  APPLICATION
# ═══════════════════════════════════════════════════════════════
class MovieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎬  Movie Recommendation System")
        self.geometry("1280x820")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._loading = True   # flag

        self.engine = DataEngine(status_cb=self._set_status)
        self._build_ui()
        self._show_loading_overlay()
        self._start_loading()

    # ── loading overlay ──────────────────────────────────────
    def _show_loading_overlay(self):
        self._overlay = tk.Frame(self, bg="#000000")
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()

        inner = tk.Frame(self._overlay, bg=CARD, padx=40, pady=30)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="🎬", font=("Helvetica", 48), bg=CARD, fg=ACCENT).pack()
        tk.Label(inner, text="Movie Recommendation System",
                 font=("Helvetica", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=(0,4))
        tk.Label(inner, text="Loading models, please wait …",
                 font=("Helvetica", 12), bg=CARD, fg=TEXT_SUB).pack()

        self._ov_status = tk.StringVar(value="Starting …")
        tk.Label(inner, textvariable=self._ov_status,
                 font=("Helvetica", 11, "italic"), bg=CARD, fg=ACCENT2).pack(pady=(10,0))

        self._dot_lbl = tk.Label(inner, text="●  ○  ○", bg=CARD, fg=ACCENT,
                                 font=("Helvetica", 16))
        self._dot_lbl.pack(pady=(10,0))
        self._dot_state = 0
        self._animate_dots()

    def _animate_dots(self):
        patterns = ["●  ○  ○", "○  ●  ○", "○  ○  ●"]
        if hasattr(self, '_dot_lbl') and self._loading:
            self._dot_lbl.config(text=patterns[self._dot_state % 3])
            self._dot_state += 1
            self.after(400, self._animate_dots)

    def _hide_loading_overlay(self):
        self._loading = False
        if hasattr(self, '_overlay'):
            self._overlay.destroy()

    # ── status bar ───────────────────────────────────────────
    def _set_status(self, msg):
        def _update():
            self.status_var.set(msg)
            if hasattr(self, '_ov_status'):
                self._ov_status.set(msg)
        self.after(0, _update)

    # ── top-level layout ─────────────────────────────────────
    def _build_ui(self):
        # ── header ──
        hdr = tk.Frame(self, bg=ACCENT, height=54)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎬  Movie Recommendation System",
                 font=FONT_H1, bg=ACCENT, fg=TEXT).pack(side="left", padx=20, pady=10)

        # ── status bar ──
        self.status_var = tk.StringVar(value="⏳  Initializing …")
        sb = tk.Label(self, textvariable=self.status_var,
                      font=("Helvetica", 10), bg=CARD, fg=TEXT_SUB, anchor="w")
        sb.pack(fill="x", side="bottom", ipady=4, padx=4)

        # ── notebook (tabs) ──
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background=PANEL, foreground=TEXT_SUB,
                        font=FONT_BODY, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", TEXT)])

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        self._tab_recommend()
        self._tab_genre()
        self._tab_top20()
        self._tab_pagerank()
        self._tab_rules("Apriori Rules", "apriori")
        self._tab_rules("FP-Growth Rules", "fp")
        self._tab_cowatch()

    # ──────────────────────────────────────────────────────────
    # TAB 1 — RECOMMEND
    # ──────────────────────────────────────────────────────────
    def _tab_recommend(self):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="  🎯 Recommend  ")

        # left panel
        left = tk.Frame(f, bg=PANEL, width=340)
        left.pack(side="left", fill="y", padx=(8,4), pady=8)
        left.pack_propagate(False)
        left.grid_propagate(False)

        tk.Label(left, text="Select Movies You've Watched",
                 font=FONT_H2, bg=PANEL, fg=TEXT).pack(pady=(14,6), padx=10, anchor="w")
        tk.Label(left, text="(hold Ctrl / Cmd for multiple)",
                 font=("Helvetica", 9), bg=PANEL, fg=TEXT_SUB).pack(anchor="w", padx=12)

        # search box
        self.movie_search = tk.StringVar()
        self.movie_search.trace_add("write", self._filter_movies)
        srch = tk.Entry(left, textvariable=self.movie_search,
                        bg=CARD, fg=TEXT, insertbackground=TEXT,
                        font=FONT_BODY, relief="flat")
        srch.pack(fill="x", padx=10, pady=(6,2), ipady=6)

        # listbox
        lb_frame = tk.Frame(left, bg=PANEL)
        lb_frame.pack(fill="both", expand=True, padx=10, pady=4)
        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")
        self.movie_lb = tk.Listbox(lb_frame, selectmode="multiple",
                                   bg=CARD, fg=TEXT, selectbackground=ACCENT,
                                   font=FONT_BODY, relief="flat",
                                   yscrollcommand=sb.set, activestyle="none",
                                   highlightthickness=0)
        self.movie_lb.pack(fill="both", expand=True)
        sb.config(command=self.movie_lb.yview)
        self._all_movie_list = ALL_MOVIES
        for m in ALL_MOVIES:
            self.movie_lb.insert("end", m)

        # top-N slider
        ctrl = tk.Frame(left, bg=PANEL)
        ctrl.pack(fill="x", padx=10, pady=6)
        tk.Label(ctrl, text="Top-N recommendations:", bg=PANEL, fg=TEXT_SUB,
                 font=FONT_BODY).pack(anchor="w")
        self.topn_var = tk.IntVar(value=10)
        tk.Scale(ctrl, variable=self.topn_var, from_=3, to=20,
                 orient="horizontal", bg=PANEL, fg=TEXT, troughcolor=CARD,
                 highlightthickness=0, sliderrelief="flat",
                 activebackground=ACCENT).pack(fill="x")

        # button
        tk.Button(left, text="  Get Recommendations  ",
                  command=self._do_recommend,
                  bg=ACCENT, fg=TEXT, font=("Helvetica", 12, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground="#c1000e", activeforeground=TEXT
                  ).pack(fill="x", padx=10, pady=10, ipady=8)

        # right panel — results
        right = tk.Frame(f, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(4,8), pady=8)

        tk.Label(right, text="Recommendations", font=FONT_H2, bg=BG, fg=TEXT
                 ).pack(anchor="w", pady=(10,4), padx=4)

        cols = ("Movie","Genre","Score","PageRank")
        self.rec_tree = self._make_tree(right, cols)
        self.rec_tree.pack(fill="both", expand=True, padx=4)

        # insight label
        self.insight_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self.insight_var,
                 font=("Helvetica", 10, "italic"), bg=BG, fg=ACCENT2,
                 wraplength=700, justify="left").pack(anchor="w", padx=6, pady=6)

    def _filter_movies(self, *_):
        q = self.movie_search.get().lower()
        self.movie_lb.delete(0, "end")
        for m in self._all_movie_list:
            if q in m.lower():
                self.movie_lb.insert("end", m)

    def _do_recommend(self):
        if not self.engine._ready:
            self.status_var.set("⏳  Still loading — please wait a moment then try again …")
            return
        sel = [self.movie_lb.get(i) for i in self.movie_lb.curselection()]
        if not sel:
            messagebox.showwarning("No selection", "Please select at least one movie.")
            return
        recs = self.engine.recommend(sel, top_n=self.topn_var.get())
        self.rec_tree.delete(*self.rec_tree.get_children())
        for r in recs:
            self.rec_tree.insert("", "end",
                                 values=(r['Movie'], r['Genre'],
                                         f"{r['Score']:.2f}", f"{r['PageRank']:.5f}"))
        genres = [r['Genre'] for r in recs]
        top_genre = Counter(genres).most_common(1)[0][0] if genres else ""
        self.insight_var.set(
            f"💡  Based on {len(sel)} watched movie(s), top genre in recommendations: "
            f"{top_genre}.  Scores combine co-watch frequency, semantic similarity, "
            f"popularity, and PageRank."
        )

    # ──────────────────────────────────────────────────────────
    # TAB 2 — GENRE DISTRIBUTION
    # ──────────────────────────────────────────────────────────
    def _tab_genre(self):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="  📊 Genre Distribution  ")
        self.genre_frame = f
        tk.Label(f, text="⏳ Loading …", bg=BG, fg=TEXT_SUB, font=FONT_H2).pack(expand=True)

    def _draw_genre(self):
        for w in self.genre_frame.winfo_children():
            w.destroy()
        df = self.engine.genre_df
        colors = ['#e63946','#457b9d','#2a9d8f','#e9c46a','#f4a261','#264653','#8338ec']
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5),
                                 facecolor=PANEL)
        fig.suptitle('Movie Genre Distribution in Watch History',
                     fontsize=13, fontweight='bold', color=TEXT)
        for ax in axes:
            ax.set_facecolor(PANEL)

        axes[0].bar(df['Genre'], df['Count'], color=colors[:len(df)])
        axes[0].set_title('Genre Watch Count', color=TEXT)
        axes[0].set_xlabel('Genre', color=TEXT_SUB)
        axes[0].set_ylabel('Total Watches', color=TEXT_SUB)
        axes[0].tick_params(axis='x', rotation=25, colors=TEXT_SUB)
        axes[0].tick_params(axis='y', colors=TEXT_SUB)
        for sp in axes[0].spines.values():
            sp.set_edgecolor(CARD)

        axes[1].pie(df['Count'], labels=df['Genre'], autopct='%1.1f%%',
                    colors=colors[:len(df)], startangle=140,
                    textprops={'color': TEXT})
        axes[1].set_title('Genre Share (%)', color=TEXT)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.genre_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)

    # ──────────────────────────────────────────────────────────
    # TAB 3 — TOP 20 MOVIES
    # ──────────────────────────────────────────────────────────
    def _tab_top20(self):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="  🏆 Top 20 Movies  ")
        self.top20_frame = f
        tk.Label(f, text="⏳ Loading …", bg=BG, fg=TEXT_SUB, font=FONT_H2).pack(expand=True)

    def _draw_top20(self):
        for w in self.top20_frame.winfo_children():
            w.destroy()
        df = self.engine.top20_df
        fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=PANEL)
        ax.set_facecolor(PANEL)
        cmap_vals = [i/20 for i in range(20)]
        bars = ax.barh(df['Movie'][::-1], df['Count'][::-1],
                       color=plt.cm.viridis(cmap_vals))
        ax.set_title('Top 20 Most Watched Movies', fontsize=13,
                     fontweight='bold', color=TEXT)
        ax.set_xlabel('Watch Count', color=TEXT_SUB)
        ax.tick_params(colors=TEXT_SUB)
        for sp in ax.spines.values():
            sp.set_edgecolor(CARD)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.top20_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)

    # ──────────────────────────────────────────────────────────
    # TAB 4 — PAGERANK
    # ──────────────────────────────────────────────────────────
    def _tab_pagerank(self):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="  📐 PageRank  ")
        self.pr_frame = f
        tk.Label(f, text="⏳ Loading …", bg=BG, fg=TEXT_SUB, font=FONT_H2).pack(expand=True)

    def _draw_pagerank(self):
        for w in self.pr_frame.winfo_children():
            w.destroy()

        # split: chart left, table right
        left = tk.Frame(self.pr_frame, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(self.pr_frame, bg=BG, width=300)
        right.pack(side="right", fill="y", padx=(0,8), pady=8)
        right.pack_propagate(False)

        top_pr = self.engine.pagerank_df.head(20)
        fig, ax = plt.subplots(figsize=(8, 5.5), facecolor=PANEL)
        ax.set_facecolor(PANEL)
        colors_pr = plt.cm.plasma([i/20 for i in range(20)])
        ax.barh(top_pr['Movie'][::-1], top_pr['PageRank'][::-1], color=colors_pr[::-1])
        ax.set_title('Top 20 Movies by PageRank', fontsize=12, fontweight='bold', color=TEXT)
        ax.set_xlabel('PageRank Score', color=TEXT_SUB)
        ax.tick_params(colors=TEXT_SUB)
        for sp in ax.spines.values():
            sp.set_edgecolor(CARD)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=left)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)

        tk.Label(right, text="Combined Score Ranking",
                 font=FONT_H2, bg=BG, fg=TEXT).pack(pady=(10,4))
        cols = ("Movie","Score")
        tree = self._make_tree(right, cols)
        tree.pack(fill="both", expand=True)
        for _, row in self.engine.combined_df.head(20).iterrows():
            tree.insert("", "end",
                        values=(row['Movie'], f"{row['Combined_Score']:.4f}"))

    # ──────────────────────────────────────────────────────────
    # TAB 5 & 6 — RULES
    # ──────────────────────────────────────────────────────────
    def _tab_rules(self, label, key):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text=f"  🔁 {label}  ")
        if key == "apriori":
            self.apriori_frame = f
        else:
            self.fp_frame = f
        tk.Label(f, text="⏳ Loading …", bg=BG, fg=TEXT_SUB, font=FONT_H2).pack(expand=True)

    def _draw_rules(self, frame, df, title):
        for w in frame.winfo_children():
            w.destroy()
        tk.Label(frame, text=title, font=FONT_H2, bg=BG, fg=TEXT
                 ).pack(anchor="w", padx=10, pady=(10,4))
        if df.empty:
            tk.Label(frame, text="No rules found (install apyori / mlxtend and rerun).",
                     bg=BG, fg=TEXT_SUB, font=FONT_BODY).pack(expand=True)
            return

        # scatter
        fig, ax = plt.subplots(figsize=(8, 3.5), facecolor=PANEL)
        ax.set_facecolor(PANEL)
        sc = ax.scatter(df['Support'], df['Confidence'], c=df['Lift'],
                        cmap='viridis', alpha=0.7, edgecolors='k', linewidths=0.3)
        plt.colorbar(sc, ax=ax, label='Lift')
        ax.set_xlabel('Support', color=TEXT_SUB)
        ax.set_ylabel('Confidence', color=TEXT_SUB)
        ax.set_title(f'{title} ({len(df)} rules)', color=TEXT)
        ax.tick_params(colors=TEXT_SUB)
        for sp in ax.spines.values():
            sp.set_edgecolor(CARD)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=8)
        plt.close(fig)

        cols = ("LHS","RHS","Support","Confidence","Lift")
        tree = self._make_tree(frame, cols)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        for _, row in df.head(50).iterrows():
            tree.insert("", "end",
                        values=(row['LHS'], row['RHS'],
                                f"{row['Support']:.4f}",
                                f"{row['Confidence']:.4f}",
                                f"{row['Lift']:.4f}"))

    # ──────────────────────────────────────────────────────────
    # TAB 7 — CO-WATCH NETWORK
    # ──────────────────────────────────────────────────────────
    def _tab_cowatch(self):
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="  🌐 Co-Watch Network  ")
        self.cw_frame = f
        tk.Label(f, text="⏳ Loading …", bg=BG, fg=TEXT_SUB, font=FONT_H2).pack(expand=True)

    def _draw_cowatch(self):
        for w in self.cw_frame.winfo_children():
            w.destroy()

        co = self.engine.co_watch
        edge_list = []
        for a in co:
            for b, w in co[a].items():
                if a < b:
                    edge_list.append((a, b, w))
        edge_list.sort(key=lambda x: -x[2])
        top_edges = edge_list[:30]

        top_nodes = set()
        for a, b, _ in top_edges:
            top_nodes.add(a); top_nodes.add(b)
        top_nodes = sorted(top_nodes)
        n = len(top_nodes)
        angles = [2*math.pi*i/n for i in range(n)]
        pos = {nd: (math.cos(angles[i])*3, math.sin(angles[i])*3)
               for i, nd in enumerate(top_nodes)}

        fig, ax = plt.subplots(figsize=(10, 7), facecolor=PANEL)
        ax.set_facecolor(PANEL)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Frequent Movie Pair Co-Watch Network (Top 30 Pairs)',
                     fontsize=12, fontweight='bold', color=TEXT)

        max_w = max(w for _,_,w in top_edges)
        min_w = min(w for _,_,w in top_edges)
        for a, b, w in top_edges:
            x1,y1=pos[a]; x2,y2=pos[b]
            lw    = 0.5 + 3.5*(w-min_w)/(max_w-min_w+1)
            alpha = 0.3 + 0.6*(w-min_w)/(max_w-min_w+1)
            ax.plot([x1,x2],[y1,y2], color=BLUE, linewidth=lw, alpha=alpha, zorder=1)

        pr_lookup = dict(zip(self.engine.pagerank_df['Movie'], self.engine.pagerank_df['PageRank']))
        max_pr = self.engine.pagerank_df['PageRank'].max()
        for nd, (x,y) in pos.items():
            pr = pr_lookup.get(nd, 0)
            size = 150 + 900*(pr/max_pr)
            ax.scatter(x, y, s=size, c=ACCENT, zorder=3, edgecolors='white', linewidths=1.5)
            ax.annotate(nd, (x,y), textcoords='offset points',
                        xytext=(0,8), ha='center', fontsize=7, fontweight='bold', color=TEXT)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.cw_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)

    # ──────────────────────────────────────────────────────────
    # HELPER — themed Treeview
    # ──────────────────────────────────────────────────────────
    def _make_tree(self, parent, cols):
        style = ttk.Style()
        style.configure("Dark.Treeview",
                        background=CARD, foreground=TEXT, fieldbackground=CARD,
                        rowheight=26, font=FONT_BODY, borderwidth=0)
        style.configure("Dark.Treeview.Heading",
                        background=PANEL, foreground=ACCENT2, font=("Helvetica",10,"bold"))
        style.map("Dark.Treeview", background=[("selected", ACCENT)])

        frame = tk.Frame(parent, bg=BG)
        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Dark.Treeview",
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=160, anchor="w")
        return frame   # returns the wrapper frame; tree is inside

    # override to return actual tree widget
    def _make_tree(self, parent, cols):
        style = ttk.Style()
        style.configure("Dark.Treeview",
                        background=CARD, foreground=TEXT, fieldbackground=CARD,
                        rowheight=26, font=FONT_BODY)
        style.configure("Dark.Treeview.Heading",
                        background=PANEL, foreground=ACCENT2,
                        font=("Helvetica",10,"bold"))
        style.map("Dark.Treeview", background=[("selected", ACCENT)])

        vsb = ttk.Scrollbar(parent, orient="vertical")
        hsb = ttk.Scrollbar(parent, orient="horizontal")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                            style="Dark.Treeview",
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=160, anchor="w")
        return tree

    # ──────────────────────────────────────────────────────────
    # LOADING  (background thread)
    # ──────────────────────────────────────────────────────────
    def _start_loading(self):
        t = threading.Thread(target=self._load_worker, daemon=True)
        t.start()

    def _load_worker(self):
        self.engine.run()
        self.after(0, self._on_load_done)

    def _on_load_done(self):
        self._hide_loading_overlay()
        self._draw_genre()
        self._draw_top20()
        self._draw_pagerank()
        self._draw_rules(self.apriori_frame, self.engine.rules_apriori, "Apriori Rules")
        self._draw_rules(self.fp_frame,      self.engine.rules_fp,      "FP-Growth Rules")
        self._draw_cowatch()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()
