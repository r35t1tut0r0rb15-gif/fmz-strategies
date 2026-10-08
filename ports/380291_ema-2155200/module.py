"""EMA 21 / 55 / 200 (Zer3192): EMA 21 crossing above EMA 55 with both (and the close) above EMA 200
goes long; the mirror goes short. RSI 14 falling back under 70 closes a long; rising back over 30
closes a short.
Port of FMZ strategy #380291 "EMA 21,55,200".

Source
    https://www.fmz.com/strategy/380291 (PineScript v4, author Zer3192, FMZ last modified
    2022-08-27 21:56:34). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 30-63), EMA 21 / 55 / 200, RSI 14 (70 / 30)
    long  = crossover(ema21, ema55) and ema21, ema55, close > ema200 -> entry long
    short = crossunder(ema21, ema55) and ema21, ema55, close < ema200 -> entry short
    close long on crossunder(rsi, 70) (and rsi > 50); close short on crossover(rsi, 30) (and rsi < 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI closes are close-based exit signals; a close does not apply on the bar its own entry
      is placed, and an entry while already on that side is ignored (position mirrored in
      simulate()).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}). Fixed qty 100 -> sizing.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380291_ema_21_55_200_rsi_exit"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 21],
    "mid": [34, 55],
    "slow": [100, 200],
}
DEFAULT_PARAMS = {"fast": 21, "mid": 55, "slow": 200, "rsi_len": 14}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    f, m_, s = e(p["fast"]), e(p["mid"]), e(p["slow"])
    up = ((f > m_) & (f.shift(1) <= m_.shift(1)) & (f > s) & (m_ > s) & (c > s)).to_numpy()
    dn = ((f < m_) & (f.shift(1) >= m_.shift(1)) & (f < s) & (m_ < s) & (c < s)).to_numpy()
    r = _rsi(c, int(p["rsi_len"]))
    close_l = ((r < 70) & (r.shift(1) >= 70) & (r > 50)).to_numpy()
    close_s = ((r > 30) & (r.shift(1) <= 30) & (r < 50)).to_numpy()
    n = len(c)
    le, lx, se, sx = (np.zeros(n, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(n):
        before = pos
        if up[i] and before != 1:
            le[i], pos = True, 1
        elif dn[i] and before != -1:
            se[i], pos = True, -1
        elif close_l[i] and before == 1:
            lx[i], pos = True, 0
        elif close_s[i] and before == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
