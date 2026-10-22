"""Engulfing and three-line-strike candles on the side of EMA 2 against SMA 200, from 08:30 to 12:00 UTC, 1-minute bars: a bullish pattern with EMA 2 over SMA 200 goes long, a bearish one under it goes short; EMA 2 crossing back through SMA 200 closes; reversing.
Port of FMZ strategy #485125 "趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following" (TMA Strategy).

FMZ source id: 485125

Source
    https://www.fmz.com/strategy/485125 (PineScript v5, FMZ last modified 2025-03-06 11:02:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-251), SMAs 21 / 50 / 100 (plots) / 200; EMA 2; session 08:30-12:00 (timezone input unused); 100 % of equity, capital 10000, commission 0.1 %
    long = (bullishEngulfing or bullish 3LS) and ema2 > sma200 and in session;  short mirror
    crossunder(ema2, sma200) -> close Long;  crossover(ema2, sma200) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * timestamp(year, month, day, 8, 30) has no zone argument, so it reads the chart exchange's zone, UTC
      for the header's Binance pair; the timezone input feeds nothing: bars opening 08:30-12:00 UTC
      (inclusive) qualify (fixed UTC, no DST). The engulfing and strike tests are kept as written. A close
      on the bar of an entry is masked by the entry; an entry on the other side reverses (REVERSAL
      INTENDED). The 100 % of equity size and the capital are sizing; the commission is a cost (the house
      cost model applies). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle patterns with a fast / slow average side.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock window 08:30-12:00 UTC on the bar's open time (fixed UTC, no DST; the header exchange's time zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485125_engulf_3ls_ema2_sma200_side_utc_window_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
SESSION_TZ = "UTC"  # timestamp() without a zone reads the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "len4": [200, 100],
    "ema_fast": [2, 5],
}
DEFAULT_PARAMS = {"len4": 200, "ema_fast": 2, "start_minute": 510, "end_minute": 720}


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
    o, c = bars_df["open"], bars_df["close"]
    s4 = c.rolling(int(p["len4"])).mean()
    e2 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    o1, c1 = o.shift(1), c.shift(1)
    bull3 = (c.shift(3) < o.shift(3)) & (c.shift(2) < o.shift(2)) & (c1 < o1) & (c > o1)
    bear3 = (c.shift(3) > o.shift(3)) & (c.shift(2) > o.shift(2)) & (c1 > o1) & (c < o1)
    bull_e = (o <= c1) & (o < o1) & (c > o1)
    bear_e = (o >= c1) & (o > o1) & (c < o1)
    loc = bars_df.index.tz_convert(SESSION_TZ)
    mod = np.asarray(loc.hour * 60 + loc.minute)
    sess = pd.Series((mod >= int(p["start_minute"])) & (mod <= int(p["end_minute"])), index=c.index)
    le = (bull_e | bull3) & (e2 > s4) & sess
    se = (bear_e | bear3) & (e2 < s4) & sess
    lx = (e2 < s4) & (e2.shift(1) >= s4.shift(1))
    sx = (e2 > s4) & (e2.shift(1) <= s4.shift(1))
    return le & ~se, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
