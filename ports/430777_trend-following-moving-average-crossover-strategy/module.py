"""Trend catcher (pernath), 15-minute bars: the EMA 55 crossing above the EMA 100 with the EMA 12 above the EMA 200 goes long
(target 35 %, stop 3 %); the EMA 100 crossing below the EMA 200 goes short (target 27 %, stop 2 %); the EMA 12 crossing
under the EMA 30 closes a long, the EMA 25 crossing under the EMA 6 closes a short.
Port of FMZ strategy #430777 "Trend Following Moving Average Crossover Strategy" (TREND_CATCHER).

FMZ source id: 430777

Source
    https://www.fmz.com/strategy/430777 (PineScript v5, FMZ last modified 2023-11-01 17:18:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 235-345), EMA 6 / 12 / 25 / 30 / 55 / 100 / 200; long TP 35 % SL 3 %, short TP 27 % SL 2 % (of the close, in ticks)
    Go_Long = crossover(ema55, ema100) and ema12 > ema200 -> close short, entry long
    Go_Short = crossunder(ema100, ema200) -> close long, entry short
    exit(profit = close x 35 % / mintick, loss = close x 3 % / mintick) for longs; 27 % / 2 % for shorts, every bar
    crossunder(ema12, ema30) -> close long;  crossunder(ema25, ema6) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit distances are re-sized from each bar's close (moving levels): rule 2, mark
      trailing_stop_pending; the port fixes them at the same fractions of the fill (long sl 0.03 /
      tp 0.35, short sl 0.02 / tp 0.27), side from the signal bar, shifted one bar.
    * Each entry signal also closes the other side (a reversal). When both entries fire on one bar the
      long, written last, wins. A close signal on the bar of a same-side entry keeps the entry (stated
      approximation; the source ends flat when that side was already held).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at the fill (rule 2).
    2 generic: PASS, moving averages and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: a fixed quantity of 1 stored; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430777_trend_catcher_emas"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_long": [0.03, 0.05],
    "sl_short": [0.02, 0.04],
}
DEFAULT_PARAMS = {"sl_long": 0.03, "tp_long": 0.35, "sl_short": 0.02, "tp_short": 0.27}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def _signals(bars_df):
    c = bars_df["close"]
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (6, 12, 25, 30, 55, 100, 200)}
    go_long = (_xo(e[55], e[100]) & (e[12] > e[200])).astype(bool)
    go_short = (_xu(e[100], e[200]) & ~go_long).astype(bool)
    cancel_long = _xu(e[12], e[30])
    cancel_short = _xu(e[25], e[6])
    long_x = ((go_short | cancel_long) & ~go_long).astype(bool)
    short_x = ((go_long | cancel_short) & ~go_short).astype(bool)
    return go_long, long_x, go_short, short_x


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    return _signals(bars_df)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    go_long, _, go_short, _ = _signals(bars_df)
    idx = bars_df.index
    sl = pd.Series(np.where(go_long, p["sl_long"], np.where(go_short, p["sl_short"], np.nan)), index=idx)
    tp = pd.Series(np.where(go_long, p["tp_long"], np.where(go_short, p["tp_short"], np.nan)), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
