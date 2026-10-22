"""Double-smoothed Heikin-Ashi open / close crossings, long only, broker days: the EMA 100 of the EMA 50 of the Heikin-Ashi close crossing over that of the open goes long, crossing under closes; each trade has a
7.5 % stop.
Port of FMZ strategy #439378 "Cryptocurrency Trend Following Strategy Based on Heiken Ashi" (CRYPTO HA Strategy).

FMZ source id: 439378

Source
    https://www.fmz.com/strategy/439378 (PineScript v4, FMZ last modified 2024-01-19 17:40:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-207), EMA 50 then EMA 100 on Heikin-Ashi candles; only long on, original (reversing) off; stop 0.075 of the close in ticks; date window true
    o = ema(open, 50), c = ema(close, 50) on the Heikin-Ashi ticker;  o2 = ema(o, 100);  c2 = ema(c, 100);  buy = o2 < c2 and o2[1] > c2[1];  sell = o2 > c2 and o2[1] < c2[1]
    entry long when buy;  close long when sell;  exit(loss = close x 0.075 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi candles are built from the module's own bars (close = ohlc4, open = the mean of the
      previous HA open and close, the first one (open + close) / 2); security() on the same period reads
      the same bar. The stop is 7.5 % of the close in ticks, measured from the fill: the port reads it as
      a fixed 7.5 % of the entry fill (as #437751). Long only. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: mark coarse_bar_stop. The 100 % of equity size and commission are
      sizing. Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: PASS, smoothed Heikin-Ashi crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439378_smoothed_heikin_ashi_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma1_len": [50, 20],
    "ma2_len": [100, 50],
}
DEFAULT_PARAMS = {"ma1_len": 50, "ma2_len": 100, "sl": 0.075}


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


def _heikin_ashi(bars_df):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    return pd.Series(ho, index=bars_df.index), pd.Series(hc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ho, hc = _heikin_ashi(bars_df)
    n1, n2 = int(p["ma1_len"]), int(p["ma2_len"])
    o2 = ho.ewm(span=n1, adjust=False).mean().ewm(span=n2, adjust=False).mean()
    c2 = hc.ewm(span=n1, adjust=False).mean().ewm(span=n2, adjust=False).mean()
    buy = (o2 < c2) & (o2.shift(1) > c2.shift(1))
    sell = (o2 > c2) & (o2.shift(1) < c2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
