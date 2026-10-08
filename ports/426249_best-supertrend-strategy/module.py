"""BEST SuperTrend: with the last SMA 7 / 20 cross upward, a close at or above the previous broker
day's SuperTrend line (daily, ATR 3 x 3) goes long; with it downward, a close at or below goes
short. The opposite SMA cross closes each side.
Port of FMZ strategy #426249 "BEST Supertrend Strategy".

Source
    https://www.fmz.com/strategy/426249 (PineScript v4, FMZ last modified 2023-09-09 22:20:09).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 78-232), Longs+Shorts, SMA 7 / 20, ST factor 3 (header
args 2), ST period 3, timeframe daily
    st = SuperTrend line (hl2 +- factor atr(3), ratchets on close[1], trend on close vs [1] lines)
    st_D = security('D', st[1], lookahead = true)   (the last completed day's line)
    cross_buy = last SMA cross was up;  bull = close >= st_D and cross_buy -> entry long
    bear = close <= st_D and cross_sell -> entry short
    crossunder(sma7, sma20) closes the long; crossover closes the short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily SuperTrend is computed on broker days (17:00 New York) built from the port's
      2-hour bars (each bar assigned to the broker day of its open) and read as the last completed
      day ([1] with lookahead on).
    * A short entry and a long close on the same bar net to the short (entries reverse); an
      entry while already on that side is ignored. REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426249_sma_cross_daily_supertrend"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [2.0, 3.0],
    "fast": [5, 7],
    "slow": [20, 30],
}
DEFAULT_PARAMS = {"factor": 3.0, "pd": 3, "fast": 7, "slow": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _st_line(bars, factor, pd_):
    h, l, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr_pine(bars, pd_).to_numpy()
    up_l, dn_l = (h + l) / 2 - factor * atr, (h + l) / 2 + factor * atr
    m = len(c)
    tu, td, tsl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    t = 1.0
    for i in range(m):
        tu1 = tu[i - 1] if i else np.nan
        td1 = td[i - 1] if i else np.nan
        c1 = c[i - 1] if i else np.nan
        tu[i] = max(up_l[i], tu1) if c1 > tu1 else up_l[i]
        td[i] = min(dn_l[i], td1) if c1 < td1 else dn_l[i]
        t = 1.0 if c[i] > td1 else (-1.0 if c[i] < tu1 else t)
        tsl[i] = tu[i] if t == 1 else td[i]
    return tsl


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    day = broker_day(idx)
    daily = bars_df.groupby(day).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    st_d = pd.Series(_st_line(daily, float(p["factor"]), int(p["pd"])), index=daily.index)
    prev_day = st_d.shift(1)  # the last completed day's value, seen during the current day
    st = prev_day.reindex(day).to_numpy()
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    lx_c = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    sx_c = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    last = 0  # +1 after an up cross (short_exit), -1 after a down cross (long_exit)
    pos = 0
    for i in range(m):
        if sx_c[i]:
            last = 1
        if lx_c[i]:
            last = -1
        bull = cv[i] >= st[i] and last == 1
        bear = cv[i] <= st[i] and last == -1
        before = pos
        if bull and pos != 1:
            pos = 1
        if lx_c[i] and pos == 1 and before == 1:
            pos = 0
        if bear and pos != -1:
            pos = -1
        if sx_c[i] and pos == -1 and before == -1:
            pos = 0
        if pos != before:
            if pos == 1:
                le[i] = True
            elif pos == -1:
                se[i] = True
            elif before == 1:
                lx[i] = True
            else:
                sx[i] = True
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
