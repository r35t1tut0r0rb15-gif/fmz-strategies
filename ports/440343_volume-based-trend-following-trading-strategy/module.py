"""Hourly bars, long only: a volume ratio (34-bar volume against the 200-bar volume per 34-bar block) at a 21-bar high or crossing over 1, with the close above the close 13 bars ago, starts a long state and goes long; a 13-bar low of the ratio, or the same volume surge with the close below the close 13 bars ago, ends it and closes; a crossing over 1.2 with the close below that close also closes.
Port of FMZ strategy #440343 "Volume based Trend Following Trading Strategy" (Volume Advanced).

FMZ source id: 440343

Source
    https://www.fmz.com/strategy/440343 (PineScript v4, FMZ last modified 2024-01-29 15:04:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 124-178), volume length 34, smoothing 200, rising 21, falling 13; thresholds 1 / 1.2; direction 13 bars
    volsum = sum(volume, 34) / (sum(volume, 200) / (200 / 34));  LongEntry = (rising(volsum, 21) or crossover(volsum, 1)) and close > close[13];  ShortEntry likewise with close < close[13]
    state 0 -> 1 on LongEntry, -> 2 on ShortEntry;  1 -> 0 on ShortEntry or falling(volsum, 13);  2 -> 0 on LongEntry or falling;  state 1 and close > close[13] -> entry BUY;  state 0 or LongExit2 -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * v4 int / int: 200 / 34 = 5, so the ratio is 5 x sum(34) / sum(200) (weird case: about 0.85 on flat
      volume). rising / falling compare with every one of the previous n values. The short state only
      blocks new longs; nothing is sold short. 100 % of equity and the commission are sizing and costs.
      The date window is dropped. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-surge state machine with a 13-bar trend test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the ratio of the 34-bar and 200-bar volume sums; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440343_volume_ratio_surge_state_close13_1h_long_only"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_length": [34, 20],
    "direction": [13, 26],
}
DEFAULT_PARAMS = {"vol_length": 34, "vol_smooth": 200, "rise_len": 21, "fall_len": 13, "threshold": 1.0,
                  "threshold2": 1.2, "direction": 13}


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
    vl, vs = int(p["vol_length"]), int(p["vol_smooth"])
    s200 = v.rolling(vs).sum() / (vs // vl)
    vsum = v.rolling(vl).sum() / s200.where(s200 != 0)
    rl, fl = int(p["rise_len"]), int(p["fall_len"])
    rising = vsum > vsum.shift(1).rolling(rl).max()
    falling = vsum < vsum.shift(1).rolling(fl).min()
    t1, t2 = float(p["threshold"]), float(p["threshold2"])
    x1 = (vsum > t1) & (vsum.shift(1) <= t1)
    x2 = (vsum > t2) & (vsum.shift(1) <= t2)
    d = int(p["direction"])
    up, dn = c > c.shift(d), c < c.shift(d)
    surge = rising | x1
    long_e = (surge & up).to_numpy()
    short_e = (surge & dn).to_numpy()
    fall = falling.to_numpy()
    exit2 = (x2 & dn).to_numpy()
    upv = up.to_numpy()
    m = len(long_e)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state, pos = 0, 0
    for i in range(m):
        prev = state
        if prev == 0:
            if long_e[i]:
                state = 1
            if short_e[i]:
                state = 2
        elif prev == 1:
            if short_e[i] or fall[i]:
                state = 0
        elif prev == 2:
            if long_e[i] or fall[i]:
                state = 0
        if pos == 1 and (state == 0 or exit2[i]):
            lx[i], pos = True, 0
        elif pos == 0 and state == 1 and upv[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
