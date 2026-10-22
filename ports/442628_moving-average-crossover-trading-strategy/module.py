"""Close crossing its EMA 8 above an EMA 50, daily bars, long only: the close crossing over the EMA 8 while above the EMA 50 goes long; the EMA 8 crossing under the EMA 18 closes.
Port of FMZ strategy #442628 "Moving Average Crossover Trading Strategy" (Trading EMAs).

FMZ source id: 442628

Source
    https://www.fmz.com/strategy/442628 (PineScript v5, FMZ last modified 2024-02-23 12:46:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-167), EMA 8 / 18 / 50
    crossover(close, ema8) and close > ema50 -> entry Long;  crossunder(ema8, ema18) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442628_close_ema8_cross_ema50_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 5],
    "mid": [18, 30],
}
DEFAULT_PARAMS = {"fast": 8, "mid": 18, "trend": 50}


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
    e8 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e18 = c.ewm(span=int(p["mid"]), adjust=False).mean()
    e50 = c.ewm(span=int(p["trend"]), adjust=False).mean()
    go = ((c > e8) & (c.shift(1) <= e8.shift(1)) & (c > e50)).to_numpy()
    out = ((e8 < e18) & (e8.shift(1) >= e18.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
