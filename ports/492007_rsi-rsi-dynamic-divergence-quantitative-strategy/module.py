"""Regular RSI 14 divergences at confirmed 5 / 5 RSI pivots 5 to 60 bars apart, broker days: a lower price low with a higher RSI low goes long, a higher price high with a lower RSI high goes short; reversing (the per-bar swing bracket is pending).
Port of FMZ strategy #492007 "RSI动态背离量化策略-RSI-Dynamic-Divergence-Quantitative-Strategy" (RSI Divergence Strategy - AliferCrypto).

FMZ source id: 492007

Source
    https://www.fmz.com/strategy/492007 (PineScript v6, FMZ last modified 2025-04-25 14:57:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-219), RSI 14; pivots 5 / 5; range 5-60; SL/TP method Swing (20-bar extreme -/+ 1 %, RR 2); 10 % of equity
    pivot low of rsi (5, 5) and low[5] < previous pivot's low[5] and rsi[5] > previous pivot's rsi and 5 <= bars since the previous pivot <= 60 -> entry Long;  mirror on pivot highs -> entry Short
    held: every bar exit(stop = lowest(low, 20) x 0.99, limit = avg + 2 (avg - stop)) for Long;  mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is known at its confirmation bar, 5 bars after the RSI extreme (strict on both sides); the
      previous pivot's values come from valuewhen(..., 1) and the spacing from barssince one bar back,
      followed in a loop. The exit is re-sent every bar from the current 20-bar swing, so the bracket
      follows the price: not ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite
      entry is the exit. An entry on the other side reverses (REVERSAL INTENDED). Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent swing bracket pending.
    2 generic: PASS, RSI pivot divergences.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_492007_rsi14_pivot5_divergence_reversal"
FAMILY = "rsi_divergence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookLeft": [5, 3],
    "rangeUpper": [60, 30],
}
DEFAULT_PARAMS = {"lookLeft": 5, "rangeUpper": 60, "lookRight": 5, "rangeLower": 5, "rsiLength": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _pivot(x, side, left, right):
    """Strict pivot of x at t - right, confirmed at t (Pine ta.pivothigh / pivotlow)."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsiLength"]))
    lb, rb = int(p["lookLeft"]), int(p["lookRight"])
    pl, ph = _pivot(r, -1, lb, rb), _pivot(r, 1, lb, rb)
    rr = r.shift(rb).to_numpy()
    lr, hr = lo.shift(rb).to_numpy(), h.shift(rb).to_numpy()
    lo_lim, hi_lim = int(p["rangeLower"]), int(p["rangeUpper"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_l = last_h = -1
    prev_l_r = prev_l_p = prev_h_r = prev_h_p = np.nan
    for i in range(m):
        if pl[i]:
            gap = (i - 1 - last_l) if last_l >= 0 else np.nan
            ok = lo_lim <= gap <= hi_lim
            le[i] = bool(ok and lr[i] < prev_l_p and rr[i] > prev_l_r)
            prev_l_r, prev_l_p, last_l = rr[i], lr[i], i
        if ph[i]:
            gap = (i - 1 - last_h) if last_h >= 0 else np.nan
            ok = lo_lim <= gap <= hi_lim
            se[i] = bool(ok and hr[i] > prev_h_p and rr[i] < prev_h_r)
            prev_h_r, prev_h_p, last_h = rr[i], hr[i], i
    le_s, se_s = pd.Series(le, index=c.index), pd.Series(se, index=c.index)
    false = pd.Series(False, index=c.index)
    return le_s & ~se_s, false, se_s, false.copy()


def portfolio_kwargs(**params):
    return {}
