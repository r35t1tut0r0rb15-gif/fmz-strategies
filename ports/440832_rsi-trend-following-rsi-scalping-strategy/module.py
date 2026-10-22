"""RSI momentum longs, 3-hour bars, long only: the RSI 14 above 70 goes long; the RSI under 55, or a close 6 % above the entry, closes.
Port of FMZ strategy #440832 "基于RSI的追踪趋势策略Trend-Following-RSI-Scalping-Strategy" (Trend-following RSI Scalping Strategy (by Coinrule)).

FMZ source id: 440832

Source
    https://www.fmz.com/strategy/440832 (PineScript v1, FMZ last modified 2024-02-02 14:54:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-149), RSI 14; entry above 70; exit under 55 or take profit 6 %; 30 % of equity; dates 2020-2112 (window() is true)
    RSI > 70 -> entry long;  RSI < 55 or close > avg price x 1.06 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit is a close test against the fill price, sent at the next open (not an order).
      Pine's and/or precedence reads "RSI < 55 or (close > target and window)". The entry is a level; an
      entry while long does nothing. Long only. The 30 % of equity size, capital and commission are
      sizing and costs. FREQ = "3h" from the backtest header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested target.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity, capital and commission settings.
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

NAME = "fmz_440832_rsi70_momentum_long_close_target"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "take_profit": [6, 3],
    "exit_rsi": [55, 50],
}
DEFAULT_PARAMS = {"take_profit": 6, "exit_rsi": 55, "entry_rsi": 70, "length": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    buy = (r > float(p["entry_rsi"])).to_numpy()
    xr = (r < float(p["exit_rsi"])).to_numpy()
    tp = float(p["take_profit"]) / 100
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, x = 0, np.nan
    for i in range(m):
        new = 1 if buy[i] else pos
        if pos == 1 and new == 1 and (xr[i] or cv[i] > x * (1 + tp)):
            new = 0
        if new == 1 and pos != 1 and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new long
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
