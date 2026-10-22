"""Close against an average of the daily close, 1-hour bars: the close above the 14-bar SMA of the last completed broker day's close goes long, below it short; reversing on each change (the take-profit /
stop option is off).
Port of FMZ strategy #440107 "Moving Average Crossover Strategy" (SMA Backtest).

FMZ source id: 440107

Source
    https://www.fmz.com/strategy/440107 (PineScript v4, FMZ last modified 2024-01-26 16:29:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-188), resolution D, source close, length 14, trigger close; take profit 50 / stop 20 with "Use Take/Stop" off; reverse off
    xSeries = security(syminfo.tickerid, "D", close);  xSMA = sma(xSeries, 14);  pos = close > xSMA ? 1 : close < xSMA ? -1 : pos[1]
    possig = pos changed ? pos : 0;  possig 1 -> entry Long, -1 -> entry Short;  (UseTPSL off: the strategy.close lines are skipped)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: xSeries is the
      previous broker day's close on every 1-hour bar, built from the module's own bars; the SMA then
      runs over 14 one-hour values, as written. The take-profit / stop closes are off by default and not
      ported. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: PASS, close against an average of the daily close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND429383 (2 members, best partner #429383, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily close (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440107_close_vs_daily_close_sma"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 50],
}
DEFAULT_PARAMS = {"length": 14, "reverse": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    dc = c.groupby(day).last().shift(1).reindex(day)          # last completed day
    xs = pd.Series(dc.to_numpy(), index=c.index)
    sma = xs.rolling(int(p["length"])).mean()
    above, below = (c > sma).to_numpy(), (c < sma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if above[i]:
            pos = 1
        elif below[i]:
            pos = -1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
