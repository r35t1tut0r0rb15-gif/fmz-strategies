"""Engulfing or three-bar reversal candles on the SMA 200 side inside an 08:30-12:00 session, 1-minute bars: a bullish
engulfing bar or a green reversal after three red bars, with EMA 2 above SMA 200, inside the session goes long
(shorts mirrored); EMA 2 crossing back through SMA 200 closes the trade.
Port of FMZ strategy #485125 "趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following" (TMA Strategy).

FMZ source id: 485125

Source
    https://www.fmz.com/strategy/485125 (PineScript v5, FMZ last modified 2025-03-06 11:02:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 177-242), SMA 200 ("smma4"), EMA 2, session 08:30-12:00 (filter on)
    bullSig = three red bars then close > open[1];  bullishEngulfing = open <= close[1] and open < open[1] and
    close > open[1]  (bear mirrored)
    long = (engulfing or bullSig) and ema2 > sma200 and in session -> entry long (short mirrored)
    crossunder(ema2, sma200) -> close long;  crossover(ema2, sma200) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): timestamp(year, month, dayofmonth, 8, 30) has no time-zone argument, so the window
      is 08:30-12:00 (inclusive) in the chart's time zone and the tz input is unused: UTC on the author's Binance chart
      (session_tz "UTC", the default) or America/Chicago (the input's default, DST by the zone) as the variant.
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); entries
      reverse (REVERSAL INTENDED).
    * FREQ = "1min" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle patterns and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entry window 08:30-12:00 in session_tz (UTC as written; America/Chicago, DST by the zone, as the variant).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485125_candle_reversal_sma200_session"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "session_tz": ["UTC", "America/Chicago"],
    "len4": [200, 100],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "len4": 200, "start_h": 8, "start_m": 30, "end_h": 12, "end_m": 0}


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
    sma = c.rolling(int(p["len4"])).mean()
    e2 = c.ewm(span=2, adjust=False).mean()
    o1, c1 = o.shift(1), c.shift(1)
    red = c < o
    green = c > o
    bull_sig = red.shift(3, fill_value=False) & red.shift(2, fill_value=False) & red.shift(1, fill_value=False) & (c > o1)
    bear_sig = (green.shift(3, fill_value=False) & green.shift(2, fill_value=False) & green.shift(1, fill_value=False)
                & (c < o1))
    bull_eng = (o <= c1) & (o < o1) & (c > o1)
    bear_eng = (o >= c1) & (o > o1) & (c < o1)
    loc = bars_df.index.tz_convert(p["session_tz"])
    hm = pd.Series(loc.hour * 60 + loc.minute, index=bars_df.index)
    inside = (hm >= int(p["start_h"]) * 60 + int(p["start_m"])) & (hm <= int(p["end_h"]) * 60 + int(p["end_m"]))
    go_l = ((bull_eng | bull_sig) & (e2 > sma) & inside).to_numpy()
    go_s = ((bear_eng | bear_sig) & (e2 < sma) & inside).to_numpy()
    out_l = ((e2 < sma) & (e2.shift(1) >= sma.shift(1))).to_numpy()
    out_s = ((e2 > sma) & (e2.shift(1) <= sma.shift(1))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
