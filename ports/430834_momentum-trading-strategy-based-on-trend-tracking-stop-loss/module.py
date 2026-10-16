"""Supertrend momentum, 1-hour bars, long only: the close above a fast supertrend (factor 5, ATR 1) with RSI 14 above 60
goes long; the close under the supertrend closes it.
Port of FMZ strategy #430834 "Momentum Trading Strategy Based on Trend Tracking Stop Loss" (Momentum Trading Strategy (Weekly Chart)).

FMZ source id: 430834

Source
    https://www.fmz.com/strategy/430834 (PineScript v4, FMZ last modified 2023-11-02 13:59:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-241), supertrend(5, 1), RSI 14 > 60
    [st, dir] = supertrend(5, 1); close > st and rsi(close, 14) > 60 -> entry long;  close < st -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * supertrend(factor 5, ATR period 1) as Pine's ta.supertrend (ATR 1 is the bar's true range).
      The title's weekly chart is the author's suggestion; the header period (1h) is used.
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR band and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430834_supertrend_rsi_momentum_long"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [5.0, 3.0],
    "rsi_level": [60, 55],
}
DEFAULT_PARAMS = {"factor": 5.0, "atr_period": 1, "rsi_len": 14, "rsi_level": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _supertrend(bars, factor, atr_period):
    """ta.supertrend(factor, atrPeriod) as in Pine: returns (supertrend, direction); direction < 0 is an up-trend."""
    atr = _atr(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    st, dirn = np.full(m, np.nan), np.full(m, np.nan)
    lower_prev = upper_prev = 0.0
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st[i] = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
        st_prev = st[i]
    return pd.Series(st, index=bars.index), pd.Series(dirn, index=bars.index)


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st, _ = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))
    long_e = ((c > st) & (_rsi(c, int(p["rsi_len"])) > p["rsi_level"])).astype(bool)
    long_x = (c < st).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
