"""MACD 12 / 26 / 9 crossings filtered by the SMA 50 / 200 order and the RSI 14, 1-hour bars: the cross up below RSI 70 with the SMA 50 over the SMA 200 goes long, the cross down above RSI 30 with the SMA 50 under goes short; the opposite cross or an RSI beyond 70 / 30 closes; reversing.
Port of FMZ strategy #453653 "MACD与RSI相结合的多重过滤日内交易策略-MACD-and-RSI-Multi-Filter-Intraday-Trading-Strategy" (Day Trading Strategy (MACD and RSI multi-filter)).

FMZ source id: 453653

Source
    https://www.fmz.com/strategy/453653 (PineScript v5, FMZ last modified 2024-06-07 15:20:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-168), MACD 12 / 26 / 9; RSI 14, levels 70 / 30; SMA 50 / 200 filter
    crossover(macd, signal) and rsi < 70 and sma50 > sma200 -> entry BUY;  crossunder or rsi > 70 -> close BUY
    crossunder(macd, signal) and rsi > 30 and sma50 < sma200 -> entry SELL;  crossover or rsi < 30 -> close SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in source order: an entry on the held side is ignored, an opposite entry reverses,
      and a close acts only on the trade held into the bar when no earlier call reversed it. A cross
      down closes a long and, with the short filter, opens the short (one reversal); a cross down
      without it leaves the position flat. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, filtered MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453653_macd_cross_sma50_200_rsi_filter_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "rsi_len": [14, 7],
    "trend_slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "rsi_len": 14, "trend_fast": 50, "trend_slow": 200,
                  "ob": 70.0, "os": 30.0}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    sf, ss = c.rolling(int(p["trend_fast"])).mean(), c.rolling(int(p["trend_slow"])).mean()
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    ob, os_ = float(p["ob"]), float(p["os"])
    el = (up & (r < ob) & (sf > ss)).to_numpy()
    xl = (dn | (r > ob)).to_numpy()
    es = (dn & (r > os_) & (sf < ss)).to_numpy()
    xs = (up | (r < os_)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if es[i] and cur != -1:
            cur = -1
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
