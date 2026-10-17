"""Volatility-stop swings, long only, broker days: the close above the volatility stop (1 x ATR 3 from the swing extreme,
flipping when the close crosses it) holds a long; the close below it closes the long (short entries are not allowed, so
they only close the long).
Port of FMZ strategy #432766 "Dual direction Volatility Swallowing Strategy" (BCH Swinger v1).

FMZ source id: 432766

Source
    https://www.fmz.com/strategy/432766 (PineScript v2, FMZ last modified 2023-11-21 12:04:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 139-169), ATR 3, mult 1, direction 1 (long only)
    vstop: max_ / min_ track the close since the last flip; stop = up ? max - atr : min + atr; vstop ratchets with it; flip when the close crosses
    close > vstop -> entry long ("BUY");  close < vstop -> entry short ("SELL")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(long) with direction 1: a short entry is not allowed and acts
      only to close the long (Pine's rule), so the port is long only. The volatility stop is coded as
      written, nz included (min_ starts at 0, the trend starts up). ATR is Wilder; the loop starts once
      it exists.
    * withinTimeRange is always true. Long only; Opposite entries cannot occur. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR volatility stop crossed on the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, the commission and the direction setting stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432766 (2 members, best partner #441051, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432766_volatility_stop_swing_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 10],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 3, "mult": 1.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["length"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["mult"])
    m = len(cv)
    vs = np.full(m, np.nan)
    mx, mn, up, vprev = 0.0, 0.0, True, 0.0
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        max1, min1 = max(mx, cv[i]), min(mn, cv[i])
        stop = max1 - k * atr[i] if up else min1 + k * atr[i]
        v1 = max(vprev, stop) if up else min(vprev, stop)
        new_up = cv[i] - v1 >= 0
        changed = new_up != up
        mx = cv[i] if changed else max1
        mn = cv[i] if changed else min1
        vprev = (mx - k * atr[i] if new_up else mn + k * atr[i]) if changed else v1
        up = new_up
        vs[i] = vprev
    vss = pd.Series(vs, index=c.index)
    le = (c > vss).astype(bool)
    lx = (c < vss).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
