"""Broker days: the EMA 9 crossing over the EMA 21 above the SMA 50 on volume over 1.5 x its 20-day average goes long, the mirror goes short; each trade has a 1 % stop and a 400 % target from its fill; reversing.
Port of FMZ strategy #483129 "Advanced Quantitative Trading Multi Moving Average Crossover System with Volume Filter Strategy" (Optimized Moving Average Crossover Strategy with Volume Filter).

FMZ source id: 483129

Source
    https://www.fmz.com/strategy/483129 (PineScript v5, FMZ last modified 2025-02-21 14:50:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-158), EMA 9 / 21; SMA 50; volume SMA 20 x 1.5; SL 1 %, TP 400 % of position_avg_price; 100 % of equity
    longCondition = crossover(ema9, ema21) and close > sma50 and volume > 1.5 x avgVolume -> entry Long;  shortCondition mirrored -> entry Short
    position_size > 0 -> exit(stop = avg x 0.99, limit = avg x 5.0);  position_size < 0 -> exit(stop = avg x 1.01, limit = avg x (1 - 4.0))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent from position_avg_price every bar from the fill bar's close, so it is fixed
      at the fill: ported as sl_stop 0.01 / tp_stop 4.0 (stated approximation: the source acts from the
      bar after the fill, the house from the fill, as #429494). The 400 % target is out of reach (the
      short's is a negative price), so trades end by the 1 % stop or a reversal (weird case). REVERSAL
      INTENDED. 100 % of equity is sizing. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 1 % stop from the fill.
    2 generic: PASS, EMA crossings with an SMA 50 trend filter on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483129_ema9_21_cross_sma50_volume_1pct_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.01, 0.02],
    "tp": [4.0, 0.05],
}
DEFAULT_PARAMS = {"sl": 0.01, "tp": 4.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    t = c.rolling(50).mean()
    vol_ok = v > v.rolling(20).mean() * 1.5
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & (c > t) & vol_ok
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & (c < t) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
