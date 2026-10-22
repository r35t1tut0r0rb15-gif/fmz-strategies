"""Swing-low or bullish three-line-strike entries, bar size from the search, long only: a 12-bar low on this or the previous bar, or three red bars engulfed by a green one, goes long; a close 4 ATR(14)
above the latest signal close, or 2 ATR under it, closes.
Port of FMZ strategy #446552 "Intraday Bullish Breakout Strategy" (Intraday Bullish Script (LuxTradeVenture)).

FMZ source id: 446552

Source
    https://www.fmz.com/strategy/446552 (PineScript v5, FMZ last modified 2024-03-29 16:13:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-182), swing low 12; three-line strike; ATR 14, target 4 ATR, stop 2 ATR from the latest signal close; margins 100 / 100
    swingLow = low == lowest(low, 12) or low[1] == lowest(low, 12);  b3ls = three red bars then close > open[1];  signal -> entryLongPrice = close, entry Long
    close >= entryLongPrice + 4 atr -> close;  close <= entryLongPrice - 2 atr -> close  (bar-close tests, current ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. Every
      signal resets the reference price to its close, also while long, as written; the exits are
      bar-close tests against that price with the current bar's ATR, filled at the next open. The
      lele exhaustion counters are computed but never used. Long only. The margin settings are sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exits are close tests.
    2 generic: PASS, swing-low / three-line-strike entries with ATR close tests.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446552_swing_low_3line_strike_atr_close_tests_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_atr": [4.0, 2.0],
    "sl_atr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"tp_atr": 4.0, "sl_atr": 2.0, "atr_len": 14, "swing_len": 12}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    ll = lo.rolling(int(p["swing_len"])).min()
    swing = (lo == ll) | (lo.shift(1) == ll)
    b3 = (c.shift(3) < o.shift(3)) & (c.shift(2) < o.shift(2)) & (c.shift(1) < o.shift(1)) & (c > o.shift(1))
    sig = (swing | b3).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp, sl = float(p["tp_atr"]), float(p["sl_atr"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, ref = False, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if sig[i]:
                ref = cv[i]
                if not held:
                    le[i] = True
            if held and (cv[i] >= ref + tp * atr[i] or cv[i] <= ref - sl * atr[i]):
                lx[i] = True
            held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
