"""Heikin-Ashi trend: EMA of HA close vs EMA of HA open, each smoothed again; long while the
close side is at or above the open side, short otherwise (always in).
Port of FMZ strategy #362000 "Heikin-Ashi-Trend".

Source
    https://www.fmz.com/strategy/362000 (PineScript v5, FMZ last modified 2022-05-09 14:33:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 57-79), EMA 77, smoothing 21
    ha_open/ha_close = request.security(ticker.heikinashi(...), timeframe.period, ema(open/close,77))
    trend = ema(ha_close_ema, 21) >= ema(ha_open_ema, 21)
    trend -> entry long, else -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi series are built from the port's bars: ha_close = (o+h+l+c)/4,
      ha_open = (ha_open[1] + ha_close[1])/2 seeded with (o+c)/2. Same timeframe, no lookahead.
    * strategy.entry every bar in the current direction; a change reverses: REVERSAL INTENDED
      (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362000_heikin_ashi_ema_trend"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [50, 77, 100],
    "smooth": [10, 21, 30],
}
DEFAULT_PARAMS = {"ema_len": 77, "smooth": 21}


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


def _heikin_ashi(bars):
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    ha_c = (o + h + lo + c) / 4
    ha_o = np.empty(len(o))
    for i in range(len(o)):
        ha_o[i] = (o[i] + c[i]) / 2 if i == 0 else (ha_o[i - 1] + ha_c[i - 1]) / 2
    return pd.Series(ha_o, index=bars.index), pd.Series(ha_c, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ha_o, ha_c = _heikin_ashi(bars_df)
    n, s = int(p["ema_len"]), int(p["smooth"])
    so = ha_o.ewm(span=n, adjust=False).mean().ewm(span=s, adjust=False).mean().to_numpy()
    sc = ha_c.ewm(span=n, adjust=False).mean().ewm(span=s, adjust=False).mean().to_numpy()
    warm = np.arange(len(so)) >= n
    return _always_in(warm & (sc >= so), warm & (sc < so), bars_df.index)


def portfolio_kwargs(**params):
    return {}
