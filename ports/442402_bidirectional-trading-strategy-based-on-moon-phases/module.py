"""Lunar phase flips, 1-hour bars: the computed moon age crossing 15 days ("new moon" as labelled) goes long, the age wrapping back to 0 ("full moon" as labelled) goes short; each signal fires once per
phase; reversing.
Port of FMZ strategy #442402 "Bidirectional Trading Strategy Based on Moon Phases" ([astropark] Moon Phases [strategy]).

FMZ source id: 442402

Source
    https://www.fmz.com/strategy/442402 (PineScript v4, FMZ last modified 2024-02-21 16:15:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-274), strategy "buy on new moon, sell on full moon"; long and short on; from 2017 (start date)
    age = normalize((jd - 2451550.1) / 29.530588853) x 29.53 from year / month / day;  moon = floor(age)[1] > floor(age) ? 1 : floor(age)[1] < 15 and floor(age) >= 15 ? -1 : na
    longCond = moon == -1;  shortCond = moon == 1;  in-trade flags;  buySignal = longCond and not inLong[1] -> entry long, close short;  sellSignal = shortCond and not inShort[1] -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The moon age is computed from the bar's calendar date (UTC, the exchange time zone) as written, so
      the signals fall on the first bar of a day. pyramiding = 10, but each signal fires once per phase, so
      no position is added to. The start date is dropped like other date windows. strategy.entry reverses:
      REVERSAL INTENDED. The 100 % of equity size, capital and commission are sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, calendar moon-age flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: moon age from the UTC calendar date of the bar.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442402_moon_age_phase_flip_reversal"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "flip_day": [15, 7],
}
DEFAULT_PARAMS = {"flip_day": 15}


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


def _moon_age(index):
    t = index.tz_convert("UTC")
    year, month, day = t.year.to_numpy(), t.month.to_numpy(), t.day.to_numpy()
    y = year - np.floor((12 - month) / 10)
    m = month + 9
    m = np.where(m >= 12, m - 12, m)
    k1 = np.floor(365.25 * (y + 4712))
    k2 = np.floor(30.6 * m + 0.5)
    k3 = np.floor(np.floor((y / 100) + 49) * 0.75) - 38
    jd = k1 + k2 + day + 59
    jd = np.where(jd > 2299160, jd - k3, jd)
    x = (jd - 2451550.1) / 29.530588853
    x = x - np.floor(x)
    x = np.where(x < 0, x + 1, x)
    return x * 29.53


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    fa = np.floor(_moon_age(bars_df.index))
    fd = float(p["flip_day"])
    m = len(fa)
    moon = np.zeros(m, dtype=np.int8)
    for i in range(1, m):
        if fa[i - 1] > fa[i]:
            moon[i] = 1
        elif fa[i - 1] < fd and fa[i] >= fd:
            moon[i] = -1
    long_c, short_c = moon == -1, moon == 1
    tgt = np.zeros(m, dtype=np.int8)
    in_l = in_s = False
    held = 0
    for i in range(m):
        buy = long_c[i] and not in_l
        sell = short_c[i] and not in_s
        in_l = (long_c[i] or in_l) and not short_c[i]
        in_s = (short_c[i] or in_s) and not long_c[i]
        new = held
        if buy and new != 1:
            new = 1
        if sell and new != -1:
            new = -1
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
