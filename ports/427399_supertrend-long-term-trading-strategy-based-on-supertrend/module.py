"""SuperTrend long-term on 3-day bars: the SuperTrend (3 x ATR 10 of hl2) turning up with the close
above SMA 20 goes long; turning down with the close below it closes the long and goes short.
Port of FMZ strategy #427399 "Long-Term Trading Strategy Based on SuperTrend".

FMZ source id: 427399

Source
    https://www.fmz.com/strategy/427399 (PineScript v4, FMZ last modified 2023-09-20 17:14:33).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 210-275), ATR 10 (Wilder), multiplier 3, SMA 20
    up = hl2 - 3 atr; up := close[1] > up[1] ? max(up, up[1]) : up (dn mirrors)
    trend := trend == -1 and close > dn[1] ? 1 : trend == 1 and close < up[1] ? -1 : trend
    trend turns 1 and close > sma(close, 20) -> entry long
    trend turns -1 and close < sma(close, 20) -> close long and entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * 3-day bars are built from broker days (session ends 17:00 America/New_York) in fixed blocks of
      three broker-day dates counted from 1970-01-01, stamped with the first session start: the
      same construction as worker A's 2-day ports (block phase: decision owed there too).
    * "Change ATR calculation" is on (Wilder ATR). The date window (from 2018) is dropped.
    * The short entry reverses the long: REVERSAL INTENDED.
    * FREQ = "3D" from the backtest header (period 3d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples and an MA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash qty 50000 stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427399 (3 members, best partner #428578, Jaccard 0.709); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427399_supertrend_3d_long_term"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 20],
    "multiplier": [3.0, 2.0],
    "ma_period": [20, 50],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0, "ma_period": 20}


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


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker-day dates counted from 1970-01-01 (as worker A's #426995), each stamped
    with the session start of its first broker day."""
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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    ma = c.rolling(int(p["ma_period"])).mean().to_numpy()
    k = float(p["multiplier"])
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        u, d = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        u1 = up[i - 1] if i and not np.isnan(up[i - 1]) else u      # nz(up[1], up)
        d1 = dn[i - 1] if i and not np.isnan(dn[i - 1]) else d
        c1 = cv[i - 1] if i else np.nan
        up[i] = max(u, u1) if c1 > u1 else u
        dn[i] = min(d, d1) if c1 < d1 else d
        t = trend[i - 1] if i else 1
        if t == -1 and cv[i] > d1:
            t = 1
        elif t == 1 and cv[i] < u1:
            t = -1
        trend[i] = t
    t1 = np.concatenate(([1], trend[:-1]))
    buy = (trend == 1) & (t1 == -1) & (cv > ma)
    sell = (trend == -1) & (t1 == 1) & (cv < ma)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif sell[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
