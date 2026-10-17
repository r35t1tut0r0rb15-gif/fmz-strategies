"""UT Bot ATR trailing line, long only, 3-hour bars: the close crossing above the ATR(10) x 1 trailing line goes long;
the line crossing above the close closes the long.
Port of FMZ strategy #489301 "量化多空趋势追踪动态止损策略-Quantitative-Long-Short-Trend-Tracking-Dynamic-Stop-Loss-Strategy" (ducanhmaster v1).

FMZ source id: 489301

Source
    https://www.fmz.com/strategy/489301 (PineScript v6, FMZ last modified 2025-04-03 11:34:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 145-203), key 1, ATR 10, Heikin-Ashi off
    trail = the UT Bot ratchet of src -+ 1 x ATR(10) (nz(trail[1], 0) at the start);  ema = EMA 1 of src = src
    buy = src > trail and crossover(src, trail) -> entry long;  sell = src < trail and crossover(trail, src) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is an indicator on bar closes (no stop order): the exits are close-based signals.
    * The source's Heikin-Ashi switch uses a simplified candle (HA close = (o + h + l + c) / 4), kept as a variant.
    * The commission and slippage in strategy() are costs (not in the module). Long only. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR-scaled line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489301_utbot_atr_line_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1, 2],
    "heikin": [False, True],
}
DEFAULT_PARAMS = {"key": 1, "atr_len": 10, "heikin": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _ut_trail(sr, nloss):
    m = len(sr)
    out = np.full(m, np.nan)
    prev = 0.0                              # nz(trail[1], 0)
    for i in range(m):
        s, nl = sr[i], nloss[i]
        if np.isnan(s) or np.isnan(nl):     # na in Pine; nz() reads it as 0 on the next bar
            prev = 0.0
            continue
        s1 = sr[i - 1] if i > 0 else np.nan
        if s > prev and (not np.isnan(s1)) and s1 > prev:
            t = max(prev, s - nl)
        elif s < prev and (not np.isnan(s1)) and s1 < prev:
            t = min(prev, s + nl)
        else:
            t = s - nl if s > prev else s + nl
        out[i] = t
        prev = t
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4 if p["heikin"] else c
    nloss = p["key"] * _atr(bars_df, int(p["atr_len"]))
    trail = pd.Series(_ut_trail(src.to_numpy(dtype=float), nloss.to_numpy(dtype=float)), index=c.index)
    t_prev = trail.shift(1).fillna(0.0)                 # nz(trail[1], 0) in the crosses
    above = (src > trail) & (src.shift(1) <= t_prev)
    below = (trail > src) & (t_prev <= src.shift(1))
    buy = (above & (src > trail)).astype(bool)
    sell = (below & (src < trail)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
