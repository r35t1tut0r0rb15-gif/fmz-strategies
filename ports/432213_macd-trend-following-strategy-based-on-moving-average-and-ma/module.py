"""Zero-lag LSMA 32 / 400 turns at a MACD cross, 1-minute bars: with the ZLSMA 32 below a falling ZLSMA 400 and itself
rising, a MACD (12 / 26, SMA 9 signal) cross with the MACD at or above its signal goes long; with the ZLSMA 32 above a
rising ZLSMA 400 and itself falling, the same kind of cross goes short. The ZLSMA 32 crossing the close closes the trade.
Port of FMZ strategy #432213 "基于均线和MACD指标的量化交易策略Trend-Following-Strategy-Based-on-Moving-Average-and-MACD" (Stratégie ZLSMA Bruno).

FMZ source id: 432213

Source
    https://www.fmz.com/strategy/432213 (PineScript v5, FMZ last modified 2023-11-15 15:58:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 203-269), MACD 12 / 26 / SMA 9, ZLSMA 32 and 400 (offset 0)
    zlsma(n) = lsma + (lsma - linreg(lsma, n)), lsma = linreg(close, n)
    zl32 < zl400 and zl400 < zl400[1] and zl32 > zl32[1] and cross(macd, signal) and macd >= signal -> entry long
    zl32 > zl400 and zl400 > zl400[1] and zl32 < zl32[1] and cross(macd, signal) and macd >= signal -> entry short
    crossunder(zl32, close) -> close long;  crossover(zl32, close) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries require macd_color == lime, i.e. macd >= signal, as written: with ta.cross either
      direction this means an upward MACD cross for shorts too.
    * linreg(x, n, 0) is the least-squares line through the last n values (current bar included),
      read at the current bar. crossunder(zl32, close) = zl32 < close and zl32[1] >= close[1].
    * A close written after the entries acts on the position held at the bar's start: a same-side
      signal while in the trade is an ignored add, so a close on that bar leaves it flat; an opposite
      entry reverses and a later close of the other side does not undo it (C31-C39 convention):
      REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression-line turns and a MACD cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432213_zlsma_macd_cross"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [32, 16],
    "slow": [400, 200],
}
DEFAULT_PARAMS = {"macd_fast": 12, "macd_slow": 26, "macd_signal": 9, "fast": 32, "slow": 400}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def _zlsma(x, n):
    a = _linreg(x, n)
    return a + (a - _linreg(a, n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["macd_signal"])).mean()
    crs = ((macd > sig) & (macd.shift(1) <= sig.shift(1))) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)))
    lime = macd >= sig
    zf, zs = _zlsma(c, int(p["fast"])), _zlsma(c, int(p["slow"]))
    le = ((zf < zs) & (zs < zs.shift(1)) & (zf > zf.shift(1)) & crs & lime).to_numpy()
    se = ((zf > zs) & (zs > zs.shift(1)) & (zf < zf.shift(1)) & crs & lime).to_numpy()
    xl = ((zf < c) & (zf.shift(1) >= c.shift(1))).to_numpy()
    xs = ((zf > c) & (zf.shift(1) <= c.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le[i]:
            pos = 1
        if se[i]:
            pos = -1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    l_e = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)                      # a reversal is the opposite entry alone
    s_e = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (l_e, lx, s_e, sx))


def portfolio_kwargs(**params):
    return {}
