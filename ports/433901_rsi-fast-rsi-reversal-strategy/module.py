"""Noro's fast RSI fades, 1-hour bars: a sizeable red candle with the RSI 3 under 25 goes long, a sizeable green candle with
the RSI 3 over 75 goes short; a long is closed by a sizeable candle with the RSI 3 back above 25, a short by one with
the RSI 3 back under 75.
Port of FMZ strategy #433901 "快速RSI反转策略Fast-RSI-Reversal-Strategy" (Noro's Fast RSI Strategy v1.0).

FMZ source id: 433901

Source
    https://www.fmz.com/strategy/433901 (PineScript v3, FMZ last modified 2023-12-01 13:37:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 174-210), RSI 3 (rma), limit 25; body filter ema(body, 30) / 2; pyramiding 5
    up = red and fastrsi < 25 and body > ema(body, 30) / 2 -> entry long;  dn = green and fastrsi > 75 and the body test -> entry short
    exit = (long and fastrsi > 25 or short and fastrsi < 75) and body > ema(body, 30) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 5 adds units on repeated signals; stacking is sizing (SURVEY_README, as #426588), so
      the net position is ported.
    * Each bar: the exit acts on the position held at the start of the bar, then an entry wins (an
      entry against the position reverses it). REVERSAL INTENDED. The date window is open. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and pyramiding 5 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG433901 (2 members, best partner #434178, Jaccard 0.836); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433901_noro_fast_rsi_fade"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [25, 15],
    "rsi_len": [3, 5],
}
DEFAULT_PARAMS = {"limit": 25, "rsi_len": 3, "body_len": 30}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = ((100 - 100 / (1 + up_ / dn_)).where(up_ != 0, 0.0).where(dn_ != 0, 100.0).where(up_.notna())).to_numpy()
    body = (c - o).abs()
    big = (body > body.ewm(span=int(p["body_len"]), adjust=False).mean() / 2).to_numpy()
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    lo_l, hi_l = float(p["limit"]), 100 - float(p["limit"])
    with np.errstate(invalid="ignore"):
        up = red & (r < lo_l) & big
        dn = green & (r > hi_l) & big
        xl = (r > lo_l) & big
        xs = (r < hi_l) & big
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if (pos == 1 and xl[i]) or (pos == -1 and xs[i]):
            pos = 0
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
