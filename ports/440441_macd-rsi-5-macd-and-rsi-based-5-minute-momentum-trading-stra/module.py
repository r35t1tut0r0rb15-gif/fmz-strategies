"""RSI and MACD momentum, 2-hour bars: the RSI 14 crossing over 30 together with the MACD crossing over its signal goes long; the RSI crossing under 70 or the MACD crossing under its signal goes short;
as written a short is closed on the next bar (its close test is always true); reversing.
Port of FMZ strategy #440441 "基于MACD和RSI的5分钟动量交易策略MACD-and-RSI-Based-5-Minute-Momentum-Trading-Strategy" (XRP Momentum).

FMZ source id: 440441

Source
    https://www.fmz.com/strategy/440441 (PineScript v5, FMZ last modified 2024-01-30 15:59:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-180), RSI 14 (70 / 30); MACD 12 / 26 / 9; stop 1 %, target 2 % of the current close
    buy = crossover(rsi, 30) and crossover(macd, signal) -> entry Buy;  sell = crossunder(rsi, 70) or crossunder(macd, signal) -> entry Sell
    close Buy when close > close x 1.02 or close < close x 0.99;  close Sell when close < close x 1.02 or close > close x 0.99

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are taken from the same bar's close, so the long close test is never true and the
      short close test always is: a short closes on the bar after its fill (a close acts only on the
      held position; on the signal bar the reversing entry stands, as #438020). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header (bars on UTC
      multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and MACD crossings.
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

NAME = "fmz_440441_rsi_macd_momentum_one_bar_short"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "rsi_oversold": [30, 40],
}
DEFAULT_PARAMS = {"rsi_length": 14, "rsi_oversold": 30, "fast": 12, "slow": 26, "signal": 9,
                  "stop_pct": 1.0, "target_pct": 2.0}


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
    r = _rsi(c, int(p["rsi_length"]))
    os_ = float(p["rsi_oversold"])
    ob = 100 - os_
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    buy = ((r > os_) & (r.shift(1) <= os_) & (macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    sell = (((r < ob) & (r.shift(1) >= ob)) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)))).to_numpy()
    tp, sl = c * (1 + float(p["target_pct"]) / 100), c * (1 - float(p["stop_pct"]) / 100)
    lx_t = ((c > tp) | (c < sl)).to_numpy()
    sx_t = ((c < tp) | (c > sl)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        if lx_t[i] and pos == 1 and new == 1:
            new = 0
        if sx_t[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
