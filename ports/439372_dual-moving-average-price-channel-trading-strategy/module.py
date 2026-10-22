"""G-Channel trend with EMA 20 pullbacks, 1-minute bars: while the last G-Channel cross is bullish, a close under the EMA 20 goes long; while bearish, a close over the EMA goes short; reversing; the entry is
sent on every bar of the state.
Port of FMZ strategy #439372 "Dual Moving Average Price Channel Trading Strategy" (G-Channel and EMA Strategy).

FMZ source id: 439372

Source
    https://www.fmz.com/strategy/439372 (PineScript v4, FMZ last modified 2024-01-19 16:44:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 191-224), G-Channel length 100; EMA 20
    a = max(close, a[1]) - (a[1] - b[1]) / 100;  b = min(close, b[1]) + (a[1] - b[1]) / 100 (both start at the close)
    crossup = b[1] < close[1] and b > close;  crossdn = a[1] < close[1] and a > close;  bullish = barssince(crossdn) <= barssince(crossup)
    buy = bullish and close < ema 20 -> entry Buy;  sell = not bullish and close > ema 20 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince is undefined until its condition has happened once; a comparison with it is then false,
      so the state reads as not bullish, as written. A same-side entry while in the position is
      ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel crossings and an EMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439372_g_channel_trend_ema20_pullback"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "ema_length": [20, 50],
}
DEFAULT_PARAMS = {"length": 100, "ema_length": 20}


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
    cv = c.to_numpy(dtype=float)
    n = float(p["length"])
    m = len(cv)
    a, b = np.full(m, np.nan), np.full(m, np.nan)
    bull = np.zeros(m, dtype=bool)
    last_up = last_dn = -1
    for i in range(m):
        if i == 0 or np.isnan(a[i - 1]):
            a[i] = b[i] = cv[i]
        else:
            w = (a[i - 1] - b[i - 1]) / n
            a[i] = max(cv[i], a[i - 1]) - w
            b[i] = min(cv[i], b[i - 1]) + w
        if i > 0:
            if b[i - 1] < cv[i - 1] and b[i] > cv[i]:
                last_up = i
            if a[i - 1] < cv[i - 1] and a[i] > cv[i]:
                last_dn = i
        bull[i] = last_up >= 0 and last_dn >= 0 and (i - last_dn) <= (i - last_up)
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean().to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(bull & (cv < e), index=ix), false, pd.Series(~bull & (cv > e), index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
