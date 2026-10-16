"""Buy the dip in an up-move (Coinrule), 4-hour bars, long only: a 24-bar rise over 3 % with a 2-bar drop of more than
1 % goes long; a close 3 % under the entry price, or 4 % above it, closes the long.
Port of FMZ strategy #430383 "Multi Timeframe Buy the Dip Strategy" (Multi Time Frame Buy the Dips (by Coinrule)).

FMZ source id: 430383

Source
    https://www.fmz.com/strategy/430383 (PineScript v1, FMZ last modified 2023-10-27 16:56:23).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 275-318), look-backs 24 / 2, increase 3 %, dip -1 %, stop 3 %, target 4 %
    overall = % change over 24 bars; overall_2 = % change over 2 bars
    overall > 3 and overall_2 < -1 -> entry long
    close < avg x 0.97 or close > avg x 1.04 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are tested on bar closes with strategy.close (market exits at the next
      open): exit signals, not stop orders, from the average price = the fill (the next open after the
      signal). A further signal while long adds nothing (pyramiding 0).
    * window() is always true. Long only; Opposite entries cannot occur. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, percentage changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 30 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430383 (3 members, best partner #436600, Jaccard 0.817); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430383_coinrule_buy_the_dip_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lkb_long": [24, 48],
    "stop_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"lkb_long": 24, "lkb_short": 2, "increase": 3.0, "dip": 1.0, "stop_pct": 3.0, "tp_pct": 4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    a, b = int(p["lkb_long"]), int(p["lkb_short"])
    overall = (c - c.shift(a)) / c.shift(a) * 100
    overall2 = (c - c.shift(b)) / c.shift(b) * 100
    sig = ((overall > p["increase"]) & (overall2 < -p["dip"])).to_numpy()
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    sl, tp = float(p["stop_pct"]) / 100, float(p["tp_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, pending = 0, np.nan, False
    for i in range(m):
        if pending:                                  # the entry fills at this bar's open
            avg, pending = ov[i], False
        if pos == 1 and (cv[i] < avg * (1 - sl) or cv[i] > avg * (1 + tp)):
            pos, avg = 0, np.nan
        elif pos == 0 and sig[i]:
            pos, pending = 1, True
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
