"""Heikin-Ashi colour with a Bollinger width filter, broker days: a run of green Heikin-Ashi candles (1 by default) while the width of the 4-bar, 20-deviation Bollinger band is above a threshold goes long, a run of
red ones goes short; entries are sent on every qualifying bar, reversing.
Port of FMZ strategy #436772 "Bollinger Bands Heiken Ashi Short term Trading Strategy" (ANCIENT TECHNOLOGY).

FMZ source id: 436772

Source
    https://www.fmz.com/strategy/436772 (PineScript v4, FMZ last modified 2023-12-27 15:52:08).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 170-212), consecutive candles 1, Bollinger length 4, multiplier 20, volatility threshold 0.2 (price units)
    upper / lower = sma(close, 4) +- 20 stdev(close, 4);  bandWidth = upper - lower;  haOpen := na ? (open + close) / 2 : (haOpen + haClose) / 2;  haClose := ohlc4
    long = the last N candles green and bandWidth > 0.2 -> entry Long;  short = the last N red and bandWidth > 0.2 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.2 threshold is a PRICE-UNIT width; the port tests the width as a fraction of the
      close (bandWidth / close > vol_frac); 0.0000067 reads 0.2 on BTC near 30000 (a filter that almost
      always passes there), 0.5 a filter that bites (the 40-deviation width is usually large). stdev is
      the population deviation. haOpen uses the previous bar's haClose (the update order of the script).
      A same-side entry while in the position is ignored (pyramiding 0). REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit width threshold -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436772_heikin_ashi_bollinger_width"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "consecutive": [1, 2],
    "vol_frac": [0.0000067, 0.5],
}
DEFAULT_PARAMS = {"consecutive": 1, "vol_frac": 0.0000067, "length_bb": 4, "mult_bb": 20.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length_bb"])
    width = 2.0 * float(p["mult_bb"]) * c.rolling(n).std(ddof=0)
    wide = (width / c) > float(p["vol_frac"])
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ha_c = ((o + h + lo + c) / 4).to_numpy()
    m = len(cv)
    ha_o = np.full(m, np.nan)
    for i in range(m):
        ha_o[i] = (ov[i] + cv[i]) / 2 if i == 0 or np.isnan(ha_o[i - 1]) else (ha_o[i - 1] + ha_c[i - 1]) / 2
    green = pd.Series(ha_c > ha_o, index=c.index).astype(float)
    red = pd.Series(ha_c < ha_o, index=c.index).astype(float)
    k = int(p["consecutive"])
    all_green = green.rolling(k, min_periods=1).sum() == k
    all_red = red.rolling(k, min_periods=1).sum() == k
    false = pd.Series(False, index=bars_df.index)
    return all_green & wide, false, all_red & wide, false.copy()


def portfolio_kwargs(**params):
    return {}
