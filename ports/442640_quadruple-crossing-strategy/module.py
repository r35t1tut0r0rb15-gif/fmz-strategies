"""Hourly bars, long only: a close up to 5 % above the EMA 200 on a rising close, two bars of rising volume, a rising RSI 14 above 35 and a positive MACD histogram, or a close 14 % under the EMA 20, or a close under the 2.5 sd Bollinger band, goes long; the mirror set (close up to 3 % under the EMA 200 ..., 19 % over the EMA 20, over the upper band) closes it.
Port of FMZ strategy #442640 "Quadruple Crossing Strategy" (Quadruple Cross Strategy (anonXmoous)).

FMZ source id: 442640

Source
    https://www.fmz.com/strategy/442640 (PineScript v5, FMZ last modified 2024-02-23 14:20:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 144-188), EMA 200 / 20; RSI 14; MACD 12 / 26 / 9; Bollinger 20 x 2.5
    buySignal = (bc1 and bc2 and bc3 and bc4 and bc5) or close < ema20 x 0.86 or close < lowerBB -> entry long
    sellSignal = (sc1 and sc2 and sc3 and sc4 and sc5) or close > ema20 x 1.19 or close > upperBB -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * bc1 = close above the EMA 200 by at most 5 % (or exactly on it); bc3 = volume rising two bars in
      a row. The entry is called before the close: from flat a bar with both signals enters; while long it
      closes. Pine's stdev is the population deviation. Long only. 10 % of equity and the commission are
      sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend-pullback momentum confluence or deep-dip entries with mirrored exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10 % of equity, capital 100000, commission 0.1 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the two-bar rising-volume tests; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442640_quadruple_cross_confluence_dip_entries_1h_long_only"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_k": [2.5, 2.0],
    "ema_long": [200, 100],
}
DEFAULT_PARAMS = {"bb_k": 2.5, "ema_long": 200}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    e200 = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    e20 = c.ewm(span=20, adjust=False).mean()
    rsi = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hist = macd - sig
    sma = c.rolling(20).mean()
    sd = c.rolling(20).std(ddof=0)
    k = float(p["bb_k"])
    up_bb, lo_bb = sma + k * sd, sma - k * sd
    vol_up = (v > v.shift(1)) & (v.shift(1) > v.shift(2))
    b1 = ((c > e200) & ((c - e200) / e200 <= 0.05)) | (c == e200)
    s1 = ((c < e200) & ((c - e200) / e200 >= -0.03)) | (c == e200)
    buy = ((b1 & (c > c.shift(1)) & vol_up & (rsi > 35) & (rsi > rsi.shift(1)) & (macd > sig) & (hist > 0))
           | ((c < e20) & ((c - e20) / e20 <= -0.14)) | (c < lo_bb)).to_numpy()
    sell = ((s1 & (c < c.shift(1)) & vol_up & (rsi < 65) & (rsi < rsi.shift(1)) & (macd < sig) & (hist < 0))
            | ((c > e20) & ((c - e20) / e20 >= 0.19)) | (c > up_bb)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
