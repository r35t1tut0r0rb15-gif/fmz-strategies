"""Hull trend with a Kalman-style smoother, broker days: the smoothed "HMA3" of the close crossing above the smoothed HMA 24
of hl2 goes long, crossing below goes short.
Port of FMZ strategy #430775 "Hull Moving Average and Kalman Filter Based Trend Tracking Strategy" (Hull Trend with Kahlman Strategy Backtest).

FMZ source id: 430775

Source
    https://www.fmz.com/strategy/430775 (PineScript v4, FMZ last modified 2023-11-01 17:10:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-212), HMA 24 of hl2, HMA3 (half length 12) of close, gain 10000, Kalman on
    a = kahlman(hma(hl2, 24)); b = kahlman(wma(wma(close, 4) x 3 - wma(close, 6) - wma(close, 12), 12))
    kahlman: dk = x - kf[1]; kf = kf[1] + dk sqrt(2 g) + velo, velo = velo[1] + g dk   (g = gain / 10000 = 1)
    b > a and b[1] < a[1] -> entry long;  a > b and a[1] < b[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * hma3 uses the script-level length (24) and close, not its arguments, as written: p = 12,
      wma lengths 4 / 6 / 12 (integer division). nz(kf[1], x) starts each filter at its input.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed moving averages.
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

NAME = "fmz_430775_hull_kalman_cross"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [24, 48],
    "gain": [10000, 5000],
}
DEFAULT_PARAMS = {"length": 24, "gain": 10000}


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
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def _kahlman(x, g):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    kf, velo = np.nan, 0.0
    for i in range(len(v)):
        prev = v[i] if np.isnan(kf) else kf
        dk = v[i] - prev
        smooth = prev + dk * np.sqrt(g * 2)
        velo = velo + g * dk if not np.isnan(dk) else velo
        kf = smooth + velo
        out[i] = kf
    return pd.Series(out, index=x.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    g = float(p["gain"]) / 10000
    half = int(n / 2)
    a = _kahlman(_hma((h + lo) / 2, n), g)
    h3 = _wma(_wma(c, int(half / 3)) * 3 - _wma(c, int(half / 2)) - _wma(c, half), half)
    b = _kahlman(h3, g)
    up = ((b > a) & (b.shift(1) < a.shift(1))).to_numpy()
    dn = ((a > b) & (a.shift(1) < b.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
