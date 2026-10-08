"""Bollinger lows (Zer3192): a swing line built from a smoothed price-shadow series (EMA 20 +- ATR
20, swing machine with 0.1 % reversal) crossing above the 100-bar lowest Bollinger-buy close goes
long; crossing below the 100-bar highest Bollinger-sell close goes short (always in).
Port of FMZ strategy #366388 "Bollinger lows".

Source
    https://www.fmz.com/strategy/366388 (PineScript v4, author Zer3192, FMZ last modified
    2022-05-29 07:22:43). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 43-194), EMA 30 +- 2 sd, len 20, period 20, factor 0.001
    long_bb = crossover(close, ema30 - 2 sd);  last_open_long = close at it (0 before)
    short_bb = crossunder(close, ema30 + 2 sd);  last_open_short likewise
    lowb = lowest(last_open_long, 100);  highb = highest(last_open_short, 100)
    vp = spread + cum(spread), spread = (close - open) * 100 * close
    shadow = (vp - sma(vp, 14)) / stdev(vp - sma(vp, 14), 28) * stdev(high - low, 28)
    out = shadow > 0 ? high + shadow : low + shadow;  yp = ema(out, 20)
    x = yp - atr(20), n = yp + atr(20) -> swing machine (hb / lb / trend), v = hb or lb
    crossover(v, lowb) -> entry long; else crossunder(v, highb) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cum() is a running sum of past bars only; vp - sma(vp, 14) depends only on the last 14
      increments, so the shadow does not depend on where the data starts.
    * The swing machine follows Pine's nz() semantics (state reset to 0 after an na).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366388_bollinger_lows_swing"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len5": [20, 30],
    "len": [10, 20],
    "period": [14, 20],
}
DEFAULT_PARAMS = {"len5": 30, "multi": 2.0, "len": 20, "period": 20, "lookback": 100, "factor": 0.001}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _hb_lb_trend(n, x, factor):
    """Zer3192's swing machine (Pine nz() semantics): hb ratchets up with x while trend > 0 and
    flips to -1 when n falls `factor` below hb[1]; lb ratchets down with n while trend < 0 and
    flips to 1 when x rises `factor` above lb[1]. Returns (trend, v = hb if 1, lb if -1)."""
    n, x = np.asarray(n, dtype=float), np.asarray(x, dtype=float)
    m = len(n)
    hb, lb = np.full(m, np.nan), np.full(m, np.nan)
    tr = np.zeros(m)
    nz = lambda a: 0.0 if np.isnan(a) else a
    for i in range(m):
        hb1 = hb[i - 1] if i else np.nan
        lb1 = lb[i - 1] if i else np.nan
        h_, l_, t = nz(hb1), nz(lb1), (tr[i - 1] if i else 0.0)
        if i == 0:
            l_, h_ = n[i], x[i]
        elif i == 1:
            if x[i] >= hb1:
                h_, t = x[i], 1.0
            else:
                l_, t = n[i], -1.0
        elif tr[i - 1] > 0:
            if x[i] >= hb1:
                h_ = x[i]
            elif n[i] < hb1 - hb1 * factor:
                l_, t = n[i], -1.0
        else:
            if n[i] <= lb1:
                l_ = n[i]
            elif x[i] > lb1 + lb1 * factor:
                h_, t = x[i], 1.0
        hb[i], lb[i], tr[i] = h_, l_, t
    v = np.where(tr == 1, hb, np.where(tr == -1, lb, np.nan))
    return tr, v


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    k5 = int(p["len5"])
    mean, sd = c.ewm(span=k5, adjust=False).mean(), p["multi"] * c.rolling(k5).std(ddof=0)
    lo_b, up_b = mean - sd, mean + sd
    long_bb = ((c > lo_b) & (c.shift(1) <= lo_b.shift(1))).to_numpy()
    short_bb = ((c < up_b) & (c.shift(1) >= up_b.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lol, los = np.zeros(m), np.zeros(m)
    for i in range(m):
        lol[i] = cv[i] if long_bb[i] else (lol[i - 1] if i else 0.0)
        los[i] = cv[i] if short_bb[i] else (los[i - 1] if i else 0.0)
    r = int(p["lookback"])
    lowb = pd.Series(lol).rolling(r).min().to_numpy()
    highb = pd.Series(los).rolling(r).max().to_numpy()
    spread = (c - o) * 100 * c
    vp = spread + spread.cumsum()
    dev = vp - vp.rolling(14).mean()
    shadow = dev / dev.rolling(28).std(ddof=0) * (h - l).rolling(28).std(ddof=0)
    out = np.where(shadow > 0, h + shadow, l + shadow)
    yp = pd.Series(out, index=c.index).ewm(span=int(p["len"]), adjust=False).mean()
    atr = _atr_pine(bars_df, int(p["period"]))
    _, v = _hb_lb_trend((yp + atr).to_numpy(), (yp - atr).to_numpy(), p["factor"])
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (v > lowb) & (lag(v) <= lag(lowb))
    sell = (v < highb) & (lag(v) >= lag(highb))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
