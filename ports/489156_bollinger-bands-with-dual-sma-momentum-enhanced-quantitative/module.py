"""Upper-band breakouts in the SMA 6 / 45 trend, long only, broker days: a close above the Bollinger 21 x 2 upper band
and above SMA 45, with SMA 6 above SMA 45, goes long; a close below the lower band or SMA 6 below SMA 45 closes it.
Port of FMZ strategy #489156 "布林带结合快速与慢速移动平均线的多维趋势强化量化交易策略-Bollinger-Bands-with-Dual-SMA-Momentum-Enhanced-Quantitative-Trading-Strategy" (BTC Bollinger Bands w Fast and Slow SMAs).

FMZ source id: 489156

Source
    https://www.fmz.com/strategy/489156 (PineScript v6, FMZ last modified 2025-04-02 11:28:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 165-214), BB 21 x 2 (SMA basis), SMA 6 / 45
    close > upper and close > sma45 and sma6 > sma45 -> entry long
    close < lower or sma6 < sma45 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The basis MA type input defaults to SMA (VWMA, a volume weighting, is one of its options and is not used:
      check 8). ta.stdev is the population deviation. An entry and an exit cannot hold on one bar.
    * The commission and slippage in strategy() are costs (not in the module). Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands and SMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8; the VWMA option of the basis input is not used).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489156_bb_upper_breakout_sma_trend_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "slow_sma": [45, 100],
}
DEFAULT_PARAMS = {"length": 21, "mult": 2.0, "fast_sma": 6, "slow_sma": 45}


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
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    fast, slow = c.rolling(int(p["fast_sma"])).mean(), c.rolling(int(p["slow_sma"])).mean()
    entry = ((c > upper) & (c > slow) & (fast > slow)).astype(bool)
    exit_ = ((c < lower) | (fast < slow)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return entry, exit_, false, false.copy()


def portfolio_kwargs(**params):
    return {}
