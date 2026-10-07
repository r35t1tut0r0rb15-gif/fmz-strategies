"""Fukuiz Octa-EMA + Ichimoku: EMA11 above EMA34 with their average above both displaced cloud
lines goes long; EMA11 below EMA34 goes short (always in).
Port of FMZ strategy #363588 "Fukuiz Octa-EMA + Ichimoku".

Source
    https://www.fmz.com/strategy/363588 (PineScript v5, FMZ last modified 2022-05-16 18:21:00).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 86-192), EMA2 11, EMA8 34, Ichimoku 9 / 26 / 52 / 26
    SenkouA = donchian_mid(52) [displacement];  SenkouB = (Tenkan[26] + Kijun[26]) / 2
    fukuiz = avg(ema2, ema8)
    buy2 = ema2 > ema8 and fukuiz > SenkouA[26] and fukuiz > SenkouB -> entry long
    else sell2 = ema2 < ema8 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The author's names are swapped against the usual Ichimoku (SenkouA is the 52-bar midline),
      kept as coded; both lines are past values (no forward plot offset reaches the rule).
    * The other six ribbon EMAs and the buy/sell (barssince) conditions only draw.
    * The start/end date inputs are a backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363588_octa_ema_ichimoku"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [8, 11],
    "ema_slow": [34, 55],
    "displacement": [26, 52],
}
DEFAULT_PARAMS = {"ema_fast": 11, "ema_slow": 34, "tenkan": 9, "kijun": 26, "span_b": 52, "displacement": 26}


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
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = lambda n: (h.rolling(int(n)).max() + l.rolling(int(n)).min()) / 2
    k, d = int(p["kijun"]), int(p["displacement"])
    senkou_a = mid(p["span_b"]).shift(d)
    senkou_b = (mid(p["tenkan"]).shift(k) + mid(k).shift(k)) / 2
    e2 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    e8 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    fk = (e2 + e8) / 2
    buy = ((e2 > e8) & (fk > senkou_a) & (fk > senkou_b)).to_numpy()
    sell = (e2 < e8).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
