"""EMA 9 / 21 and MACD 12 / 26 / 9 up-crosses on the same bar, hourly bars, long only: both up-crosses go long, either down-cross closes; signals on the first bar of each UTC day are dropped.
Port of FMZ strategy #483047 "多周期均线带及MACD交叉策略系统-Multi-Period-Moving-Average-Ribbon-and-MACD-Crossover-Strategy-System" (Daily MA Ribbon + MACD Crossover with Buy/Sell Signals).

FMZ source id: 483047

Source
    https://www.fmz.com/strategy/483047 (PineScript v6, FMZ last modified 2025-02-21 10:51:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-166), EMA 9 / 21 (menu defaults); MACD 12 / 26 / 9 with EMA oscillator and signal (menu defaults); daily reset on time("D")
    buy = crossover(ma1, ma2) and crossover(macd, signal);  sell = crossunder(ma1, ma2) or crossunder(macd, signal)
    change(time("D")) -> buy := false, sell := false;  buy -> entry Buy;  sell -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * time("D") starts the day at 00:00 in the chart exchange's time zone, UTC for the header's Binance
      pair: the first bar of each UTC date (fixed UTC, no DST) has both signals cleared, as written. The
      MA and MACD type menus keep their defaults (EMA). A sell on the bar of a buy is masked by the buy.
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA and MACD up-crosses together.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: day start 00:00 UTC (time("D") of the header exchange; fixed UTC, no DST): first bar of the day has no signal.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483047_ema9_21_and_macd_cross_same_bar_daily_reset_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
SESSION_TZ = "UTC"  # time("D") reads the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "ma1_length": [9, 5],
    "ma2_length": [21, 50],
}
DEFAULT_PARAMS = {"ma1_length": 9, "ma2_length": 21, "fast_length": 12, "slow_length": 26, "signal_length": 9}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    m1, m2 = ema(c, p["ma1_length"]), ema(c, p["ma2_length"])
    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    sig = ema(macd, p["signal_length"])
    ma_up = (m1 > m2) & (m1.shift(1) <= m2.shift(1))
    ma_dn = (m1 < m2) & (m1.shift(1) >= m2.shift(1))
    md_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    md_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    day = pd.Series(np.asarray(bars_df.index.tz_convert(SESSION_TZ).normalize()), index=c.index)
    new_day = day != day.shift(1)
    new_day.iloc[0] = False
    buy = ma_up & md_up & ~new_day
    sell = (ma_dn | md_dn) & ~new_day
    false = pd.Series(False, index=c.index)
    return buy, sell & ~buy, false, false.copy()


def portfolio_kwargs(**params):
    return {}
