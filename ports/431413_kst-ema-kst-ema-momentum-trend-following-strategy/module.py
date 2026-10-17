"""KST signal crosses with an EMA 50 filter, broker days: the KST crossing above its signal while below zero, with the close
above the EMA 50, goes long (mirror short); a 1 % trailing stop on the best close follows each position.
Port of FMZ strategy #431413 "基于KST指标和EMA指标的交易策略KST-EMA-Momentum-Trend-Following-Strategy" (Know Sure Thing and EMA Strategy by JLX).

FMZ source id: 431413

Source
    https://www.fmz.com/strategy/431413 (PineScript v4, FMZ last modified 2023-11-07 16:36:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 165-224), KST ROC 10 / 15 / 20 / 30, SMA 10 / 10 / 10 / 15, signal 9, EMA 50, trail 1 %
    kst = sma(roc10, 10) + 2 sma(roc15, 10) + 3 sma(roc20, 10) + 4 sma(roc30, 15); sig = sma(kst, 9)
    crossover(kst - sig, 0) and kst < 0 and close > ema50 -> entry long (mirror short)
    long: stop = max(close x 0.99, stop[1]) every bar -> exit(stop);  short: min(close x 1.01, stop[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is a ratchet on the bar closes: the house trail {"type": "percent", "pct": 0.01,
      "anchor": "close"} (the best close x 0.99, never retreating). Natively ported: mark
      trailing_stop. The house trail reads minute closes; the source's daily closes (stated).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house stop.
    2 generic: PASS, KST, an EMA and a percentage trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431413_kst_ema_trail"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [1.0, 3.0],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"trail_pct": 1.0, "ema_len": 50, "sig_len": 9}


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

    def sr(r, s):
        return (100 * (c - c.shift(r)) / c.shift(r)).rolling(s).mean()
    kst = sr(10, 10) + 2 * sr(15, 10) + 3 * sr(20, 10) + 4 * sr(30, 15)
    sig = kst.rolling(int(p["sig_len"])).mean()
    dlt = kst - sig
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    lg = ((dlt > 0) & (dlt.shift(1) <= 0) & (kst < 0) & (c > ema)).astype(bool)
    sh = ((dlt < 0) & (dlt.shift(1) >= 0) & (kst > 0) & (c < ema)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
