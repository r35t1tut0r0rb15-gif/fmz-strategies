"""ATR trailing-stop bands with wick protection, broker days: when the band line flips (the price touching it from the
other side), the new state decides the side: a flip to "green" goes long, a flip to "red" goes short.
Port of FMZ strategy #429651 "基于ATR指标的自适应跟踪止损策略ATR-Trailing-Stop-Bands-Strategy" (ATR Trailing Stop Bands Strategy[R]).

FMZ source id: 429651

Source
    https://www.fmz.com/strategy/429651 (PineScript v2, FMZ last modified 2023-10-19 12:42:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 225-263), ATR 5 x 4, wick protection 30 (average)
    TS ratchets below lows (low - 4 atr5 - avg lower wick) or above highs (high + 4 atr5 + avg upper wick); a touch from the other side switches to the band
    pos = close[1] > TS[1] and low <= TS[1] ? 1 (red) : close[1] < TS[1] and high >= TS[1] ? -1 (green) : pos[1]
    green after red -> entry long, close short; red after green -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop line and bands are signals, not stop orders. The wick averages use the previous 30 bars'
      wicks (each from bar [1]). na ATR makes the line na (as Pine's max / min with na), restarting from 0.
    * Each flip reverses in one bar: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples and wick averages from the bars.
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

NAME = "fmz_429651_atr_band_flip"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [5, 14],
    "mult": [4.0, 2.5],
}
DEFAULT_PARAMS = {"atr_period": 5, "mult": 4.0, "length": 30}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _nmax(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else max(a, b)


def _nmin(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else min(a, b)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    upw = pd.Series(np.where(c <= o, h - o, h - c), index=c.index).shift(1).rolling(n).mean().to_numpy()
    low_w = pd.Series(np.where(c > o, o - lo, c - lo), index=c.index).shift(1).rolling(n).mean().to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    nl = (p["mult"] * _rma(tr, int(p["atr_period"]))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    ub, lb, ts = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    pos = np.zeros(m, dtype=np.int8)
    for i in range(m):
        z = lambda a: 0.0 if (i == 0 or np.isnan(a[i - 1])) else a[i - 1]  # noqa: E731
        ubp, lbp, tsp = z(ub), z(lb), z(ts)
        h1 = hv[i - 1] if i >= 1 else np.nan
        l1 = lv[i - 1] if i >= 1 else np.nan
        c1 = cv[i - 1] if i >= 1 else np.nan
        uraw, lraw = hv[i] + nl[i] + upw[i], lv[i] - nl[i] - low_w[i]
        ub[i] = _nmin(ubp, uraw) if (hv[i] < ubp and h1 < ubp) else uraw
        lb[i] = _nmax(lbp, lraw) if (lv[i] > lbp and l1 > lbp) else lraw
        if lv[i] > tsp and l1 > tsp:
            ts[i] = _nmax(tsp, lraw)
        elif hv[i] < tsp and h1 < tsp:
            ts[i] = _nmin(tsp, uraw)
        elif lv[i] <= tsp and c1 > tsp:
            ts[i] = ub[i - 1] if i >= 1 else np.nan
        elif hv[i] >= tsp and c1 < tsp:
            ts[i] = lb[i - 1] if i >= 1 else np.nan
        else:
            ts[i] = 0.0
        q = pos[i - 1] if i >= 1 else 0
        if c1 > tsp and lv[i] <= tsp:
            q = 1
        elif c1 < tsp and hv[i] >= tsp:
            q = -1
        pos[i] = q
    prev = np.concatenate(([0], pos[:-1]))
    idx = bars_df.index
    green_flip = (pos == -1) & (prev == 1)
    red_flip = (pos == 1) & (prev == -1)
    false = pd.Series(False, index=idx)
    return pd.Series(green_flip, index=idx), false, pd.Series(red_flip, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
