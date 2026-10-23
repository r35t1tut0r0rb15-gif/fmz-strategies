"""EMA 9 / 21 crossings confirmed by volume (0.85 x volume over the previous 5 bars' average), the close on the EMA 9 side and a four-close reversal pattern, 2-hour bars: confirmed up-crossings go long, confirmed down-crossings go short; reversing.
Port of FMZ strategy #361966 "Buy Sell Strat" (Buy/Sell Strat).

FMZ source id: 361966

Source
    https://www.fmz.com/strategy/361966 (PineScript v5, FMZ last modified 2022-05-09 11:24:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 38-88), EMA 9 / 21; volume average of bars 1-5; pattern close > close[1] > close[2] < close[3] < close
    crossover(ema9, ema21) and volume x 0.85 > avg(volume[1..5]) and close > ema9 and up pattern -> entry long;  mirror -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern needs close > close[1] > close[2], close[3] > close[2] and close > close[3] (mirror for
      shorts), as written. Entries only (the exits are commented out); each reverses the other side.
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with volume and pattern confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG361966 (2 members, best partner #433566, Jaccard 0.846); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume x 0.85 > the mean of the previous 5 bars; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361966_ema9_21_cross_volume_surge_four_close_pattern_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_factor": [0.85, 0.6],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"vol_factor": 0.85, "slow": 21, "fast": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    vavg = v.shift(1).rolling(5).mean()
    loud = v * float(p["vol_factor"]) > vavg
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    up_pat = (c > c1) & (c1 > c2) & (c3 > c2) & (c > c3)
    dn_pat = (c < c1) & (c1 < c2) & (c3 < c2) & (c < c3)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & loud & (c > a) & up_pat
    se = (a < b) & (a.shift(1) >= b.shift(1)) & loud & (c < a) & dn_pat
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
