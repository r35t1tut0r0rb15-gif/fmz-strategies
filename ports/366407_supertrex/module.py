"""SuperTREX (Zer3192): the close at the last RSI(14) cross above 35 (a step line) is wrapped in a
4 x ATR(10) SuperTrend-style band; the step line crossing above the active band line goes long,
below goes short (always in).
Port of FMZ strategy #366407 "SuperTREX".

Source
    https://www.fmz.com/strategy/366407 (PineScript v4, author Zer3192, FMZ last modified
    2022-05-29 09:49:08). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 43-101), RSI 14 (35 / 70), ST 4 x ATR 10
    xy = close at the last crossover(rsi, 35) (0 before);  ev1 = close at the last crossunder(rsi, 70)
    up_trend := xy[1] > up_trend[1] ? max(xy - 4 atr, up_trend[1]) : xy - 4 atr
    down_trend := ev1[1] < down_trend[1] ? min(xy + 4 atr, down_trend[1]) : xy + 4 atr
    trend := close > down_trend[1] ? 1 : close < up_trend[1] ? -1 : trend[1] (1 at start)
    st = trend == 1 ? up_trend : down_trend
    crossover(xy, st) -> entry long; else crossunder(xy, st) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The down band ratchets on the RSI-sell close (ev1) but is centred on xy, as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366407_supertrex_rsi_step"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "st_mult": [2.0, 4.0],
    "st_period": [10, 20],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 35, "over_bought": 70, "st_mult": 4.0, "st_period": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cs = bars_df["close"]
    rsi = _rsi(cs, int(p["length"]))
    lng = ((rsi > p["over_sold"]) & (rsi.shift(1) <= p["over_sold"])).to_numpy()
    sht = ((rsi < p["over_bought"]) & (rsi.shift(1) >= p["over_bought"])).to_numpy()
    c = cs.to_numpy(dtype=float)
    atr = (p["st_mult"] * _atr_pine(bars_df, int(p["st_period"]))).to_numpy()
    m = len(c)
    xy, ev1 = np.zeros(m), np.zeros(m)
    up, dn, st = np.zeros(m), np.zeros(m), np.full(m, np.nan)
    t = 1.0
    for i in range(m):
        xy[i] = c[i] if lng[i] else (xy[i - 1] if i else 0.0)
        ev1[i] = c[i] if sht[i] else (ev1[i - 1] if i else 0.0)
        up_lev, dn_lev = xy[i] - atr[i], xy[i] + atr[i]
        u1 = up[i - 1] if i else np.nan
        d1 = dn[i - 1] if i else np.nan
        up[i] = max(up_lev, u1) if (i and xy[i - 1] > u1) else up_lev
        dn[i] = min(dn_lev, d1) if (i and ev1[i - 1] < d1) else dn_lev
        t = 1.0 if c[i] > d1 else (-1.0 if c[i] < u1 else t)
        st[i] = up[i] if t == 1 else dn[i]
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (xy > st) & (lag(xy) <= lag(st))
    sell = (xy < st) & (lag(xy) >= lag(st))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
