"""Capitulation bar buys, broker days, long only: a large red bar far below its SMA 20 (distance over twice its 100-bar
average), making a lower body low, with a 3-bar fast RSI under 10, goes long; a 20 % target from the signal close.
Adds are not ported.
Port of FMZ strategy #430846 "Momentum Breakout Identifies Strategy" (ONLY LONG V4 v1).

FMZ source id: 430846

Source
    https://www.fmz.com/strategy/430846 (PineScript v4, FMZ last modified 2023-11-02 14:39:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-296), fast RSI 3 under 10, body 2.5 x its SMA 20, distance 2 x its SMA 100, target 20 %, pyramiding 1000
    up = close < open and |close - sma20| > 2 sma(|close - sma20|, 100) and min(open, close) < min[1] and fastrsi < 10
         and body > 2.5 sma(body, 20) -> entry long (adds while long, pyramiding 1000)
    exit("TP", "long", limit = last signal close x 1.20), every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 1000: further signals add in the source; adds are not ported (one net position).
      The target is re-issued every bar from the latest signal's close, so a new signal while long
      moves it: rule 2, mark trailing_stop_pending; the port fixes it at 20 % of the fill (tp_stop 0.20).
    * The 2019 start is the author's window: dropped. Long only; Opposite entries cannot occur. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D".

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported; the moving target fixed at the fill (rule 2).
    2 generic: PASS, body and distance ratios, an RSI level and a percentage target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50 % of equity per entry and pyramiding 1000 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430846_capitulation_bar_long"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [20.0, 10.0],
    "body_mult": [2.5, 2.0],
}
DEFAULT_PARAMS = {"tp_pct": 20.0, "body_mult": 2.5, "rsi_len": 3, "rsi_level": 10, "dist_mult": 2.0}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    body = (c - o).abs()
    dist = (c - c.rolling(20).mean()).abs()
    mn = np.minimum(o, c)
    up = ((c < o) & (dist > dist.rolling(100).mean() * p["dist_mult"]) & (mn < mn.shift(1))
          & (_rsi(c, int(p["rsi_len"])) < p["rsi_level"]) & (body > body.rolling(20).mean() * p["body_mult"]))
    false = pd.Series(False, index=bars_df.index)
    return up.astype(bool), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
