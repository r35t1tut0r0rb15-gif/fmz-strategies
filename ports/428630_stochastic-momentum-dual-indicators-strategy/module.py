"""Noro SMI + RSI, 2-day bars: a red real-bodied bar with the stochastic momentum index under -50 or the
fast RSI(7) under 20 goes long; a green real-bodied bar with SMI over 50 or RSI over 80 goes short. A
long closes on a green real-bodied bar, a short on a red one.
Port of FMZ strategy #428630 "Stochastic Momentum Dual Indicators Strategy" (Noro SMI + RSI).

FMZ source id: 428630

Source
    https://www.fmz.com/strategy/428630 (PineScript v2, FMZ last modified 2023-10-07 16:45:25).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 139-214), SMI 5 / 3, limit 50, fast RSI 7 (20 / 80), body filter
    SMI = ema(ema(close - mid5, 3), 3) / (ema(ema(range5, 3), 3) / 2) x 100
    body = |close - open| > sma(|close - open|, 10) / 3
    up = (SMI < -50 or rsi7 < 20) and red bar and body -> close a short, entry long
    dn = (SMI > 50 or rsi7 > 80) and green bar and body -> close a long, entry short
    exit = (long and green bar or short and red bar) and body -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A signal bar also meets the exit of the opposite position: the entry wins (house convention).
    * Martingale (off), capital % and the switches are sizing; the date window is dropped.
    * REVERSAL INTENDED. 2-day bars are blocks of broker days counted from 1970-01-01 (as worker
      A's 2-day ports), stamped with the session start. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and body ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot, martingale and capital inputs stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428630 (3 members, best partner #433007, Jaccard 0.913); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428630_noro_smi_rsi_2d"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [50, 40],
    "a": [5, 10],
}
DEFAULT_PARAMS = {"a": 5, "b": 3, "limit": 50, "rsi_len": 7, "body_len": 10}


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


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
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
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    d = c.diff()
    k = int(p["rsi_len"])
    fu, fd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + fu / fd)).where(fu != 0, 0.0).where(fd != 0, 100.0).where(fu.notna() & fd.notna())
    a, b = int(p["a"]), int(p["b"])
    ll, hh = lo.rolling(a).min(), h.rolling(a).max()
    e2 = lambda x: x.ewm(span=b, adjust=False, ignore_na=True).mean().ewm(span=b, adjust=False, ignore_na=True).mean()
    avgrel, avgdiff = e2(c - (hh + ll) / 2), e2(hh - ll)
    smi = (avgrel / (avgdiff / 2) * 100).where(avgdiff != 0, 0.0).where(avgdiff.notna())
    nb = (c - o).abs()
    body = (nb > nb.rolling(int(p["body_len"])).mean() / 3).to_numpy()
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    lim = p["limit"]
    up = (((smi < -lim) | (rsi < 20)).to_numpy()) & red & body
    dn = (((smi > lim) | (rsi > 80)).to_numpy()) & green & body
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        elif start == 1 and green[i] and body[i]:
            pos = 0
        elif start == -1 and red[i] and body[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
