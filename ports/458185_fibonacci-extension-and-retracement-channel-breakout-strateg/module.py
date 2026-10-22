"""20-bar channel breakouts, daily bars: a close over the previous 20-bar high goes long, a close under the previous 20-bar low goes short; reversing.
Port of FMZ strategy #458185 "Fibonacci-Extension-and-Retracement-Channel-Breakout-Strategy-斐波那契延展回撤通道突破策略" (Highest High and Lowest Low Channel Strategy).

FMZ source id: 458185

Source
    https://www.fmz.com/strategy/458185 (PineScript v5, FMZ last modified 2024-07-30 16:37:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 200-281), highest(high, 20)[1] / lowest(low, 20)[1]; reverse off; Fibonacci levels plotted only
    pos = close > hh[1] ? 1 : close < ll[1] ? -1 : pos[1];  pos == 1 -> entry Long;  pos == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The position state is held between breakouts, so the entries repeat while held and do nothing.
      The Fibonacci targets are only drawn. There is no exit: positions end at the opposite entry.
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, previous-channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458185_prior_20bar_channel_breakout_state_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 55],
}
DEFAULT_PARAMS = {"length": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    up = (c > h.rolling(n).max().shift(1)).to_numpy()
    dn = (c < lo.rolling(n).min().shift(1)).to_numpy()
    m = len(c)
    state = np.zeros(m, dtype=int)
    s = 0
    for i in range(m):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        state[i] = s
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(state == 1, index=ix), false, pd.Series(state == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
