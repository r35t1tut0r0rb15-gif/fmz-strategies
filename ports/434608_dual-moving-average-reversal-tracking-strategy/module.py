"""HPotter "daily SMA" side, 10-minute bars, as written: the close above the 14-bar SMA of the daily close series (the last
completed broker day's close, repeated on every 10-minute bar) goes long, below it goes short; held in between.
Port of FMZ strategy #434608 "Dual Moving Average Reversal Tracking Strategy" (Simple SMA Strategy Backtest).

FMZ source id: 434608

Source
    https://www.fmz.com/strategy/434608 (PineScript v4, FMZ last modified 2023-12-07 17:40:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 135-160), resolution D, source close, length 14, trigger close; reverse false
    xSeries = security(tickerid, 'D', close);  xSMA = sma(xSeries, 14)   (on the chart's bars);  pos = close > xSMA ? 1 : close < xSMA ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', close) without lookahead is read as the last completed broker day's close
      (17:00 America/New_York), as #429502. The SMA runs on the chart's 10-minute series of that
      value, so it equals the previous day's close except during the 14 bars after a day change, as
      written.
    * The side holds until the opposite test; close_all only acts before the first. strategy.entry
      reverses: REVERSAL INTENDED. reverse is false. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, price against a prior-day level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily close on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434608_prev_day_close_sma_side"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 50],
    "reverse": [False, True],
}
DEFAULT_PARAMS = {"length": 14, "reverse": False}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    day = broker_day(bars_df.index)
    dclose = pd.Series(c.to_numpy(), index=day).groupby(level=0).last().shift(1)
    xs = pd.Series(dclose.reindex(day).to_numpy(), index=c.index)
    sma = xs.rolling(int(p["length"])).mean()
    up, dn = (c > sma).to_numpy(), (c < sma).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    if bool(p["reverse"]):
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
