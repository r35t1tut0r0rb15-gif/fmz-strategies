"""Donchian 100 breakouts with an ATR trailing line exit, daily bars, long only: the close crossing over the previous bar's 100-bar high goes long; the close crossing under the ATR(10) x 3 trailing line
closes.
Port of FMZ strategy #445840 "Donchian Channel Breakout Strategy with ATRSL Trailing Stop" (Stock Trend USE THIS (Donchian breakout with ATRSL trail)).

FMZ source id: 445840

Source
    https://www.fmz.com/strategy/445840 (PineScript v4, FMZ last modified 2024-03-22 16:13:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-138), Donchian 100; slow ATR 10 x 3 trailing line on the close
    crossover(close, highest(100)[1]) -> entry Long;  Trail2 = ATR trailing line (nz seeds);  crossunder(close, Trail2) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest() / lowest() without a source use high / low; the breakout compares with the previous
      bar's channel, so the current bar is not in its own window. The trailing line follows the
      script's nz() seeds; it is a bar-close crossing, filled at the next open, not a stop order. Long
      only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian breakout with an ATR trailing-line exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445840_donchian100_break_atr_trail_cross_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "don_len": [100, 55],
    "atr_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"don_len": 100, "atr_mult": 3.0, "atr_len": 10}


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
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    sl = (float(p["atr_mult"]) * _rma(tr, int(p["atr_len"]))).to_numpy()
    sv = c.to_numpy(dtype=float)
    m = len(sv)
    trail = np.full(m, np.nan)
    for i in range(m):
        prev = trail[i - 1] if i > 0 and not np.isnan(trail[i - 1]) else 0.0
        s1 = sv[i - 1] if i > 0 else np.nan
        if sv[i] > prev and s1 > prev:
            trail[i] = _nmax(prev, sv[i] - sl[i])
        elif sv[i] < prev and s1 < prev:
            trail[i] = _nmin(prev, sv[i] + sl[i])
        else:
            trail[i] = sv[i] - sl[i] if sv[i] > prev else sv[i] + sl[i]
    tr_s = pd.Series(trail, index=c.index)
    up1 = h.rolling(int(p["don_len"])).max().shift(1)
    go = ((c > up1) & (c.shift(1) <= up1.shift(1))).to_numpy()
    out = ((c < tr_s) & (c.shift(1) >= tr_s.shift(1))).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
