"""Mobo Bands: the detrended price oscillator (DPO) breaking above its upper deviation band after
a break-down state goes long; breaking below its lower band after a break-out state goes short.
Port of FMZ strategy #362868 "Mobo Bands".

Source
    https://www.fmz.com/strategy/362868 (PineScript v4, FMZ last modified 2022-05-13 14:36:34).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 51-114), price hl2, DPO 13, Mobo 10, devs -0.8 / 0.8
    xsma = sma(price[int(13 / 2 + 1)], 13);  DPO = price - xsma
    Upper/Lower = sma(DPO, 10) +- 0.8 * stdev(DPO, 10)
    Signal1 = DPO > Upper and DPO[1] < Upper[1];  Signal2 = DPO < Lower and DPO[1] > Lower[1]
    wasUp := Signal1 ? 1 : Signal2 ? 0 : wasUp[1];  wasDn mirrors
    Signal1 and wasDn[1] -> entry long; else Signal2 and wasUp[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DPO lag int(dpo / 2 + 1) is 7 for dpo 13 (either integer or float division). stdev is
      the population deviation. moboDisplace (0) and the colour options are display only.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362868_mobo_band_break"
FAMILY = "bollinger_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dpo_len": [9, 13, 21],
    "mobo_len": [10, 20],
    "num_dev": [0.8, 1.2],
}
DEFAULT_PARAMS = {"dpo_len": 13, "mobo_len": 10, "num_dev": 0.8}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    price = (bars_df["high"] + bars_df["low"]) / 2
    n = int(p["dpo_len"])
    dpo = price - price.shift(int(n / 2 + 1)).rolling(n).mean()
    k = int(p["mobo_len"])
    mid, sd = dpo.rolling(k).mean(), dpo.rolling(k).std(ddof=0)
    upper, lower = mid + p["num_dev"] * sd, mid - p["num_dev"] * sd
    s1 = ((dpo > upper) & (dpo.shift(1) < upper.shift(1))).to_numpy()
    s2 = ((dpo < lower) & (dpo.shift(1) > lower.shift(1))).to_numpy()
    m = len(price)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    was_up = was_dn = 0
    for i in range(m):
        le[i], se[i] = s1[i] and was_dn == 1, s2[i] and was_up == 1
        was_up = 1 if s1[i] else (0 if s2[i] else was_up)
        was_dn = 1 if s2[i] else (0 if s1[i] else was_dn)
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
