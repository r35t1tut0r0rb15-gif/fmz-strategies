"""An up bar above the VWMA 33 with the RSI 14 of the VWMA at or above 30 while the ATR 33 x 3.5 trailing line state is up, hourly bars, long only: such a bar goes long; the close crossing under the trailing line closes.
Port of FMZ strategy #431414 "基于VWMA及ATR的趋势跟踪策略VWMA-and-ATR-Trend-Following-Strategy" (VWMA_withATRstops_strategy V2).

FMZ source id: 431414

Source
    https://www.fmz.com/strategy/431414 (PineScript v4, FMZ last modified 2023-11-07 16:39:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-214), VWMA 33; ATR 33 x 3.5 trailing line; RSI 14 of the VWMA; risk 10 %, stop 5 % (sizing only)
    xATRTrailingStop ratchets around the close by 3.5 atr(33) (from nz = 0);  pos = 1 when the close crosses up through it, -1 when down
    rsi(vwma, 14) >= 30 and close > open and close > vwma and pos == 1 -> entry VWMA LE;  position_size >= 1 and crossunder(close, trailing line) -> close VWMA LE

Interpretation choices (Pine rules in SURVEY_README.md)
    * position_size >= 1 is read as "in a position" (as #426617). The trailing line and its state run as
      written from nz = 0. The 5 % "stop" only sizes the risk-based quantity, it sends no order. Long only.
      The risk-based quantity and 20 % of equity are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWMA trend entries with an ATR trailing-line exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 10 % / (close x 5 %), 20 % of equity, capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(close, 33) and its RSI; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431414_vwma33_atr_trailing_state_rsi_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vwma_length": [33, 20],
    "atr_mult": [3.5, 2.0],
}
DEFAULT_PARAMS = {"vwma_length": 33, "atr_mult": 3.5, "atr_period": 33, "rsi_len": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["vwma_length"])
    vw = (c * v).rolling(n).sum() / v.rolling(n).sum()
    d = vw.diff()
    k = int(p["rsi_len"])
    rsi = 100 - 100 / (1 + _rma(d.clip(lower=0), k) / _rma((-d).clip(lower=0), k))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    nl = (float(p["atr_mult"]) * _rma(tr, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.zeros(m)
    st = np.zeros(m)
    prev, ps = 0.0, 0.0
    for i in range(m):
        c1 = cv[i - 1] if i else np.nan
        if cv[i] > prev and c1 > prev:
            t = max(prev, cv[i] - nl[i])
        elif cv[i] < prev and c1 < prev:
            t = min(prev, cv[i] + nl[i])
        else:
            t = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
        if c1 < prev and cv[i] > prev:
            ps = 1.0
        elif c1 > prev and cv[i] < prev:
            ps = -1.0
        ts[i], st[i] = t, ps
        prev = 0.0 if np.isnan(t) else t
    tss = pd.Series(ts, index=c.index)
    ent = ((rsi >= 30) & (c > o) & (c > vw) & pd.Series(st == 1, index=c.index)).to_numpy()
    xd = ((c < tss) & (pc >= tss.shift(1))).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xd[i]:
            lx[i], pos = True, 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
