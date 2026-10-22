"""Three SuperTrends (10 x 3, 14 x 2, 20 x 2.5), 1-hour bars: the close above all three as it crosses the first goes long, below all three as it crosses down short; close_all runs on every bar, so each
position is closed at the open after its fill bar unless reversed first.
Port of FMZ strategy #442809 "Threefold Overlapping SuperTrend Strategy" (Combined Supertrend Strategy - Ajit Prasad).

FMZ source id: 442809

Source
    https://www.fmz.com/strategy/442809 (PineScript v5, FMZ last modified 2024-02-26 10:04:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-187), SuperTrend 10 / 3, 14 / 2, 20 / 2.5; daily close (unused); market-time constants (unused); close_all every bar
    buy = close > st1, st2, st3 and close[1] <= st1[1] -> entry Buy;  sell = close < st1, st2, st3 and close[1] >= st1[1] -> entry Sell
    close < any st[1] -> close Buy;  close > any st[1] -> close Sell;  if true -> strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close-all block is gated by "if true", not by the 15:10 IST time its comment names, so every
      open position is closed at the end of its first bar (one-bar holds), as written; a reversing entry
      on that bar stands (a close written after a reversing entry leaves the reversal standing). The
      daily request and the time constants are unused. ta.supertrend follows Pine (direction -1 up).
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, triple SuperTrend agreement; one-bar holds as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the IST times are unused constants).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442809_triple_supertrend_cross_one_bar_hold"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor1": [3.0, 2.0],
    "atr1": [10, 20],
}
DEFAULT_PARAMS = {"factor1": 3.0, "atr1": 10, "factor2": 2.0, "atr2": 14, "factor3": 2.5, "atr3": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s = [pd.Series(_supertrend(h, lo, c, float(p[f"factor{k}"]), int(p[f"atr{k}"]))[0], index=c.index)
         for k in (1, 2, 3)]
    c1 = c.shift(1)
    buy = ((c > s[0]) & (c > s[1]) & (c > s[2]) & (c1 <= s[0].shift(1))).to_numpy()
    sell = ((c < s[0]) & (c < s[1]) & (c < s[2]) & (c1 >= s[0].shift(1))).to_numpy()
    xb = ((c < s[0].shift(1)) | (c < s[1].shift(1)) | (c < s[2].shift(1))).to_numpy()
    xs = ((c > s[0].shift(1)) | (c > s[1].shift(1)) | (c > s[2].shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if xb[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        if held != 0 and new == held:      # close_all on every bar
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
