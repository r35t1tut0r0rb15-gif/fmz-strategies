"""MACD crosses after RSI extremes, long only, broker days: the MACD (12 / 26) crossing above its EMA 9 signal with the
RSI 14 at or under 35 on any of the last six bars goes long; crossing below it with the RSI at or over 80 on any of the
last six bars closes it.
Port of FMZ strategy #432657 "Double Strong Indicators Strategy" (MACD and RSI (MACD&RSI)).

FMZ source id: 432657

Source
    https://www.fmz.com/strategy/432657 (PineScript v5, FMZ last modified 2023-11-20 09:47:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 156-183), MACD 12 / 26 / 9, RSI 14, oversold 35, overbought 80
    wasOversold = rsi <= 35 on any of the bars t..t-5;  wasOverbought = rsi >= 80 on any of them
    cross(macd, signal) and macd > signal and wasOversold -> entry long;  cross and macd < signal and wasOverbought -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cross flags are the average of MACD and signal when a cross happens (na otherwise); used as
      conditions they are true on a cross (a value of exactly 0 would read false). The signal is the
      EMA 9 of the MACD line. The RSI is the source's own (Wilder; 100 with no down move, 0 with no
      up move). Long only; Opposite entries cannot occur. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crosses and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432657 (2 members, best partner #439758, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432657_macd_cross_after_rsi_extreme"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [35, 30],
    "overbought": [80, 70],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "rsi_len": 14, "oversold": 35, "overbought": 80, "memory": 6}


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
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(~((up == 0) & (dn != 0)), 0.0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    k = int(p["memory"])
    was_os = (r <= float(p["oversold"])).astype(float).rolling(k, min_periods=1).max() > 0
    was_ob = (r >= float(p["overbought"])).astype(float).rolling(k, min_periods=1).max() > 0
    crs = ((macd > sig) & (macd.shift(1) <= sig.shift(1))) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)))
    nz = (macd + sig) != 0
    le = (crs & (macd > sig) & nz & was_os).astype(bool)
    lx = (crs & (macd < sig) & nz & was_ob).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
