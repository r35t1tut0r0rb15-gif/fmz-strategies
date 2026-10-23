"""Breaks of the EMA 34 bands of highs and lows, hourly bars: a bar opening under (or closing back over) the upper band and closing over it goes long, the mirror through the lower band goes short; each break reverses the other side.
Port of FMZ strategy #362022 "EMA bands leledc bollinger bands trend catching strategy" (Trend Pooristics (EMA bands + leledc + bollinger bands trend catching strategy)).

FMZ source id: 362022

Source
    https://www.fmz.com/strategy/362022 (PineScript v5, FMZ last modified 2022-05-09 16:48:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 131-819), EMA 34 of high / low / close; defaults: mid-band breakout long / short on, close on the opposite band, every other option off
    longMidBreak = (open < emaHigh and close > emaHigh) or (open > emaHigh and close > emaHigh and close[1] <= emaHigh[1]) -> entry Long
    shortMidBreak = (open > emaLow and close < emaLow) or (open < emaLow and close < emaLow and close[1] >= emaLow[1]) -> entry Short
    long held and shortMidBreak -> close Long ("Opposite band");  short held and longMidBreak -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the input defaults only the middle-band breakouts trade: the Leledc, Bollinger-exhaustion,
      bounce, default-position and counter-trend branches are off, so their code (and the optional volume
      filter of the Leledc bars, off by default) feeds no order and volume is not used. The opposite-band
      close is the other side's entry, which reverses the position first (the close then has nothing to
      act on, as #441963). The strategy() line is commented out in the source; FMZ runs it with its
      defaults. REVERSAL INTENDED. No sizing code. The source carries the Mozilla Public License 2.0
      notice. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA high / low band breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the commented strategy() line holds 100 % of equity).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG362022 (2 members, best partner #434180, Jaccard 0.976); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362022_ema34_high_low_band_break_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [34, 55],
    "use_slow_ema": [0, 1],
}
DEFAULT_PARAMS = {"ema_length": 34, "use_slow_ema": 0, "slow_ema_len": 200}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["ema_length"])
    eh = h.ewm(span=n, adjust=False).mean()
    el = lo.ewm(span=n, adjust=False).mean()
    up_break = ((o < eh) & (c > eh)) | ((o > eh) & (c > eh) & (c.shift(1) <= eh.shift(1)))
    dn_break = ((o > el) & (c < el)) | ((o < el) & (c < el) & (c.shift(1) >= el.shift(1)))
    if int(p["use_slow_ema"]):
        slow = c.ewm(span=int(p["slow_ema_len"]), adjust=False).mean()
        le = up_break & (c > slow) & (o < eh)
        se = dn_break & (c < slow) & (o > el)
    else:
        le, se = up_break, dn_break
    lx = dn_break & ~se                    # the opposite-band close (only when no short entry reverses)
    sx = up_break & ~le
    return le, lx & ~le, se, sx & ~se


def portfolio_kwargs(**params):
    return {}
