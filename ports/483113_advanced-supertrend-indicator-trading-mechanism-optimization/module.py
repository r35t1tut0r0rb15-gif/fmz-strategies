"""Close crossing a tight Supertrend (6, 0.25) on a direction change, always in the market, daily (broker-day) bars:
when the Supertrend direction differs from the direction at the previous change of the line and the close crosses
above the line, go long; crossing below, go short.
Port of FMZ strategy #483113 "高级超趋势指标交易机制优化策略-Advanced-Supertrend-Indicator-Trading-Mechanism-Optimization-Strategy" (Supertrend Strategy with Money Ocean Trade).

FMZ source id: 483113

Source
    https://www.fmz.com/strategy/483113 (PineScript v5, FMZ last modified 2025-02-21 15:05:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 111-140), Supertrend length 6, factor 0.25
    trendChanged = not na(prevSupertrend) and direction != nz(valuewhen(prevSupertrend != supertrend, direction, 1))
    long = trendChanged and close[1] < supertrend[1] and close > supertrend (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as TradingView documents it (pine_supertrend). prevSupertrend is the previous bar's line, so the
      valuewhen condition is "the line changed on this bar"; valuewhen(..., 1) is the direction on the second most
      recent such bar (this bar counted), nz -> 0 before there is one. A comparison with na is false.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. Daily bars are broker days (17:00 America/New_York)
      stamped with their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend (ATR bands).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_483113_supertrend_change_cross_1d"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [0.25, 1.0],
    "length": [6, 10],
}
DEFAULT_PARAMS = {"factor": 0.25, "length": 6}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _supertrend_pine(bars_df, factor, n):
    """ta.supertrend (pine_supertrend): (line, direction); nan comparisons are false, as in Pine."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    st, dr = np.full(m, np.nan), np.ones(m)
    prev_u = prev_l = prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        pl = 0.0 if np.isnan(prev_l) else prev_l               # nz(lowerBand[1])
        pu = 0.0 if np.isnan(prev_u) else prev_u
        pc = c[i - 1] if i > 0 else np.nan
        lw = lw if (lw > pl or pc < pl) else pl
        up = up if (up < pu or pc > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        st[i], dr[i] = (lw if d == -1 else up), d
        prev_u, prev_l, prev_st = up, lw, st[i]
    return st, dr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"].to_numpy(dtype=float)
    st, dr = _supertrend_pine(bars_df, float(p["factor"]), int(p["length"]))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    changes = []                                   # directions on bars where the line changed
    for i in range(1, m):
        prev = st[i - 1]
        if not np.isnan(prev) and not np.isnan(st[i]) and prev != st[i]:
            changes.append(dr[i])
        ref = changes[-2] if len(changes) >= 2 else 0.0
        changed = (not np.isnan(prev)) and dr[i] != ref
        if changed and not np.isnan(st[i]):
            if c[i - 1] < prev and c[i] > st[i]:
                le[i] = True
            elif c[i - 1] > prev and c[i] < st[i]:
                se[i] = True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
