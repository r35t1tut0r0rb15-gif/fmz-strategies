"""McGinley averages from three time frames, 1-hour bars: the 15-minute McGinley 21 (its last value inside the hour) crossing over the 1-hour McGinley 21 while the smoothed 4-hour McGinley 50 rises goes
long, the mirror short; the opposite crossing closes; reversing.
Port of FMZ strategy #442618 "Triple Dynamic Moving Average Trend Tracking Strategy" (Triple MA HTF strategy - Dynamic Smoothing).

FMZ source id: 442618

Source
    https://www.fmz.com/strategy/442618 (PineScript v5, FMZ last modified 2024-02-23 12:07:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-290), McGinley 21 on 15m, 21 on 60m, 50 on 240m; smoothing round(HTF minutes / 60); pyramiding 5; equity quantity; commission 0.05
    MA_HTF = security(15, mcginley(close, 21));  MA_HTF2 = security(60, mcginley(close, 21));  MA_HTF3 = security(240, mcginley(close, 50));  UP3 = sma(MA_HTF3, 4) rising
    crossover(MA_HTF, MA_HTF2) and UP3 -> entry Long;  position > 0 and crossunder -> close Long;  crossunder and DOWN3 -> entry Short;  position < 0 and crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute request from a 1-hour chart is a lower time frame: its value is the last 15-minute
      bar inside the hour (as #436765), built from minutes in precompute. The 60-minute request is the
      chart itself. A version-5 request.security() without lookahead on 240 minutes is read as the last
      completed 4-hour bar (UTC-aligned blocks, as #440503), then smoothed over round(240 / 60) = 4
      hourly values. The first two smoothing lengths (round(15 / 60) = 0 and 1) only feed plots. The
      McGinley line starts from the first close (Pine's ema first value), then follows its recursion.
      A crossing back closes before any re-entry, so pyramiding 5 never adds. The quantity is sizing.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 4-hour values from completed bars, 15-minute values ending with the bar.
    2 generic: PASS, multi-time-frame McGinley crossings with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity quantity, capital and commission stored.
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

NAME = "fmz_442618_mcginley_15m_1h_cross_4h_trend"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "length3": [50, 100],
}
DEFAULT_PARAMS = {"length": 21, "length3": 50, "smooth3": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _mcginley(src, n):
    v = src.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    mg = np.nan
    for i in range(len(v)):
        if np.isnan(mg):
            mg = v[i]
        elif not np.isnan(v[i]):
            mg = mg + (v[i] - mg) / (n * (v[i] / mg) ** 4)
        out[i] = mg
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    b15 = _resample(raw_1m_df, "15min")
    m15 = _mcginley(b15["close"], int(p["length"]))
    last15 = m15.groupby(b15.index.floor("1h")).last()           # the last 15-minute bar inside the hour
    bars["mg15"] = last15.reindex(bars.index).to_numpy()
    b240 = _resample(raw_1m_df, "4h")
    m240 = _mcginley(b240["close"], int(p["length3"])).shift(1)   # last completed 4-hour bar
    bars["mg240"] = m240.reindex(bars.index.floor("4h")).to_numpy()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = bars_df["mg15"]
    b = _mcginley(c, int(p["length"]))
    s3 = bars_df["mg240"].rolling(int(p["smooth3"])).mean()
    up3 = s3 > s3.shift(1)
    dn3 = s3 < s3.shift(1)
    co = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    cu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    buy, sell = co & up3.to_numpy(), cu & dn3.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if held == 1 and cu[i] and new == 1:
            new = 0
        if sell[i] and new != -1:
            new = -1
        if held == -1 and co[i] and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
