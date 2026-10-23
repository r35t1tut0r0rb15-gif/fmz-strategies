"""Broker days, long only: a close above the upper Bollinger band (20 x 2) on volume above 2 x its SMA 20 goes long; a close under the lower band on such volume closes.
Port of FMZ strategy #437386 "Bollinger Bands Volume Confirmation Quantitative Trading Strategy" (Volume + Bollinger Bands Strategy).

FMZ source id: 437386

Source
    https://www.fmz.com/strategy/437386 (PineScript v5, FMZ last modified 2024-01-02 11:04:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 115-141), BB 20 x 2; volume multiplier 2 x SMA 20
    buyCondition = close > upper and volume > 2 sma(volume, 20) -> entry Buy;  sellCondition = close < lower and volume > 2 sma(volume, 20) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume test compares the bar with its own SMA. stdev is the population form. Long only. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts on volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 2 x sma(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437386_bb20_breakout_volume_spike_daily_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "vol_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "vol_mult": 2.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    spike = v > float(p["vol_mult"]) * v.rolling(n).mean()
    buy = ((c > basis + dev) & spike).to_numpy()
    sell = ((c < basis - dev) & spike).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            le[i], pos = True, 1
        elif pos == 1 and sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
