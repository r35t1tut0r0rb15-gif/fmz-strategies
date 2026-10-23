"""Hourly bars: a MACD bullish crossing with the close above the EMA 7 above the EMA 90, while the last completed 8-hour close is above its chart-bar EMA 7 on above-average 8-hour volume, goes long with a 1.5 ATR 14 stop and a 3 ATR target; the mirror crossing under (with the same bullish 8-hour filter) goes short with the long-side levels, so it exits at once; reversing.
Port of FMZ strategy #483088 "多重时间框架趋势跟踪策略结合动态仓位管理和ATR止盈止损系统-Multi-Timeframe-Trend-Following-Strategy-with-Dynamic-Position-Sizing-and-ATR-Based-Take-Profit-Stop-Loss-System" (Optimized Trend Strategy).

FMZ source id: 483088

Source
    https://www.fmz.com/strategy/483088 (PineScript v6, FMZ last modified 2025-02-27 17:02:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 95-141), EMA 7 / 90; MACD 12 / 26 / 9; 8-hour close / volume via request.security("480"); ATR 14; SL 1.5, TP 3 ATR
    h8Close = request.security("480", close);  h8Volume = request.security("480", volume);  h8Signal = h8Close > ema(h8Close, 7) and h8Volume > sma(h8Volume, 50)  (EMA / SMA taken on the chart's bars)
    longCondition = close > ema7 > ema90 and crossover(macd, signal) and h8Signal -> entry Long, exit(stop = close - 1.5 atr, limit = close + 3 atr)
    shortCondition = close < ema7 < ema90 and crossunder(macd, signal) and h8Signal -> entry Short, exit(stop = close - 1.5 atr, limit = close + 3 atr)  (the long levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 8-hour security (no look-ahead) is read as the last 8-hour block (UTC 00 / 08 / 16) completed
      before the bar's own block (as #482904's reading of completed higher bars); its EMA 7 and SMA 50
      are then taken over the hourly series of those stepped values, as written. The short gets the
      long-side levels (a buy stop under and a buy limit over the price), so it is closed at once (weird
      case): ported as the 1e-6 floor for both. The quantity (equity x 0.3 / 0.5 / 0.7 / close by trend
      strength) and the 50 in cash are sizing. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, MACD crossings in an EMA 7 / 90 trend with an 8-hour filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: trend-strength quantity and cash size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per 8-hour block) against its SMA 50 on the hourly series; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h); 8-hour blocks from UTC midnight.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483088_macd_cross_ema7_90_h8_filter_atr_bracket_1h_reversal"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 2.0],
    "tp_atr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "tp_atr": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _h8_prev(bars_df):
    """Close and volume of the last 8-hour block completed before each bar's own block."""
    c, v = bars_df["close"], bars_df["volume"]
    blk = bars_df.index.floor("8h")
    bc = pd.Series(c.to_numpy(), index=blk).groupby(level=0).last()
    bv = pd.Series(v.to_numpy(), index=blk).groupby(level=0).sum()
    return (pd.Series(bc.shift(1).reindex(blk).to_numpy(), index=c.index),
            pd.Series(bv.shift(1).reindex(blk).to_numpy(), index=c.index))


def simulate(bars_df, **params):
    c = bars_df["close"]
    e7, e90 = c.ewm(span=7, adjust=False).mean(), c.ewm(span=90, adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hc, hv = _h8_prev(bars_df)
    h8 = (hc > hc.ewm(span=7, adjust=False).mean()) & (hv > hv.rolling(50).mean())
    buy = (c > e7) & (e7 > e90) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & h8
    sell = (c < e7) & (e7 < e90) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & h8
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    stop_lv = c - float(p["sl_atr"]) * atr          # the same levels for both sides, as written
    tp_lv = c + float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - stop_lv.shift(1) / o)
            .mask(sf, stop_lv.shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, tp_lv.shift(1) / o - 1)
            .mask(sf, 1 - tp_lv.shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
