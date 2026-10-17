"""Donchian 20 trend state, always in the market, daily (broker-day) bars: a close above the previous bar's 20-bar
high sets the trend up (long), a close below the previous 20-bar low sets it down (short); the trend holds in between.
Port of FMZ strategy #483040 "多重周期唐奇安指标趋势跟踪与背离交易策略-Multi-Period-Donchian-Channel-Trend-Following-and-Divergence-Trading-Strategy" (Donchian Trend Ribbon Strategy).

FMZ source id: 483040

Source
    https://www.fmz.com/strategy/483040 (PineScript v6, FMZ last modified 2025-02-21 10:38:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-180), Donchian period 20
    trend = close > highest(20)[1] ? 1 : close < lowest(20)[1] ? -1 : trend[1] (starts 0)
    trend == 1 -> entry long; trend == -1 -> entry short; the closes on the opposite trend are redundant

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ribbon's other channel lengths only colour plots. Every bar in a trend is an entry signal for that side
      (same-side ignored while held): stop-and-reverse on trend changes (REVERSAL INTENDED). No exits, no stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian channels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_483040_donchian_trend_state_reversal_1d"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dlen": [20, 40],
}
DEFAULT_PARAMS = {"dlen": 20}


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
    n = int(p["dlen"])
    hh, ll = h.rolling(n).max().shift(1).to_numpy(), lo.rolling(n).min().shift(1).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tr = np.zeros(m, dtype=np.int8)
    t = 0
    for i in range(m):
        if cv[i] > hh[i]:
            t = 1
        elif cv[i] < ll[i]:
            t = -1
        tr[i] = t
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(tr == 1, index=idx), false, pd.Series(tr == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
