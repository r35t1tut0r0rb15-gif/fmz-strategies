"""SuperTrend (10, 3) flips, always in, three-day bars: a flip up goes long, a flip down goes short (the source's
take-profit / stop-loss logic only draws labels and places no orders).
Port of FMZ strategy #489186 "高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System" (SuperTrend STRATEGY w/ TP & SL).

FMZ source id: 489186

Source
    https://www.fmz.com/strategy/489186 (PineScript v5, FMZ last modified 2025-04-02 15:30:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 178-266), ATR 10 x 3 on hl2
    lower line ("upperBand") = src - 3 ATR, ratcheted up while close[1] is above it; upper line mirrored
    trend = close > previous upper line ? 1 : close < previous lower line ? -1 : trend[1]
    flip to 1 -> entry long;  flip to -1 -> entry short   (TP / SL / entry-offset levels only label the chart)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trend test as written (both comparisons every bar, not only from the opposite state). The TP / SL / offset
      block sets flags and labels only: no order, not ported.
    * Always in after the first flip (REVERSAL INTENDED).
    * FREQ = "3D" from the backtest header (period 3d): three-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
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

NAME = "fmz_489186_supertrend_flip_always_in_3d"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [10, 20],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 10, "mult": 3.0}


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


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, int(p["atr_period"])).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    trend = np.ones(m, dtype=np.int8)
    lo_prev = up_prev = np.nan
    t = 1
    for i in range(m):
        lower, upper = src[i] - p["mult"] * atr[i], src[i] + p["mult"] * atr[i]
        pl = lower if np.isnan(lo_prev) else lo_prev          # nz(upperBand[1], upperBand) in the source's names
        pu = upper if np.isnan(up_prev) else up_prev
        if i > 0 and c[i - 1] > pl:
            lower = max(lower, pl)
        if i > 0 and c[i - 1] < pu:
            upper = min(upper, pu)
        if c[i] > pu:
            t = 1
        elif c[i] < pl:
            t = -1
        trend[i] = t
        lo_prev, up_prev = lower, upper
    prev = np.concatenate(([trend[0]], trend[:-1]))
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return (pd.Series((trend == 1) & (prev == -1), index=idx), false,
            pd.Series((trend == -1) & (prev == 1), index=idx), false.copy())


def portfolio_kwargs(**params):
    return {}
