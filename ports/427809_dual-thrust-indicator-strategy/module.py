"""Daily pivot cross with SuperTrend exits, 2-hour bars: a green bar opening below the previous broker
day's pivot point and closing above it and above SMA 20 goes long; a red bar crossing down through the
pivot under SMA 20 goes short. A long closes when a bar opens below the SuperTrend (2 x ATR 10) line,
a short when it opens above.
Port of FMZ strategy #427809 "Dual Thrust Indicator Strategy" ("Pivots strategy", amysojexson).

FMZ source id: 427809

Source
    https://www.fmz.com/strategy/427809 (PineScript v3, FMZ last modified 2023-09-25 17:34:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 263-503), pivot type Daily, SMA 20, SuperTrend 2 / 10
    pp = (H + L + C) / 3 of the previous day: security("D", x[1], lookahead_on)
    close > open and open < pp and close > pp and close > sma(close, 20) -> entry long
    close < open and open > pp and close < pp and close < sma(close, 20) -> entry short
    close long when open < Tsl; close short when open > Tsl (Tsl = SuperTrend line)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(.., x[1], lookahead_on) is the previous completed day's value from the first bar of
      the day: no look-ahead. Days are broker days (17:00 America/New_York) built from the 2-hour
      bars by their start time (a 2-hour bar that straddles the 17:00 close in summer counts with
      the day it starts in; stated approximation). The intraday and weekly pivot options are not
      the default and are not ported; the R / S levels are drawn only.
    * The closes are exit signals at the next open; an entry wins over a same-bar close of a
      position not yet open, and an opposite entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-day pivots only.
    2 generic: PASS, pivots from prices, ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily pivot; the
    0800-1600 session input belongs to the intraday option only.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427809_daily_pivot_cross_supertrend_exit"
FAMILY = "pivot_levels"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [2.0, 3.0],
    "pd": [10, 20],
    "ma": [20, 50],
}
DEFAULT_PARAMS = {"factor": 2.0, "pd": 10, "ma": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _tsl(bars, factor, n):
    h, lo, c = bars["high"], bars["low"], bars["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    a = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tu, td, out = np.zeros(m), np.zeros(m), np.full(m, np.nan)
    t = 1
    for i in range(m):
        up_b, dn_b = hl2[i] - factor * a[i], hl2[i] + factor * a[i]
        tu1 = tu[i - 1] if i else 0.0
        td1 = td[i - 1] if i else 0.0
        c1 = cv[i - 1] if i else np.nan
        tu[i] = max(up_b, tu1) if c1 > tu1 else up_b
        td[i] = min(dn_b, td1) if c1 < td1 else dn_b
        if cv[i] > td1:
            t = 1
        elif cv[i] < tu1:
            t = -1
        out[i] = tu[i] if t == 1 else td[i]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    day = broker_day(bars_df.index)
    daily = bars_df.groupby(day).agg({"high": "max", "low": "min", "close": "last"})
    prev = daily.shift(1)
    pp_d = (prev["high"] + prev["low"] + prev["close"]) / 3
    pp = pp_d.reindex(day).to_numpy()
    ma = c.rolling(int(p["ma"])).mean().to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tsl = _tsl(bars_df, float(p["factor"]), int(p["pd"]))
    with np.errstate(invalid="ignore"):
        long_s = (cv > ov) & (ov < pp) & (cv > pp) & (cv > ma)
        short_s = (cv < ov) & (ov > pp) & (cv < pp) & (cv < ma)
        close_l = ov < tsl
        close_s = ov > tsl
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and close_l[i]:
            pos = 0
        if start == -1 and close_s[i]:
            pos = 0
        if long_s[i] and start != 1:
            pos = 1
        elif short_s[i] and start != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
