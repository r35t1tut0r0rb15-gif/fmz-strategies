"""OTT (optimized trend tracker) crossings on a VIDYA-style VAR average, broker days, long only: the close crossing over the OTT line (VAR 5, 1 %) goes long, crossing under closes.
Port of FMZ strategy #442010 "Dual Moving Average Intelligent Tracking Trading Strategy" (BugRA_Trade_Strategy).

FMZ source id: 442010

Source
    https://www.fmz.com/strategy/442010 (PineScript v4, FMZ last modified 2024-02-18 15:58:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-230), length 5; percent 1; MA type VAR; wt inputs 10 / 21 (unused); date inputs (isDateInRange always true)
    VAR = nz(a |CMO| close + (1 - a |CMO|) nz(VAR[1])), a = 2 / 6, CMO = (sum up - sum down) / (sum up + sum down) over 5
    longStop = VAR - 1 % ratcheted up, shortStop = VAR + 1 % ratcheted down;  dir flips on VAR crossing the previous stops;  MT = dir == 1 ? longStop : shortStop;  OTT = VAR > MT ? MT x 201 / 200 : MT x 199 / 200
    crossover(close, OTT) -> entry Long;  crossunder(close, OTT) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VAR recursion keeps its nz() wrapping as written (an undefined CMO, as in the first bars, resets
      it to 0). isDateInRange() is always true. Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OTT crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442010 (2 members, best partner #442114, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442010_ott_var_cross_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
    "percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 5, "percent": 1.0}


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


def _ott(c, n, pct):
    d = c.diff()
    ud = d.clip(lower=0).where(d.notna(), 0.0).rolling(n).sum().to_numpy()
    dd = (-d).clip(lower=0).where(d.notna(), 0.0).rolling(n).sum().to_numpy()
    cv = c.to_numpy(dtype=float)
    a = 2.0 / (n + 1)
    m = len(cv)
    ott = np.full(m, np.nan)
    var = 0.0
    ls = ss = np.nan
    dr = 1
    for i in range(m):
        den = ud[i] + dd[i]
        if np.isnan(den) or den == 0:
            var = 0.0
        else:
            k = a * abs((ud[i] - dd[i]) / den)
            var = k * cv[i] + (1 - k) * var
        fark = var * pct * 0.01
        lc, sc = var - fark, var + fark
        lp = lc if np.isnan(ls) else ls
        sp = sc if np.isnan(ss) else ss
        ls = max(lc, lp) if var > lp else lc
        ss = min(sc, sp) if var < sp else sc
        if dr == -1 and var > sp:
            dr = 1
        elif dr == 1 and var < lp:
            dr = -1
        mt = ls if dr == 1 else ss
        ott[i] = mt * (200 + pct) / 200 if var > mt else mt * (200 - pct) / 200
    return pd.Series(ott, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    o = _ott(c, int(p["length"]), float(p["percent"]))
    up = (c > o) & (c.shift(1) <= o.shift(1))
    dn = (c < o) & (c.shift(1) >= o.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
