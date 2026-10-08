"""Simple EMA 20: a bar wholly above a rising EMA 20 (EMA above its value 20 bars ago) with
stochastic %K above %D goes long; a close below the EMA closes it. Long only.
Port of FMZ strategy #426136 "Simple EMA20 Strat".

Source
    https://www.fmz.com/strategy/426136 (PineScript v5, FMZ last modified 2023-09-08 15:56:24).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 62-75), stoch 14 / 1 / 3, EMA 20
    low > ema and k > d and ema > ema[20] -> entry long;  close < ema -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only, as written (rule 6): opposite entries cannot occur;
      portfolio_kwargs returns upon_opposite_entry="ignore".
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426136_ema20_stoch_long_only"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [10, 20, 50],
    "period_k": [9, 14],
}
DEFAULT_PARAMS = {"ema_len": 20, "period_k": 14, "smooth_k": 1, "period_d": 3}


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
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["period_k"])
    st = 100 * (c - l.rolling(n).min()) / (h.rolling(n).max() - l.rolling(n).min())
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = ((l > ema) & (k > d) & (ema > ema.shift(20))).to_numpy()
    lx = (c < ema).to_numpy()
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
