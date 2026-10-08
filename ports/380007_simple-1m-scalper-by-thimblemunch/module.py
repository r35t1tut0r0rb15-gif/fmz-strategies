"""Simple 1m scalper (thimblemunch, posted by Zer3192): above EMA 200, in an up state of an ATR
trailing line, with a rising Schaff trend cycle, the close crossing above the line goes long; the
mirror goes short (always in).
Port of FMZ strategy #380007 "Simple 1m Scalper by thimblemunch".

Source
    https://www.fmz.com/strategy/380007 (PineScript v4, author Zer3192, FMZ last modified
    2022-08-25 19:55:23). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 32-103), STC 12 / 26 / 50, trend length 21 x 3
    STC: macd = ema(26) - ema(50); two stochastic stages over 12 bars, each smoothed by a 0.5 EMA
    avgTR = wma(atr(1), 21); hiLimit = highest(high, 21)[1] - 3 avgTR[1]; loLimit = lowest(low, 21)[1] + 3 avgTR[1]
    ret = close above both ? hiLimit : close below both ? loLimit : ret[1];  pos = close vs ret
    long  = close > ema200 and pos == 1 and STC rising and crossover(close, ret)
    short = close < ema200 and pos == -1 and STC falling and crossover(ret, close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The STC stages keep their last value when the range is 0 (nz(prev)), as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No bar size in the source (the title says 1m, the code has no header): FREQ =
      "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_380007_stc_trail_scalper"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_len": [14, 21],
    "trend_mult": [2.0, 3.0],
    "stc_len": [10, 12],
}
DEFAULT_PARAMS = {"stc_len": 12, "stc_fast": 26, "stc_slow": 50, "trend_len": 21, "trend_mult": 3.0}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _stc(c, n, fast, slow):
    macd = (c.ewm(span=fast, adjust=False).mean() - c.ewm(span=slow, adjust=False).mean()).to_numpy()
    m = len(macd)
    k1, d1, k2, d2 = (np.full(m, np.nan) for _ in range(4))
    for i in range(m):
        lo = np.min(macd[max(0, i - n + 1):i + 1]) if i >= n - 1 else np.nan
        rg = np.max(macd[max(0, i - n + 1):i + 1]) - lo if i >= n - 1 else np.nan
        prev = k1[i - 1] if i else 0.0
        k1[i] = (macd[i] - lo) / rg * 100 if rg > 0 else prev
        d1[i] = k1[i] if (i == 0 or np.isnan(d1[i - 1])) else d1[i - 1] + 0.5 * (k1[i] - d1[i - 1])
        lo2 = np.min(d1[max(0, i - n + 1):i + 1]) if i >= n - 1 else np.nan
        rg2 = np.max(d1[max(0, i - n + 1):i + 1]) - lo2 if i >= n - 1 else np.nan
        prev2 = k2[i - 1] if i else 0.0
        k2[i] = (d1[i] - lo2) / rg2 * 100 if rg2 > 0 else prev2
        d2[i] = k2[i] if (i == 0 or np.isnan(d2[i - 1])) else d2[i - 1] + 0.5 * (k2[i] - d2[i - 1])
    return d2


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cs = bars_df["close"]
    stc = _stc(cs, int(p["stc_len"]), int(p["stc_fast"]), int(p["stc_slow"]))
    n = int(p["trend_len"])
    avg_tr = _wma(_atr_pine(bars_df, 1), n)
    hi_lim = (bars_df["high"].rolling(n).max().shift(1) - avg_tr.shift(1) * p["trend_mult"]).to_numpy()
    lo_lim = (bars_df["low"].rolling(n).min().shift(1) + avg_tr.shift(1) * p["trend_mult"]).to_numpy()
    c = cs.to_numpy(dtype=float)
    m = len(c)
    ret, pos = np.full(m, np.nan), np.zeros(m)
    for i in range(m):
        r1 = ret[i - 1] if i and not np.isnan(ret[i - 1]) else c[i]
        if c[i] > hi_lim[i] and c[i] > lo_lim[i]:
            ret[i] = hi_lim[i]
        elif c[i] < lo_lim[i] and c[i] < hi_lim[i]:
            ret[i] = lo_lim[i]
        else:
            ret[i] = r1
        p1 = pos[i - 1] if i else 0.0
        pos[i] = 1.0 if c[i] > ret[i] else (-1.0 if c[i] < ret[i] else p1)
    em = cs.ewm(span=200, adjust=False).mean().to_numpy()
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    up_x = (c > ret) & (lag(c) <= lag(ret))
    dn_x = (ret > c) & (lag(ret) <= lag(c))
    long_ = (c > em) & (pos == 1) & (stc > lag(stc)) & up_x
    short = (c < em) & (pos == -1) & (stc < lag(stc)) & dn_x
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
