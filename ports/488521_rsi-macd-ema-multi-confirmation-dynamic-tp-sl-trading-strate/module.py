"""Engulfing and pin-bar entries on the EMA 50 side with RSI and MACD filters and a 1.5 ATR bracket, 1-hour bars: a
large bullish engulfing bar or a bullish pin bar above EMA 50, with RSI 14 below 70 and MACD above its signal, goes
long; mirrored for shorts; each trade has a stop and a target 1.5 ATR from the signal close.
Port of FMZ strategy #488521 "多重确认动态止盈止损交易策略RSI与MACD结合EMA趋势和蜡烛形态识别-Multi-Confirmation-Dynamic-TP-SL-Trading-Strategy-RSI-and-MACD-Combined-with-EMA-Trend-and-Candlestick-Pattern-Recognition" (Enhanced Trading Strategy with RSI, MACD, TP/SL).

FMZ source id: 488521

Source
    https://www.fmz.com/strategy/488521 (PineScript v5, FMZ last modified 2025-03-28 15:37:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 190-240), EMA 50, RSI 14, MACD 12 / 26 / 9, ATR 14 x 1.5
    bullishEngulfing = prev red, green, close > open[1], open < close[1], body > 1.5 x prev body, body > SMA5(body),
    close > ema;  bullishPinBar = lower shadow > 0.66 range, upper < 0.33 range, lower > 2.5 x body, close > ema
    buy = (engulfing or pin) and rsi < 70 and macd > signal (sell mirrored with rsi > 30, macd < signal)
    entry + exit(limit = close +- 1.5 ATR, stop = close -+ 1.5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = atr_mult x ATR / close, tp_stop the same, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar (its strategy.exit): mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Buy and sell need opposite EMA sides, so they never fall on one bar. Entries reverse (REVERSAL INTENDED).
      Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, candle proportions, EMA, oscillators and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488521_engulf_pinbar_rsi_macd_atr_bracket"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"ema_len": 50, "rsi_len": 14, "atr_len": 14, "atr_mult": 1.5, "shadow_ratio": 2.5}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    body = (c - o).abs()
    avg_body = body.rolling(5).mean()
    pbody = body.shift(1)
    o1, c1 = o.shift(1), c.shift(1)
    big = (body > pbody * 1.5) & (body > avg_body)
    bull_eng = (c1 < o1) & (c > o) & (c > o1) & (o < c1) & big & (c > ema)
    bear_eng = (c1 > o1) & (c < o) & (c < o1) & (o > c1) & big & (c < ema)
    rng = h - lo
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - lo
    r = p["shadow_ratio"]
    bull_pin = (lower > rng * 0.66) & (upper < rng * 0.33) & (lower > body * r) & (c > ema)
    bear_pin = (upper > rng * 0.66) & (lower < rng * 0.33) & (upper > body * r) & (c < ema)
    long_e = ((bull_eng | bull_pin) & (rsi < 70) & (macd > sig)).astype(bool)
    short_e = ((bear_eng | bear_pin) & (rsi > 30) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": d, "tp_stop": d.copy()}


def portfolio_kwargs(**params):
    return {}
