"""Momentum sign with a counter-candle entry, 2-hour bars: while the squeeze momentum value (a 20-bar regression end of the close against the channel / average midpoint) is positive, a red candle with a body over a third
of its 30-bar average goes long; while negative, a green candle with such a body goes short (reversing).
Port of FMZ strategy #436540 "Dual Moving Average Momentum Squeeze Strategy" (Noro's Squeeze Momentum Strategy v1.0).

FMZ source id: 436540

Source
    https://www.fmz.com/strategy/436540 (PineScript v2, FMZ last modified 2023-12-25 17:01:28).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 141-203), BB 20 / 2, KC 20 / 1.5, colour and body filters on
    val = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0);  trend = sign(val);  body = |close - open|;  emabody = ema(body, 30) / 3
    up = trend == 1 and bar == -1 and body > emabody;  dn = trend == -1 and bar == 1 and body > emabody;  entry Long on up, Short on dn

Interpretation choices (Pine rules in SURVEY_README.md)
    * The squeeze flags (Bollinger inside Keltner) only colour the plot; the orders depend on the value's
      sign, the candle colour and the body size. The long / short switches and the date window (always
      true) are on. REVERSAL INTENDED. The percent-of-equity size is sizing. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum sign and candle filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND436540 (2 members, best partner #439960, Jaccard 0.667); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436540_squeeze_momentum_counter_candle"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_kc": [20, 30],
    "body_div": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length_kc": 20, "body_div": 3.0, "ema_body": 30, "use_color": True, "use_body": True}


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


def _linreg_end(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(a.mean() + np.dot(w, a) / sxx * (n - 1) / 2.0), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length_kc"])
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    val = _linreg_end(c - mid, n)
    trend = np.sign(val)
    body = (c - o).abs()
    emabody = body.ewm(span=int(p["ema_body"]), adjust=False).mean() / float(p["body_div"])
    bar = np.sign(c - o)
    big = (body > emabody) | (not p["use_body"])
    up = ((trend == 1) & ((bar == -1) | (not p["use_color"])) & big).fillna(False).astype(bool)
    dn = ((trend == -1) & ((bar == 1) | (not p["use_color"])) & big).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
