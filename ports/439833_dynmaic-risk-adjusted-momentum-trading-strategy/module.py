"""Normalised-price HMA crossings with an ATR stop, broker days: the cumulative sum of volatility-normalised returns crossing over its HMA 100 goes long, crossing under goes short; each trade has a stop one
average range (14) from the fill; reversing.
Port of FMZ strategy #439833 "Dynmaic Risk Adjusted Momentum Trading Strategy" (Crunchster's Normalised Trend Strategy).

FMZ source id: 439833

Source
    https://www.fmz.com/strategy/439833 (PineScript v5, FMZ last modified 2024-01-24 11:13:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-229), normalisation 14; HMA 100, offset 0; long and short on; stop multiple 1; leverage 1, vol target 10 %, compounding off
    nRet = change(close) / stdev(change(close), 14);  nPrice = cum(nRet);  HMA = wma(2 wma(nPrice, 50) - wma(nPrice, 100), 10)
    crossover(nPrice, HMA) -> entry Go Long!, crossunder -> close (immediately) and entry Go Short!;  exit(stop = entry - openN x 1) (openN = sma(high - low, 14) when the position opens from flat)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cumulative sum starts with the data, but an HMA is linear in its input, so a constant offset
      moves both lines alike and the crossings do not depend on the start. The script's "true range"
      uses the current close, so it is the bar range. The close with immediately = true is read at the
      next open with the reversing entry (house fill). The stop distance is taken from the signal bar as
      #434998: sl_stop = 1 x sma(high - low, 14) / close, shifted one bar inside stops() and re-based on
      the fill (the script keeps the first value through direct reversals: stated approximation). The
      volatility-target quantity is sizing. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker
      days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the signal bar.
    2 generic: PASS, normalised price and its HMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the volatility-target size, leverage and compounding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439833_normalised_price_hma_cross_range_stop"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hlength": [100, 50],
    "stop_multiple": [1.0, 2.0],
}
DEFAULT_PARAMS = {"hlength": 100, "stop_multiple": 1.0, "length": 14, "atr_len": 14}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    with np.errstate(divide="ignore", invalid="ignore"):
        nret = d / d.rolling(int(p["length"])).std(ddof=0)
    nret = nret.where(np.isfinite(nret))
    npx = pd.Series(np.nancumsum(nret.to_numpy()), index=c.index).where(nret.notna().cummax())
    n = int(p["hlength"])
    hma = _wma(2 * _wma(npx, n // 2) - _wma(npx, n), int(round(np.sqrt(n))))
    up = (npx > hma) & (npx.shift(1) <= hma.shift(1))
    dn = (npx < hma) & (npx.shift(1) >= hma.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rng = (bars_df["high"] - bars_df["low"]).rolling(int(p["atr_len"])).mean()
    sl = float(p["stop_multiple"]) * rng / bars_df["close"]
    return {"sl_stop": sl.where(sl > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
