"""Fast MACD signal-line crosses, 5-minute bars, long only: the MACD (EMA 5 / 8) crossing over its SMA 3 signal goes long; the MACD
crossing back under it closes the long.
Port of FMZ strategy #435722 "基于MACD指标的双均线交易策略MACD-Dual-Moving-Average-Tracking-Strategy" (MACD/CAM 2.1).

FMZ source id: 435722

Source
    https://www.fmz.com/strategy/435722 (PineScript v2, FMZ last modified 2023-12-18 12:25:13).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 129-192), MACD 5 / 8 with an SMA 3 signal; resolution = the chart; sell below the previous low switch on
    macd = ema(close, 5) - ema(close, 8);  signal = sma(macd, 3);  longCondition = cross(macd, signal) and macd >= signal;  redCircle = cross(macd, signal) and macd < signal
    shortCondition = redCircle;  if (venderLowerPrev) shortCondition = redCircle or low < low[1]   (the second assignment is declared inside the if block)
    entry long (longCondition);  close long (shortCondition)

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security at the chart resolution gives the chart's values. The "sell below the previous
      low" switch re-declares shortCondition with = inside the if block, which in Pine v4 creates a
      local variable and leaves the one the order reads unchanged: the exit is the red cross alone
      (the other reading, closing on any lower low, is not ported). The 20000 cash size is sizing.
      Long only. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, the previous-low exit switch has no effect (local re-declaration).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash order size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435722_fast_macd_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 3],
    "slow": [8, 13],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 8, "signal": 3}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    le = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).fillna(False).astype(bool)
    lx = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
