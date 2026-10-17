"""Stochastic crosses against an Ichimoku trend line, 1-hour bars: the stochastic K (20, smoothed 5) crossing above its D
below 65 with the close above the average of the two leading spans goes long; K crossing under D above 25 with the close
below it goes short; the 1800-tick target and 1200-tick stop become ATR fractions.
Port of FMZ strategy #432182 "基于ICHIMOKU形态和STOCH指标的趋势跟踪策略ICHIMOKU-Cloud-and-STOCH-Indicator-Based-Trend-Tracking-Strategy" (ICHI + STOCH V1).

FMZ source id: 432182

Source
    https://www.fmz.com/strategy/432182 (PineScript v5, FMZ last modified 2023-11-15 11:19:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-219), stoch 20 / 5 / 3, levels 25 / 65, Ichimoku 9 / 26 / 52, displacement 1, TP 1800 / SL 1200 ticks
    k = sma(stoch(close, high, low, 20), 5); d = sma(k, 3)
    trend = ema(avg(avg(conv, base), avg(lowest(52), highest(52))), 1)
    crossover(k, d) and k < 65 and close > trend -> entry long, exit(profit = 1800, loss = 1200)
    crossunder(k, d) and k > 25 and close < trend -> entry short, same exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: profit = 1800 and loss = 1200 ticks (180 / 120 USD on BTC_USDT, mintick 0.1)
      become tp_atr / sl_atr x the Wilder ATR 14 of the signal bar as fractions of its close (about
      0.9 / 0.6 ATR on hourly BTC), shifted one bar inside stops() and re-based on the fill.
    * The inputs named OverBought (25) and OverSold (65) are used as written (k < 65 for longs, k > 25
      for shorts). ema(x, 1) is x; the spans' plot offset only moves the drawing. ta.lowest /
      ta.highest default to low / high and include the current bar.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits are ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_432182_ichimoku_trend_stoch_cross"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.6, 1.5],
    "tp_atr": [0.9, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "smooth_k": 5, "smooth_d": 3, "ob": 25, "os": 65, "conv": 9, "base": 26,
                  "span_b": 52, "atr_len": 14, "sl_atr": 0.6, "tp_atr": 0.9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    mid = lambda m: (lo.rolling(m).min() + h.rolling(m).max()) / 2  # noqa: E731
    lead1 = (mid(int(p["conv"])) + mid(int(p["base"]))) / 2
    lead2 = mid(int(p["span_b"]))
    trend = (lead1 + lead2) / 2
    co = (k > d) & (k.shift(1) <= d.shift(1))
    cu = (k < d) & (k.shift(1) >= d.shift(1))
    le = (co & (k < float(p["os"])) & (c > trend)).astype(bool)
    se = (cu & (k > float(p["ob"])) & (c < trend)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
