"""Bollinger 20 x 1.9 upper-band breakouts, long only, broker days: from flat, the close crossing above the upper band goes
long; the trade closes once 4 bars in a row have not closed above the upper band or when the low touches the middle
band.
Port of FMZ strategy #488140 "布林带动态突破加速度量化交易策略Bollinger-Bands-Dynamic-Breakout-Momentum-Trading-Strategy" (Bollinger Bands Strategy 5m).

FMZ source id: 488140

Source
    https://www.fmz.com/strategy/488140 (PineScript v6, FMZ last modified 2025-03-25 14:10:44).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 233-273), BB 20 x 1.9, tolerance 4
    crossover(close, upper) and position_size <= 0 -> entry long (the short entry is commented out)
    position_size > 0: barsNotAboveUpper = close > upper ? 0 : + 1;  >= 4 or low <= basis -> close long, counter 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit block tests strategy.position_size, the position held at the bar's start: the count starts on the fill
      bar; the counter is reset only by a close above the band or an exit, as written.
    * Long only (the short entry and exit are comments): opposite entries cannot occur. "5m" in the title is a label;
      the backtest header is daily: broker days (17:00 America/New_York), stamped with their first minute; FREQ =
      "1D". No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488140_bb_upper_breakout_tolerance_exit"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.9, 2.5],
    "tolerance": [4, 2],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.9, "tolerance": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    up = basis + p["mult"] * c.rolling(n).std(ddof=0)
    go = ((c > up) & (c.shift(1) <= up.shift(1))).to_numpy()
    above = (c > up).to_numpy()
    touch = (bars_df["low"] <= basis).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, cnt = 0, 0
    for i in range(m):
        start = pos
        if go[i] and start <= 0:
            pos = 1
        if start > 0:
            cnt = 0 if above[i] else cnt + 1
            if cnt >= p["tolerance"] or touch[i]:
                pos, cnt = 0, 0
        le[i] = start == 0 and pos == 1
        lx[i] = start == 1 and pos == 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
