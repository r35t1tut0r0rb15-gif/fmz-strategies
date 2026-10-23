"""The sum of a 30- and a 90-bar stochastic (K smoothed 2) and its VWMA 30, broker days, long only: both turning up together after a mixed bar goes long; both turning down together after a mixed bar closes.
Port of FMZ strategy #430278 "双Stochastics与成交量加权移动平均线组合指标Dual-Stochastics-and-Volume-Weighted-Moving-Average-Combination-Indicator-Strategy" (Trend Finder V2).

FMZ source id: 430278

Source
    https://www.fmz.com/strategy/430278 (PineScript v4, FMZ last modified 2023-10-26 17:18:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 157-201), stochastics 30 / 90 (smooth 2); VWMA 30 of their sum
    ts = sma(stoch(30), 2) + sma(stoch(90), 2);  tsl = vwma(ts, 30);  colour = ts and tsl both rising ? lime : both falling ? red : yellow
    yellow then lime -> entry Long;  yellow then red -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour is lime when the sum and its VWMA both rise, red when both fall, yellow otherwise; the
      entry / close need a yellow bar just before, as written. Long only. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dual-stochastic trend turns with a volume-weighted signal.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(ts, 30); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430278_dual_stochastic_sum_vwma_colour_turn_long"
FAMILY = "stochastic_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [30, 14],
    "vwma_len": [30, 15],
}
DEFAULT_PARAMS = {"period_k": 30, "vwma_len": 30, "period_k_two": 90}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    st = lambda n: (100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min()).replace(0.0, np.nan)).rolling(2).mean()
    ts = st(int(p["period_k"])) + st(int(p["period_k_two"]))
    n = int(p["vwma_len"])
    tsl = (ts * v).rolling(n).sum() / v.rolling(n).sum()
    lime = (ts > ts.shift(1)) & (tsl > tsl.shift(1))
    red = (ts < ts.shift(1)) & (tsl < tsl.shift(1))
    yellow = ~lime & ~red
    le = yellow.shift(1, fill_value=False) & lime
    lx = yellow.shift(1, fill_value=False) & red
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
