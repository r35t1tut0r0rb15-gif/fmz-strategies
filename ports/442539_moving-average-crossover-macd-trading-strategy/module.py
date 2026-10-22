"""MACD(12, 26, 9) crossings confirmed two bars later, 1-hour bars: a crossing over two bars ago with the MACD still above its signal goes long (after closing a short), a crossing under goes short; a
confirmed crossing against the side closes; no orders when the UTC day changed within the last two bars; reversing.
Port of FMZ strategy #442539 "Moving Average Crossover MACD Trading Strategy" (EMMA).

FMZ source id: 442539

Source
    https://www.fmz.com/strategy/442539 (PineScript v5, FMZ last modified 2024-02-22 16:25:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-213), MACD 12 / 26 / 9; confirmation 2 bars; minimum |delta| 0.08 (price units); earliest 20 Jan 2024; qty floor(equity / close)
    enterLong = crossover(macd, signal)[2] and macd > signal and abs(delta) >= 0.08;  exitLong = crossunder[2] and macd < signal;  shorts mirrored
    not (hour(time[2]) > hour(time)): exitLong -> close long, else enterLong -> close short, entry long;  exitShort -> close short, else enterShort -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0.08 delta floor is in price units: as a fraction of the close at the BTC reading of 42000,
      1.9e-6. hour() is read on the UTC bar time. The earliest-date window is dropped. Named entries
      in call order with one position at a time (a close acts only on the held id, as #442342). The
      quantity floor(equity / close) is sizing. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit delta floor -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: no orders when the UTC hour of the bar is below that of two bars before (a day change).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442539_macd_cross_two_bar_confirm_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "confirm": [2, 1],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"confirm": 2, "fast": 12, "slow": 26, "signal": 9, "delta_frac": 1.9e-06}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    k = int(p["confirm"])
    co = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).shift(k, fill_value=False)
    cu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).shift(k, fill_value=False)
    big = (macd - sig).abs() >= float(p["delta_frac"]) * c
    e_long = (co & (macd > sig) & big).to_numpy()
    x_long = (cu & (macd < sig)).to_numpy()
    e_short = (cu & (macd < sig) & big).to_numpy()
    x_short = (co & (macd > sig)).to_numpy()
    hour = pd.Series(bars_df.index.tz_convert("UTC").hour, index=c.index, dtype=float)
    ok = ~(hour.shift(k) > hour).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if ok[i]:
            if x_long[i]:
                if held == 1 and new == 1:
                    new = 0
            elif e_long[i]:
                if held == -1 and new == -1:
                    new = 0
                if new != 1:
                    new = 1
            if x_short[i]:
                if held == -1 and new == -1:
                    new = 0
            elif e_short[i]:
                if held == 1 and new == 1:
                    new = 0
                if new != -1:
                    new = -1
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
