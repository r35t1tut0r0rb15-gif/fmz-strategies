"""EMA 5 / 13 crossings on the EMA 50 side, 3-hour bars: the EMA 5 crossing over the EMA 13 with the close above the EMA 50 goes long, the mirror short; a long closes on the RSI 14 above 70 or the EMA 5
crossing back under, a short on the RSI under 30 or the crossing back over.
Port of FMZ strategy #441043 "均线与RSI指标结合的趋势跟踪策略Exponential-Moving-Average-and-Relative-Strength-Index-Combination-Trend-Following-Strategy" (EMA, RSI, and Price Crossover Strategy).

FMZ source id: 441043

Source
    https://www.fmz.com/strategy/441043 (PineScript v5, FMZ last modified 2024-02-05 09:57:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-151), EMA 5 / 13 / 50; RSI 14 (70 / 30 exits); default_qty_value 1
    long = crossover(ema5, ema13) and close > ema50 -> entry Long;  short = crossunder(ema5, ema13) and close < ema50 -> entry Short
    rsi > 70 or crossunder(ema5, ema13) -> close Long;  rsi < 30 or crossover(ema5, ema13) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position; the close written after a reversing entry leaves the
      reversal standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. The quantity of 1 is
      sizing. FREQ = "3h" from the backtest header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the default quantity stored.
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

NAME = "fmz_441043_ema5_13_cross_ema50_side_rsi_exit"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_len": [50, 100],
    "rsi_length": [14, 9],
}
DEFAULT_PARAMS = {"trend_len": 50, "rsi_length": 14, "fast": 5, "slow": 13}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    t = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    xo = (f > s) & (f.shift(1) <= s.shift(1))
    xu = (f < s) & (f.shift(1) >= s.shift(1))
    el, es = (xo & (c > t)).to_numpy(), (xu & (c < t)).to_numpy()
    xl, xs = ((r > 70) | xu).to_numpy(), ((r < 30) | xo).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
