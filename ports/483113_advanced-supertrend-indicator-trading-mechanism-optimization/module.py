"""SuperTrend 0.25 / 6 line crossings on a trend change, broker days: the close crossing up through the line when the direction differs from its value two line changes back goes long, crossing down goes short; reversing, no other exit.
Port of FMZ strategy #483113 "Advanced Supertrend Indicator Trading Mechanism Optimization Strategy" (Supertrend Strategy with Money Ocean Trade).

FMZ source id: 483113

Source
    https://www.fmz.com/strategy/483113 (PineScript v5, FMZ last modified 2025-02-21 15:05:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-149), SuperTrend length 6, factor 0.25; 100 % of equity
    trendChanged = prevSupertrend not na and direction != nz(valuewhen(prevSupertrend != supertrend, direction, 1))
    trendChanged and close[1] < supertrend[1] and close > supertrend -> entry Long;  trendChanged and close[1] > supertrend[1] and close < supertrend -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * prevSupertrend is the previous bar's line, so the valuewhen condition is "the line changed on this
      bar", and occurrence 1 is the direction at the change before the latest one (0 by nz before two
      changes), as written. Entries only: each reverses the other side (REVERSAL INTENDED), no other exit.
      The 100 % of equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend line crossings on a direction change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_483113_supertrend0_25_6_line_cross_on_trend_change_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "supertrend_length": [6, 10],
    "supertrend_factor": [0.25, 1.0],
}
DEFAULT_PARAMS = {"supertrend_length": 6, "supertrend_factor": 0.25}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st, d = _supertrend(bars_df, float(p["supertrend_factor"]), int(p["supertrend_length"]))
    sv, dv = st.to_numpy(), d.to_numpy()
    m = len(sv)
    changed = np.zeros(m, dtype=bool)
    hist = []                                   # directions at the bars where the line changed
    for i in range(m):
        prev = sv[i - 1] if i >= 1 else np.nan
        cond = (not np.isnan(prev)) and (not np.isnan(sv[i])) and sv[i] != prev     # na != x is false
        if cond:
            hist.append(dv[i])
        ref = hist[-2] if len(hist) >= 2 else 0.0      # valuewhen(..., 1), nz -> 0
        changed[i] = (not np.isnan(prev)) and dv[i] != ref
    ch = pd.Series(changed, index=c.index)
    le = ch & (c.shift(1) < st.shift(1)) & (c > st)
    se = ch & (c.shift(1) > st.shift(1)) & (c < st)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
