"""Elastic volume-weighted moving averages (volume sums of 10 and 20 bars) crossing: fast over slow goes long, under goes short; broker days, reversing.
Port of FMZ strategy #435137 "基于EVWMA指标的趋势跟踪策略EVWMA-Trend-Following-Strategy" (QuantNomad - EVWMA Cross Strategy).

FMZ source id: 435137

Source
    https://www.fmz.com/strategy/435137 (PineScript v4, FMZ last modified 2023-12-12 16:00:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 106-130), fast sum length 10, slow sum length 20
    evwma := ((sum(volume, n) - volume) x nz(evwma[1], close) + volume x close) / sum(volume, n)
    crossover(fast, slow) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EVWMA recursion starts from the close (nz) and is na until the volume sum exists. The weights
      are ratios of volume to its own sum, so the units cancel. REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-weighted average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in both EVWMAs; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435137_evwma_10_20_cross_daily_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [10, 5],
    "slow_len": [20, 40],
}
DEFAULT_PARAMS = {"fast_len": 10, "slow_len": 20}


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
    cv, vv = c.to_numpy(dtype=float), v.to_numpy(dtype=float)
    sv = v.rolling(n).sum().to_numpy()
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        base = cv[i] if np.isnan(prev) else prev
        out[i] = ((sv[i] - vv[i]) * base + vv[i] * cv[i]) / sv[i] if sv[i] else np.nan
        prev = out[i]
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    f, s = _evwma(c, v, int(p["fast_len"])), _evwma(c, v, int(p["slow_len"]))
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
