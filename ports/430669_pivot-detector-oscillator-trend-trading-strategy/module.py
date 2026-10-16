"""Pivot detector oscillator (Siligardos, HPotter), broker days: RSI 14 rescaled to 35-85 above the SMA 200 or to 20-70
below it; above its midline (50) holds a long, below holds a short.
Port of FMZ strategy #430669 "Pivot Detector Oscillator Trend Trading Strategy" (The Pivot Detector Oscillator, by Giorgos E. Siligardos).

FMZ source id: 430669

Source
    https://www.fmz.com/strategy/430669 (PineScript v2, FMZ last modified 2023-10-31 14:47:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 213-247), SMA 200, RSI 14, midline 50
    nRes = close > sma200 ? (rsi - 35) / 50 : (rsi - 20) / 50
    nRes x 100 > 50 -> 1 (entry long);  nRes x 100 < 50 -> -1 (entry short);  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a rescaled RSI and a moving average.
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

NAME = "fmz_430669_pivot_detector_oscillator"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ma": [200, 100],
    "length_rsi": [14, 7],
}
DEFAULT_PARAMS = {"length_ma": 200, "length_rsi": 14, "mid": 50}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["length_ma"])).mean()
    r = _rsi(c, int(p["length_rsi"]))
    res = pd.Series(np.where(c > ma, (r - 35) / 50, np.where(c <= ma, (r - 20) / 50, 0.0)), index=c.index)
    res = res.where(ma.notna() & r.notna()) * 100
    v = res.to_numpy()
    mid = float(p["mid"])
    m = len(v)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if v[i] > mid:
            pos = 1
        elif v[i] < mid:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
