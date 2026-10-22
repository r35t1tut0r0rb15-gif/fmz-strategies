"""Trendline breaks, daily bars: from each 14-bar pivot high a line falls by ATR 14 / 14 per bar; a close over its projection goes long, and the mirror from pivot lows going short; reversing.
Port of FMZ strategy #475595 "Multi Trendline Breakout Momentum Quantitative Strategy" (Trendlines with Breaks Strategy [AlexGoldHunter]).

FMZ source id: 475595

Source
    https://www.fmz.com/strategy/475595 (PineScript v5, FMZ last modified 2024-12-20 14:26:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-165), swing lookback 14; slope ATR / 14 x 1.0 (Atr method)
    ph = pivothigh(14, 14);  slope_ph := ph ? slope : slope_ph;  upper := ph ? ph : upper - slope_ph;  upos := ph ? 0 : close > upper - slope_ph x 14 ? 1 : upos;  mirror for lower / dnos;  upos > upos[1] -> entry Buy;  dnos > dnos[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines and break states are the source's var recursions (a loop; pivots strict, confirmed 14
      bars later). The backpaint option only moves plots. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot trendline breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475595_pivot_trendline_atr_slope_break_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "mult": [1.0, 0.5],
}
DEFAULT_PARAMS = {"length": 14, "mult": 1.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    slope = (_atr(bars_df, n) / n * float(p["mult"])).to_numpy(dtype=float)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ph, pl = _pivot(hv, 1, n), _pivot(lv, -1, n)
    m = len(cv)
    upos_a, dnos_a = np.zeros(m), np.zeros(m)
    upper = lower = 0.0
    sph = spl = 0.0
    upos = dnos = 0
    for i in range(m):
        if ph[i]:
            sph = slope[i]
        if pl[i]:
            spl = slope[i]
        upper = hv[i - n] if ph[i] else upper - sph
        lower = lv[i - n] if pl[i] else lower + spl
        upos = 0 if ph[i] else (1 if cv[i] > upper - sph * n else upos)
        dnos = 0 if pl[i] else (1 if cv[i] < lower + spl * n else dnos)
        upos_a[i], dnos_a[i] = upos, dnos
    ix = bars_df.index
    u, d = pd.Series(upos_a, index=ix), pd.Series(dnos_a, index=ix)
    le = u > u.shift(1)
    se = d > d.shift(1)
    false = pd.Series(False, index=ix)
    return le & ~se, false, se, false.copy()     # the later short entry wins a bar with both


def portfolio_kwargs(**params):
    return {}
