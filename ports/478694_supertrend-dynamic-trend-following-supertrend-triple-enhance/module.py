"""SuperTrend (ATR 16 x 3.02) flips on the EMA 49 side, broker days, entries only from flat: a flip up above the EMA goes long, a flip down below it goes short; a close through a 50-point stop from the signal close, or through a 70-point close trail that starts once the close is 70 points in profit, closes.
Port of FMZ strategy #478694 "动态趋势追踪与均线辅助的SuperTrend三重优化策略-Dynamic-Trend-Following-SuperTrend-Triple-Enhancement-Strategy" (nifty supertrend triton).

FMZ source id: 478694

Source
    https://www.fmz.com/strategy/478694 (PineScript v5, FMZ last modified 2025-01-17 14:37:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-160), SuperTrend ATR 16, factor 3.02; EMA 49; trail 70 points after 70 points; initial stop 50 points; 100 % of equity
    change(direction) < 0 and close > ema49 and flat -> entry Buy, entry := close, stop := close - 50, trail := na;  change(direction) > 0 and close < ema49 and flat -> entry Sell (mirror)
    long: close <= stop -> close;  close - entry >= 70 -> trail := max(trail, close - 70);  close < trail -> close  (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are bar-close tests on the close, filled at the next open, so a loop follows them as
      written. The 50 / 70 points are price amounts, ported as fractions of 42000 of the signal close
      (0.00119 / 0.00167). The SuperTrend is Pine's reference ta.supertrend (a change below zero is a flip
      to the up-trend). Opposite entries cannot occur (entries only from flat). The 100 % of equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend flips on the EMA side with point stops and a close trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478694_supertrend16_flip_ema49_point_stop_close_trail_flat_only"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.02, 2.0],
    "ma_period": [49, 100],
}
DEFAULT_PARAMS = {"factor": 3.02, "ma_period": 49, "atr_period": 16, "stop_frac": 1.19048e-03, "trail_frac": 1.66667e-03}


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
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[1]
    chg = d.diff()
    e = c.ewm(span=int(p["ma_period"]), adjust=False).mean()
    lc = ((chg < 0) & (c > e)).to_numpy()
    sc = ((chg > 0) & (c < e)).to_numpy()
    cv = c.to_numpy(dtype=float)
    fs, ft = float(p["stop_frac"]), float(p["trail_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    entry = init = trail = a_t = np.nan
    for i in range(m):
        pos = nxt
        if lc[i] and pos == 0:
            le[i], nxt = True, 1
            entry, trail = cv[i], np.nan
            init, a_t = cv[i] - fs * cv[i], ft * cv[i]
        if sc[i] and pos == 0:
            se[i], nxt = True, -1
            entry, trail = cv[i], np.nan
            init, a_t = cv[i] + fs * cv[i], ft * cv[i]
        if pos == 1:
            hit = cv[i] <= init
            if cv[i] - entry >= a_t:
                trail = cv[i] - a_t if np.isnan(trail) else max(trail, cv[i] - a_t)
            if hit or (not np.isnan(trail) and cv[i] < trail):
                lx[i], nxt = True, 0
        elif pos == -1:
            hit = cv[i] >= init
            if entry - cv[i] >= a_t:
                trail = cv[i] + a_t if np.isnan(trail) else min(trail, cv[i] + a_t)
            if hit or (not np.isnan(trail) and cv[i] > trail):
                sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
