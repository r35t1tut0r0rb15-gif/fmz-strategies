"""Hourly bars: a bullish engulfing candle closing above the Keltner channel (EMA 20 + 1.5 ATR 14) on above-average volume goes long, a bearish engulfing candle closing below the lower channel goes short; a stop 1.5 ATR and a target 2 ATR from each bar's close, re-sent every bar, are followed in the signals; reversing.
Port of FMZ strategy #482881 "多重技术指标趋势跟踪通道突破交易策略与K线形态过滤系统-Multi-Technical-Indicator-Trend-Following-Channel-Breakout-Trading-Strategy-with-Candlestick-Pattern-Filtering-System" (Keltner Channel Breakout with Candlestick Patterns).

FMZ source id: 482881

Source
    https://www.fmz.com/strategy/482881 (PineScript v5, FMZ last modified 2025-02-27 17:30:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 105-169), EMA 20; ATR 14 x 1.5 channel; volume SMA 20; engulfing; SL 1.5 ATR, TP 2 ATR from the latest close
    long_condition = close > ema20 + 1.5 atr and volume > sma(volume, 20) and bullish_engulfing -> entry Long;  short mirrored
    every bar: exit("Exit Long", "Long", stop = close - 1.5 atr, limit = close + 2 atr);  exit("Exit Short", "Short", stop = close + 1.5 atr, limit = close - 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent every bar from that bar's close and ATR (including the signal bar, for the
      pending entry), so the levels move both ways; the house engine cannot move a bracket that way, so
      the signals follow it: a bar that reaches the previous bar's stop or target closes the trade at the
      next open (mark trailing_stop_pending). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent bracket followed in the signals.
    2 generic: PASS, Keltner breakouts confirmed by engulfing candles on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482881_keltner_breakout_engulfing_volume_rolling_atr_bracket_1h_reversal"
FAMILY = "keltner_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.0],
    "tp_atr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"mult": 1.5, "sl_atr": 1.5, "tp_atr": 2.0}


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
    ema = c.ewm(span=20, adjust=False).mean()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    k = float(p["mult"])
    vol_ok = v > v.rolling(20).mean()
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c > o) & (o1 > c1) & (c > o1) & (o < c1)
    bear = (c < o) & (o1 < c1) & (c < o1) & (o > c1)
    buy = ((c > ema + k * atr) & vol_ok & bull).to_numpy()
    sell = ((c < ema - k * atr) & vol_ok & bear).to_numpy()
    sl, tp = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    l_st, l_tg = (c - sl).to_numpy(dtype=float), (c + tp).to_numpy(dtype=float)
    s_st, s_tg = (c + sl).to_numpy(dtype=float), (c - tp).to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and (ln[i] <= l_st[i - 1] or hn[i] >= l_tg[i - 1]):
            held = 0                       # the exit sent at the previous close is touched
        elif i > 0 and held == -1 and (hn[i] >= s_st[i - 1] or ln[i] <= s_tg[i - 1]):
            held = 0
        new = held
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
