"""Broker days, long only: a close above the VWMA 14 plus its 14-bar deviation scaled by the 25-bar Garman-Klass volatility over its own average goes long; a close below the lower band closes it.
Port of FMZ strategy #475603 "自适应VWAP波段基于Garman-Klass波动率动态跟踪策略-Adaptive-VWAP-Bands-with-Garman-Klass-Volatility-Dynamic-Tracking-Strategy" (Adaptive VWAP Bands with Garman Klass Volatility).

FMZ source id: 475603

Source
    https://www.fmz.com/strategy/475603 (PineScript v5, FMZ last modified 2024-12-20 14:51:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-146), GK volatility 25; VWMA 14 ("VWAP"); stdev 14; multiplier = gcv / sma(gcv, 25)
    sum_gkv = sum over 25 bars of 0.5 x log(high / low)^2 - (2 ln 2 - 1) x log(close / open)^2;  gcv = sqrt(sum_gkv / 25)
    close > vwma14 + stdev14 x gcv / sma(gcv, 25) -> entry Long;  else if close < the lower band -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "VWAP" is ta.vwma(close, 14). The Garman-Klass sum restarts at 0 each bar (the var is reset),
      so it is a plain 25-bar window. An entry while long adds nothing; the close and the entry are
      exclusive (else-if). Pine's stdev is the population deviation. Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility-scaled VWMA band breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) as the VWMA weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475603_vwma_gk_volatility_band_breakout_long_only"
FAMILY = "volatility_band"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [25, 50],
    "vwap_len": [14, 28],
}
DEFAULT_PARAMS = {"length": 25, "vwap_len": 14, "vol_mult": 1.0}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n, nv = int(p["length"]), int(p["vwap_len"])
    term = 0.5 * np.log(h / lo) ** 2 - (2 * np.log(2) - 1) * np.log(c / o) ** 2
    gcv = np.sqrt(term.rolling(n).sum() / n)
    vw = (c * v).rolling(nv).mean() / v.rolling(nv).mean()
    band = c.rolling(nv).std(ddof=0) * gcv / gcv.rolling(n).mean() * float(p["vol_mult"])
    entry = c > vw + band
    ex = ~entry & (c < vw - band)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
