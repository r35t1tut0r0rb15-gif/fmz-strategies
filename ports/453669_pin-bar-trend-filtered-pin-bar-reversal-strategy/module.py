"""Hourly bars: a bullish pin bar (lower wick over 60 % of the range, body under 30 %, up close above the SMA 50, volume above its 20-bar average) goes long; the bearish mirror goes short; a stop two bodies beyond the bar's extreme and a target three bodies beyond the other extreme; reversing.
Port of FMZ strategy #453669 "趋势过滤Pin-Bar反转策略-Trend-Filtered-Pin-Bar-Reversal-Strategy" (Filtered Pin Bar Strategy with Relaxed Volume).

FMZ source id: 453669

Source
    https://www.fmz.com/strategy/453669 (PineScript v5, FMZ last modified 2024-06-07 16:48:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-155), wick 0.6, body 0.3; SMA 50; volume SMA 20 x 1.0; RSI 14 (unused); SL 2 x body, TP 3 x body
    bullishPinBar = lowerWick > 0.6 x range and body < 0.3 x range and close > open and close > sma50 and volume > sma(volume, 20) -> entry Bullish Pin Bar;  bearish mirror -> entry Bearish Pin Bar
    exit("Exit Long", stop = low - 2 x body, limit = high + 3 x body) every bar;  exit("Exit Short", stop = high + 2 x body, limit = low - 3 x body) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent every bar from the current bar's low, high and body, so they move with
      each bar; the port fixes them at the signal bar as fractions of the fill (mark
      trailing_stop_pending; 1e-6 floor). The RSI is computed but unused. REVERSAL INTENDED. No sizing code.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; body-based bracket fixed at the signal bar as fractions of the fill.
    2 generic: PASS, trend-filtered pin bars on above-average volume.
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

NAME = "fmz_453669_trend_filtered_pin_bar_body_bracket_1h_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "wick": [0.6, 0.5],
    "sma_len": [50, 100],
}
DEFAULT_PARAMS = {"wick": 0.6, "body": 0.3, "sma_len": 50, "sl_bodies": 2.0, "tp_bodies": 3.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    rng = h - lo
    upper_w = h - np.maximum(o, c)
    lower_w = np.minimum(o, c) - lo
    body = (c - o).abs()
    sma = c.rolling(int(p["sma_len"])).mean()
    vol_ok = v > v.rolling(20).mean()
    wk, bd = float(p["wick"]), float(p["body"])
    bull = (lower_w > wk * rng) & (body < bd * rng) & (c > o) & (c > sma) & vol_ok
    bear = (upper_w > wk * rng) & (body < bd * rng) & (c < o) & (c < sma) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return bull.astype(bool), false, bear.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs()
    sb, tb = float(p["sl_bodies"]), float(p["tp_bodies"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (lo - sb * body).shift(1) / o)
            .mask(sf, (h + sb * body).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (h + tb * body).shift(1) / o - 1)
            .mask(sf, 1 - (lo - tb * body).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
