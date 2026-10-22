"""RSI 14 of the lows under 24, no bar size in the source, long only: the RSI of the lows under 24 buys; an RSI over 72, or a close 20 % under the low of the latest signal bar, sells.
Port of FMZ strategy #458023 "基于RSI的低价动态入场与止损策略-Dynamic-Low-Price-Entry-and-Stop-Loss-Strategy-Based-on-RSI" (Simple RSI Strategy with Low as Source).

FMZ source id: 458023

Source
    https://www.fmz.com/strategy/458023 (PineScript v5, FMZ last modified 2024-07-29 13:22:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 153-187), RSI 14 of low; entry 24, exit 72; max loss 20 % from the latest signal bar's low
    rsi(low) < 24 -> entry Long, entryPrice = low;  rsi > 72 or (close - entryPrice) / entryPrice <= -20 % -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a state (repeats ignored while long), and every signal bar resets the reference to
      its low, also inside a trade, as written; the loss exit is a bar-close test filled at the next
      open. The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule
      1); precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size.
      Long only. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the loss exit is a close test.
    2 generic: PASS, RSI-of-lows dips.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458023_rsi_of_lows_dip_loss_test_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "entry_lvl": [24, 30],
    "exit_lvl": [72, 60],
}
DEFAULT_PARAMS = {"rsi_len": 14, "entry_lvl": 24.0, "exit_lvl": 72.0, "max_loss": 20.0}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    r = _rsi(lo, int(p["rsi_len"]))
    go = (r < float(p["entry_lvl"])).to_numpy()
    out = (r > float(p["exit_lvl"])).to_numpy()
    lv, cv = lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ml = float(p["max_loss"])
    m = len(cv)
    lx = np.zeros(m, dtype=bool)
    ref = np.nan
    for i in range(m):
        if go[i]:
            ref = lv[i]
        loss = not np.isnan(ref) and 100 * (cv[i] - ref) / ref <= -ml
        lx[i] = out[i] or loss
    ix = bars_df.index
    le = pd.Series(go, index=ix)
    false = pd.Series(False, index=ix)
    return le, pd.Series(lx, index=ix) & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
