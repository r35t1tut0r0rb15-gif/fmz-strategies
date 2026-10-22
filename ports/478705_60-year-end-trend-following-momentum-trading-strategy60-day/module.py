"""Close crossings over the SMA 60 with a rising SMA-14 slope of it, 3-minute bars, long only: such a cross buys; every bar on 31 December (UTC) closes all.
Port of FMZ strategy #478705 "年末趋势跟踪动量交易策略60日均线突破-Year-end-Trend-Following-Momentum-Trading-Strategy60-day-MA-Breakout" (Buy above 60-day MA, Sell at year-end).

FMZ source id: 478705

Source
    https://www.fmz.com/strategy/478705 (PineScript v5, FMZ last modified 2025-01-17 14:55:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-134), SMA 60 (bars); slope = change of sma(ma, 14); date range always true; year-end close on 31 Dec
    crossover(close, sma60) and sma(sma60, 14) - sma(sma60, 14)[1] > 0 -> entry Buy;  month == 12 and day == 31 -> close_all  (30 / 29 Dec: "next day not a trading day" is never true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * isTradingDay always returns true, so the year-end flag is set only on 31 December, and then on every
      bar of that day (UTC dates, the header market's exchange time). A buy on that day is closed at the
      next bar (a loop: close_all acts on the held position). The "60-day" MA is 60 chart bars. Long
      only. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a slope filter and a calendar exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: calendar exit on 31 December by UTC date.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478705_close_cross_sma60_slope_dec31_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 200],
    "slope_len": [14, 5],
}
DEFAULT_PARAMS = {"length": 60, "slope_len": 14}


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
    ma = c.rolling(int(p["length"])).mean()
    sm = ma.rolling(int(p["slope_len"])).mean()
    slope = sm - sm.shift(1)
    buy = ((c > ma) & (c.shift(1) <= ma.shift(1)) & (slope > 0)).to_numpy()
    t = c.index.tz_convert("UTC")
    ye = np.asarray((t.month == 12) & (t.day == 31))
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and pos == 0:
            le[i], nxt = True, 1
        if ye[i] and pos == 1:              # close_all acts on the held position only
            lx[i], nxt = True, 0
    ix = c.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
