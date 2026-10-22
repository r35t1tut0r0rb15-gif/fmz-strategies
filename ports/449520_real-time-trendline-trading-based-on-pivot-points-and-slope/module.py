"""Breaks of sloped trendlines from confirmed 14-bar pivots, daily bars: a close above the falling line from the last pivot high goes long, a close below the rising line from the last pivot low goes short;
reversing.
Port of FMZ strategy #449520 "Real time Trendline Trading Based on Pivot Points and Slope" (only Ajay (trendlines with breaks, pivots and ATR slope)).

FMZ source id: 449520

Source
    https://www.fmz.com/strategy/449520 (PineScript v5, FMZ last modified 2024-04-26 15:34:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-196), swing lookback 14; slope ATR(14) / 14 x 1 (method Atr); backpaint on (plots only)
    upper = ph ? ph : upper - slope_ph;  lower = pl ? pl : lower + slope_pl;  upos = ph ? 0 : close > upper - slope_ph x 14 ? 1 : upos;  dnos mirrored
    upos > upos[1] -> entry Up Breakout (long);  dnos > dnos[1] -> entry Down Breakout (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(14, 14) are confirmed 14 bars after the pivot and used on that bar, as
      Pine returns them; each new pivot resets its line and slope (the ATR at confirmation). The
      backpaint option only shifts the plots. A same-bar long and short: the later short wins (as
      #437773). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots used once confirmed.
    2 generic: PASS, sloped trendline breakouts.
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

NAME = "fmz_449520_pivot_trendline_atr_slope_break_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "mult": [1.0, 2.0],
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


def _pivot(x, left, right, high):
    """Pine pivothigh / pivotlow (strict), the centre's value on the bar it is confirmed (right bars later)."""
    c = x.shift(right)
    ok = c.notna()
    for k in range(1, left + 1):
        ok &= (c > x.shift(right + k)) if high else (c < x.shift(right + k))
    for k in range(right):
        ok &= (c > x.shift(k)) if high else (c < x.shift(k))
    return c.where(ok)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    slope = (_rma(tr, n) / n * float(p["mult"])).to_numpy()
    ph = _pivot(h, n, n, True).to_numpy()
    pl = _pivot(lo, n, n, False).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upper = lower = 0.0
    s_ph = s_pl = 0.0
    upos = dnos = 0
    up_b, dn_b = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            hph = not np.isnan(ph[i]) and ph[i] != 0
            hpl = not np.isnan(pl[i]) and pl[i] != 0
            if hph:
                s_ph = slope[i]
            if hpl:
                s_pl = slope[i]
            upper = ph[i] if hph else upper - s_ph
            lower = pl[i] if hpl else lower + s_pl
            u_prev, d_prev = upos, dnos
            if hph:
                upos = 0
            elif cv[i] > upper - s_ph * n:
                upos = 1
            if hpl:
                dnos = 0
            elif cv[i] < lower + s_pl * n:
                dnos = 1
            up_b[i] = i > 0 and upos > u_prev           # upos[1] is na on the first bar
            dn_b[i] = i > 0 and dnos > d_prev
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up_b & ~dn_b, index=ix), false, pd.Series(dn_b, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
