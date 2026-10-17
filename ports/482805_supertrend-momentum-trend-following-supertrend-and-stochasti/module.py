"""Stochastic crosses of 20 (80) by SuperTrend direction, closed when the direction flips or the stochastic leaves the
opposite extreme, two-day bars.
Port of FMZ strategy #482805 "动量趋势型SuperTrend与随机指标交叉策略-Momentum-Trend-Following-SuperTrend-and-Stochastic-Crossover-Strategy" (SuperTrend + Stochastic Strategy).

FMZ source id: 482805

Source
    https://www.fmz.com/strategy/482805 (PineScript v5, FMZ last modified 2025-02-20 14:55:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-155), SuperTrend 3 / 10, stochastic 14 / 3 / 3 (80 / 20)
    long = direction == 1 and crossover(k, 20) -> entry long
    short = direction == -1 and crossunder(k, 80) -> entry short
    direction == -1 or crossunder(k, 80) -> close long; direction == 1 or crossover(k, 20) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is -1 in an up-trend and 1 in a down-trend, so the longs are taken in SuperTrend
      DOWN-trends and closed when it turns up (the shorts mirrored): ported as written.
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an entry
      on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. Two-day bars are blocks of broker-day dates from
      1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a SuperTrend and a stochastic.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482805_supertrend_dir_stoch_20_80_cross_2d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "k_len": [14, 21],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_len": 10, "k_len": 14, "d_len": 3, "smooth_k": 3, "ob": 80.0, "os": 20.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


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


def _supertrend_dir(bars_df, factor, n):
    """ta.supertrend direction (pine_supertrend): -1 up-trend, 1 down-trend; nan comparisons are false."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    dr = np.ones(m)
    prev_u = prev_l = prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        pl = 0.0 if np.isnan(prev_l) else prev_l
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
        dr[i] = d
        prev_u, prev_l, prev_st = up, lw, (lw if d == -1 else up)
    return dr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    up_os = ((k > p["os"]) & (k.shift(1) <= p["os"])).to_numpy()
    dn_ob = ((k < p["ob"]) & (k.shift(1) >= p["ob"])).to_numpy()
    dr = _supertrend_dir(bars_df, float(p["factor"]), int(p["atr_len"]))
    buy, sell = (dr == 1) & up_os, (dr == -1) & dn_ob
    xl, xs = (dr == -1) | dn_ob, (dr == 1) | up_os
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and pos != -1:
            se[i], pos = True, -1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
