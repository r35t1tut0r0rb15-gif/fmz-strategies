"""Sling-shot re-entry signals traded AGAINST the trend, as written: an up-trend pullback that
closes back above the fast EMA goes short; the down-trend mirror goes long (always in).
Port of FMZ strategy #361675 "CM-Sling-Shot-System" (ChrisMoody CM_SlingShotSystem, orders added).

Source
    https://www.fmz.com/strategy/361675 (PineScript, FMZ last modified 2022-05-07 17:06:50).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-92)
    emaSlow = ema(close,62); emaFast = ema(close,38)
    entryUpTrend = emaFast > emaSlow and close[1] < emaFast and close > emaFast
    entryDnTrend = emaFast < emaSlow and close[1] > emaFast and close < emaFast
    sl and entryUpTrend -> entry "SELL" short;  else sl and entryDnTrend -> entry "BUY" long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ChrisMoody's indicator marks entryUpTrend as a conservative BUY; the added orders sell on
      it. The port follows the orders as written (flagged in PORT_NOTES).
    * close[1] is compared with the current bar's emaFast, as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default
      opposite-entry reversal applies). The `sl` display switch is true by default.
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361675_slingshot_faded"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [20, 38, 50],
    "ema_slow": [62, 100],
}
DEFAULT_PARAMS = {"ema_fast": 38, "ema_slow": 62}


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
    fast = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    warm = np.arange(len(c)) >= int(p["ema_slow"])
    up_t = ((fast > slow) & (c.shift(1) < fast) & (c > fast)).to_numpy() & warm
    dn_t = ((fast < slow) & (c.shift(1) > fast) & (c < fast)).to_numpy() & warm

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if up_t[i]:
            if pos != -1:
                se[i], pos = True, -1
        elif dn_t[i] and pos != 1:
            le[i], pos = True, 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
