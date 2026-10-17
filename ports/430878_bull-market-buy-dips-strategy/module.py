"""Coinrule dip buyer, 1-hour bars, long only: RSI 14 under 35 while the SMA 200 is below the SMA 50 goes long; a close above
the SMA 9 with the SMA 9 above the SMA 50 closes the long.
Port of FMZ strategy #430878 "Bull Market Buy Dips Strategy" (Buy The Dips in Bull Market (by Coinrule)).

FMZ source id: 430878

Source
    https://www.fmz.com/strategy/430878 (PineScript v4, FMZ last modified 2023-11-02 16:21:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-201), RSI 14 / 35, SMA 9 / 50 / 200
    entry long when RSI < 35 and sma(200) < sma(50) and window()
    close long when close > sma(9) and sma(9) > sma(50) and window()

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date window (from 10 Jan 2020) is the author's: dropped. The close is written after the
      entry: a bar that meets both ends flat when already long, long when flat (the close acts on
      the position held at the bar's start). Long only; Opposite entries cannot occur. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level and SMA comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 30 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430878_bull_dip_rsi_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "rsi_buy": [35, 25],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_buy": 35, "fast": 9, "slow": 50, "long_len": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fast = c.rolling(int(p["fast"])).mean()
    slow = c.rolling(int(p["slow"])).mean()
    lng = c.rolling(int(p["long_len"])).mean()
    buy = ((_rsi(c, int(p["rsi_len"])) < p["rsi_buy"]) & (lng < slow)).to_numpy()
    out = ((c > fast) & (fast > slow)).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if start == 1 and out[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
