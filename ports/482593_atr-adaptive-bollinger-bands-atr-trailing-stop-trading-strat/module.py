"""Closes crossing back above the lower Bollinger band (20, 2) go long, crossing back below the upper band go short;
a ratcheting 3 ATR close-based trail ends a trade when the close crosses it, hourly bars.
Port of FMZ strategy #482593 "自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy" (ATR Trailing Stop Loss with Bollinger Bands).

FMZ source id: 482593

Source
    https://www.fmz.com/strategy/482593 (PineScript v5, FMZ last modified 2025-02-19 11:00:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 88-137), BB 20 / 2, ATR 14 x 3
    while long: long_stop = max(close - 3 ATR, long_stop[1]) (na while not long); short mirrored with min
    crossover(close, lower) -> entry long; crossunder(close, upper) -> entry short
    crossunder(close, long_stop) -> close long; crossover(close, short_stop) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is computed and tested on closes with strategy.close: a close-based exit signal at the next open
      (rule 3; an author's trail checked on bar closes keeps no mark). It exists from the first bar the position is
      held (the fill bar); its first bar cannot cross (the previous value is na).
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a close-based trail.
    2 generic: PASS, Bollinger bands and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482593_bb_reentry_close_atr_trail"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [3.0, 2.0],
    "bb_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "atr_len": 14, "atr_mult": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    buy = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    sell = ((c < upper) & (c.shift(1) >= upper.shift(1))).to_numpy()
    k_atr = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = 0                       # strategy.position_size sign at this bar (fills at its open)
    nxt = 0                        # position after this bar's orders
    ls = ss = np.nan
    for i in range(m):
        held = nxt
        prev_ls, prev_ss = ls, ss
        if held == 1:
            v = cv[i] - k_atr[i]
            ls = max(v, prev_ls) if not np.isnan(prev_ls) else v
        else:
            ls = np.nan
        if held == -1:
            v = cv[i] + k_atr[i]
            ss = min(v, prev_ss) if not np.isnan(prev_ss) else v
        else:
            ss = np.nan
        x_long = i > 0 and not np.isnan(ls) and not np.isnan(prev_ls) and cv[i] < ls and cv[i - 1] >= prev_ls
        x_short = i > 0 and not np.isnan(ss) and not np.isnan(prev_ss) and cv[i] > ss and cv[i - 1] <= prev_ss
        tgt = held
        if buy[i] and tgt != 1:
            le[i], tgt = True, 1
        if sell[i] and tgt != -1:
            se[i], tgt = True, -1
        if x_long and held == 1 and tgt == 1:
            lx[i], tgt = True, 0
        if x_short and held == -1 and tgt == -1:
            sx[i], tgt = True, 0
        nxt = tgt
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
