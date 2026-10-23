"""Broker days: the elastic volume-weighted moving average over 10 bars of volume crossing over the one over 20 bars goes long, crossing under goes short; reversing.
Port of FMZ strategy #439609 "基于EVWMA的MACD交易策略EVWMA-based-MACD-Trading-Strategy" (QuantNomad - EVWMA MACD Strategy).

FMZ source id: 439609

Source
    https://www.fmz.com/strategy/439609 (PineScript v4, FMZ last modified 2024-01-22 10:50:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 110-142), fast sum length 10; slow sum length 20; signal 9 (plot only)
    fast_evwma := ((sum(volume, 10) - volume) * nz(fast_evwma[1], close) + volume * close) / sum(volume, 10);  slow likewise with 20
    crossover(fast_evwma, slow_evwma) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each EVWMA starts from the close on its first bar with a full volume sum (nz of the previous value)
      and is undefined when the volume sum is 0. The MACD signal and histogram only plot. REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, crossings of fast and slow elastic volume-weighted averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the EVWMA weights (volume over its 10- / 20-bar sums); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439609_evwma10_20_cross_reversal"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 40],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _evwma(c, v, n):
    vs = v.rolling(n).sum().to_numpy(dtype=float)
    cv, vv = c.to_numpy(dtype=float), v.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    for i in range(len(cv)):
        if np.isnan(vs[i]) or vs[i] == 0:
            continue
        prev = out[i - 1] if i > 0 and not np.isnan(out[i - 1]) else cv[i]
        out[i] = ((vs[i] - vv[i]) * prev + vv[i] * cv[i]) / vs[i]
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    f, s = _evwma(c, v, int(p["fast"])), _evwma(c, v, int(p["slow"]))
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
