"""The previous day's last 3-hour Heikin-Ashi close against an EMA 30 of the previous daily Heikin-Ashi closes, broker days: crossing over goes long, crossing under goes short; reversing.
Port of FMZ strategy #477596 "Multi Timeframe Heikin Ashi Moving Average Trend Following Trading System" (Heikin Ashi Candle Time Frame @tradingbauhaus).

FMZ source id: 477596

Source
    https://www.fmz.com/strategy/477596 (PineScript v5, FMZ last modified 2025-01-06 16:20:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-154), HA EMA timeframe "180", shift 0; HA EMA period 1, shift 1; slow EMA 30, shift 1; MACD filter off; HA candle timeframe "60" unused
    ha_close = ohlc4;  mha = security("180", ha_close);  fma = ema(mha[1], 1);  sma = ema(ha_close[1], 30);  crossover(fma, sma) -> entry Long, close Short;  crossunder -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "180" request on a daily chart is a lower time frame: it returns the chart bar's last 3-hour
      block, counted from the broker-day start (as #436765), whose Heikin-Ashi close is the block's
      ohlc4; it is built from the minutes in precompute. An EMA of length 1 is the series itself, so fma
      is that value one day back. The MACD filter is off by default and the 60-minute input is unused.
      The closes follow reversing entries and leave them standing. REVERSAL INTENDED. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 3-hour value from completed blocks of past days.
    2 generic: PASS, Heikin-Ashi close against its slow EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 3-hour blocks from the broker-day start.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477596_last3h_ha_close_vs_daily_ha_ema30_reversal"
FAMILY = "heikin_ashi"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [30, 60, 15],
}
DEFAULT_PARAMS = {"slow": 30, "block_minutes": 180}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    ny = df.index.tz_convert("America/New_York").tz_localize(None)
    offset = (ny + pd.Timedelta(hours=7)) - lab               # time since the broker-day start
    blk = np.asarray(offset // pd.Timedelta(minutes=int(p["block_minutes"])))
    key = pd.MultiIndex.from_arrays([lab, blk])
    g = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    g["ha"] = g[["open", "high", "low", "close"]].mean(axis=1)
    last_blk = g["ha"].groupby(level=0).last()                # the day's last 3-hour block
    bars["ltf_ha"] = last_blk.reindex(bars.index).to_numpy()
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ha = bars_df[["open", "high", "low", "close"]].mean(axis=1)
    fma = bars_df["ltf_ha"].shift(1)
    sma = ha.shift(1).ewm(span=int(p["slow"]), adjust=False).mean()
    le = (fma > sma) & (fma.shift(1) <= sma.shift(1))
    se = (fma < sma) & (fma.shift(1) >= sma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
