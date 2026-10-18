"""Hand-built Supertrend line crossings, broker days: a close crossing up through the trend line goes long, a close crossing
down through it goes short (reversing); factor 3, ATR 7.
Port of FMZ strategy #435269 "Supertrend Blind Following Strategy" (Supertrend blind follow).

FMZ source id: 435269

Source
    https://www.fmz.com/strategy/435269 (PineScript v2, FMZ last modified 2023-12-13 16:49:44).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 189-219), Factor 3, Pd 7; TrendUp / TrendDown ratchets; Tsl = the active line
    Up = hl2 - Factor atr(Pd);  Dn = hl2 + Factor atr(Pd);  TrendUp = close[1] > TrendUp[1] ? max(Up, TrendUp[1]) : Up;  TrendDown = close[1] < TrendDown[1] ? min(Dn, TrendDown[1]) : Dn
    Trend = close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : nz(Trend[1], 1);  Tsl = Trend == 1 ? TrendUp : TrendDown
    cross(close, Tsl) and close > Tsl -> entry long;  cross(Tsl, close) and close < Tsl -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is a crossing in either direction; with the side test it is a crossing up (long) or
      down (short) of the active line. The ATR is Wilder's (rma of the true range). strategy.entry
      reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility trend line.
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

NAME = "fmz_435269_supertrend_line_cross"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "pd": [7, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "pd": 7}


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
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["pd"]), adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    f = float(p["factor"])
    up, dn = hl2 - f * atr, hl2 + f * atr
    tu, td, tsl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m)
    for i in range(m):
        if i == 0:
            tu[i], td[i] = up[i], dn[i]
            tsl[i] = tu[i]
            continue
        tu[i] = max(up[i], tu[i - 1]) if (cv[i - 1] > tu[i - 1]) else up[i]
        td[i] = min(dn[i], td[i - 1]) if (cv[i - 1] < td[i - 1]) else dn[i]
        if cv[i] > td[i - 1]:
            trend[i] = 1
        elif cv[i] < tu[i - 1]:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1]
        tsl[i] = tu[i] if trend[i] == 1 else td[i]
    t1 = np.concatenate(([np.nan], tsl[:-1]))
    c1v = np.concatenate(([np.nan], cv[:-1]))
    with np.errstate(invalid="ignore"):
        crossed = ((cv > tsl) & (c1v <= t1)) | ((cv < tsl) & (c1v >= t1))
        lg = crossed & (cv > tsl)
        sh = crossed & (cv < tsl)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lg, index=ix), false, pd.Series(sh, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
