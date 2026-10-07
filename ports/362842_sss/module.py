"""SSS: long from flat when the SSL channel (SMA 200 of highs / lows) flips up, smoothed candle
opens rise, and both EMA(close, 100) and the smoothed high sit below the bar's midpoint; exit at a
1 % take-profit or on a close below EMA 100. Long only.
Port of FMZ strategy #362842 "SSS".

Source
    https://www.fmz.com/strategy/362842 (PineScript v5, FMZ last modified 2022-05-13 12:30:11).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 70-153), MA 100, take profit 1 %, stop off
    Hlv1 = close > sma(high, 200) ? 1 : close < sma(low, 200) ? -1 : Hlv1[1]
    CandleOpen = ema((open[1] + close[1]) / 2, 25);  CandleHigh = ema(max(high, close), 20)
    long = Hlv1 == 1 and Hlv1[1] == -1 and CandleOpen > CandleOpen[1] and ema(close, 100) < hl2
           and CandleHigh < hl2 and no open trade
    strategy.exit(limit = entry * (1 + 1 %));  if close < MA: strategy.exit(stop = close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit is fixed at the entry price: stops() returns tp_stop = take_profit / 100
      (vbt re-bases it on the fill price), shifted one bar inside stops().
    * "close < MA -> exit with stop = close" is a close-based stop (rule 3, 2026-10-07): ported as
      an exit signal on that close, not as sl_stop. "Use Stop Percentage" defaults to false.
    * Entries need a flat position; simulate() mirrors the engine's take-profit to know when the
      position is gone. Long only: opposite entries cannot occur (portfolio_kwargs
      upon_opposite_entry="ignore", rule 6).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362842_sss_ssl_flip_long_tp"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [50, 100, 200],
    "take_profit": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"ma_len": 100, "take_profit": 1.0, "ssl_len": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["ssl_len"])
    ma_h, ma_l = h.rolling(n).mean(), l.rolling(n).mean()
    hlv = np.zeros(len(c))
    up, dn = (c > ma_h).to_numpy(), (c < ma_l).to_numpy()
    for i in range(len(c)):
        hlv[i] = 1.0 if up[i] else (-1.0 if dn[i] else (hlv[i - 1] if i else np.nan))
    hlv1 = np.concatenate([[np.nan], hlv[:-1]])
    c_open = ((o.shift(1) + c.shift(1)) / 2).ewm(span=25, adjust=False).mean()
    c_high = np.maximum(h, c).ewm(span=20, adjust=False).mean()
    ma = c.ewm(span=int(p["ma_len"]), adjust=False).mean()
    mid = (h - l) / 2 + l
    long_c = (hlv == 1) & (hlv1 == -1) & ((c_open > c_open.shift(1)) & (ma < mid) & (c_high < mid)).to_numpy()
    below = (c < ma).to_numpy()

    ov, hv = o.to_numpy(dtype=float), h.to_numpy(dtype=float)
    tp = p["take_profit"] / 100
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out, target = 0, False, False, np.nan
    for i in range(m):
        if pend_in:
            pos, target, pend_in = 1, ov[i] * (1 + tp), False
        if pend_out:
            pos, pend_out = 0, False
        if pos == 1 and hv[i] >= target:
            pos = 0
        if pos == 1 and below[i]:
            lx[i], pend_out = True, True
        elif pos == 0 and not pend_in and long_c[i]:
            le[i], pend_in = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = pd.Series(p["take_profit"] / 100, index=bars_df.index)
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
