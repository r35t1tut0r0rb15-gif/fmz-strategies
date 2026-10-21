"""Open price against three Supertrend lines with an ATR margin, broker days: when the open plus one ATR is above all three lines (factors 1, 2, 3) the state is long; otherwise, when the open is below every line plus
one ATR it is short; otherwise flat; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #436763 "三重超趋势Ichimoku云量化交易策略Triple-Supertrend-Ichimoku-Cloud-Quantitative-Trading-Strategy" (HyperTrend).

FMZ source id: 436763

Source
    https://www.fmz.com/strategy/436763 (PineScript v5, FMZ last modified 2023-12-27 15:22:40).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 169-248), Supertrend 10 / 1, 11 / 2, 12 / 3; ATR 14 (RMA)
    [supertrend1..3, direction1..3] = supertrend(factor, atrPeriod);  ATR = rma(tr(true), 14)
    if open + ATR > st1, st2, st3 -> entry L;  else if open < st1 + ATR, st2 + ATR, st3 + ATR -> entry S;  else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; a same-side entry while in the
      position is ignored (pyramiding 0). Comparisons with a line not yet formed are false, so the warm-up
      bars are flat. The Ichimoku cloud, the EMA and its smoothing line are plotted only (display none)
      and place no orders. The open is the signal bar's own open, known at its close. REVERSAL INTENDED.
      The percent-of-portfolio input is not used by the orders (stored). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend lines with an ATR margin.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused percent-of-portfolio input stored.
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

NAME = "fmz_436763_triple_supertrend_open_margin"
FAMILY = "supertrend"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [14, 21],
    "factor1": [1.0, 1.5],
}
DEFAULT_PARAMS = {"atr_len": 14, "factor1": 1.0, "atr1": 10, "atr2": 11, "factor2": 2.0, "atr3": 12,
                  "factor3": 3.0}


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


def _supertrend_line(h, lo, c, factor, n):
    """Line of Pine's built-in supertrend(factor, atrPeriod)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            up_dir = False
        elif st[i - 1] == ub[i - 1]:
            up_dir = cv[i] > ub[i]
        else:
            up_dir = not (cv[i] < lb[i])
        st[i] = lb[i] if up_dir else ub[i]
    return pd.Series(st, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sts = [_supertrend_line(h, lo, c, float(p[f]), int(p[a]))
           for f, a in (("factor1", "atr1"), ("factor2", "atr2"), ("factor3", "atr3"))]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = (h - lo).iloc[0]                    # tr(true): high - low on the first bar
    atr = _rma(tr, int(p["atr_len"]))
    long_s = (o + atr > sts[0]) & (o + atr > sts[1]) & (o + atr > sts[2])
    short_s = ~long_s & (o < sts[0] + atr) & (o < sts[1] + atr) & (o < sts[2] + atr)
    flat = ~long_s & ~short_s
    return long_s, flat, short_s, flat.copy()


def portfolio_kwargs(**params):
    return {}
