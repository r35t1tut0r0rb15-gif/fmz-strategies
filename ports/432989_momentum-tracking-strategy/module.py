"""Candle-size trend follower, 1-hour bars, long only: "buy" is on while the EMA 8 of the closes is above the EMA 8 of the
opens, unless the candle is a mid-sized red one or a green candle classed as big; its switch on opens a long, its
switch off closes it. The price-unit size classes 1400 / 2100 / 3800 become ATR multiples.
Port of FMZ strategy #432989 "Momentum Tracking Strategy" (Trend Follower Strategy v2 [divonn1994]).

FMZ source id: 432989

Source
    https://www.fmz.com/strategy/432989 (PineScript v5, FMZ last modified 2023-11-23 13:47:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 100-129), timesBigger 2, crumb 1400, crumb2 2100, big candle 3800 (price units)
    crumb = |body| <= 1400;  bigCrumb = 1400 < |body| <= 2100 (each by candle colour);  the same for the previous candle
    bigCandle = green and (prev bigCrumb and body >= 2 |prev body|, or prev crumb and body >= 3800, or prev neither and body >= 2 |prev body|)
    buy = (not crumb and not bigCrumb and red) or (green and bigCandle) or ema(close, 8) <= ema(open, 8) ? 0 : 1
    crossover(buy, 0.5) -> entry long;  crossunder(buy, 0.5) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the three size classes are price units (BTC); they become crumb_atr x Wilder ATR 14
      of the same bar, with crumb2 and the big-candle size kept in the source's ratios 1.5 and
      3800 / 1400. On hourly BTC in the header window (ATR about 250 USD) 1400 is about 5.6 ATR.
    * emaAlert is "ema(close, 8) > ema(open, 8)". A doji (close = open) counts as red, as written.
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit candle sizes -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432989_candle_size_trend_follower"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "crumb_atr": [5.6, 1.0],
    "ema_len": [8, 16],
}
DEFAULT_PARAMS = {"crumb_atr": 5.6, "ema_len": 8, "times_bigger": 2.0, "atr_len": 14}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    s1 = float(p["crumb_atr"]) * atr
    s2 = s1 * 2100 / 1400
    sb = s1 * 3800 / 1400
    n = int(p["ema_len"])
    alert = c.ewm(span=n, adjust=False).mean() > o.ewm(span=n, adjust=False).mean()
    size = c - o
    psize = size.shift(1)
    green = c > o
    pgreen = c1 > o.shift(1)
    crumb = (green & (size <= s1)) | (~green & (-size <= s1))
    big_crumb = (green & (size <= s2) & (size > s1)) | (~green & (-size <= s2) & (-size > s1))
    p_small = (pgreen & (psize <= s1)) | (~pgreen & (-psize <= s1))
    p_big = (pgreen & (psize <= s2) & (psize > s1)) | (~pgreen & (-psize <= s2) & (-psize > s1))
    tb = float(p["times_bigger"])
    big = ((green & p_big & (size >= (tb * psize).abs())) | (green & p_small & (size >= sb))
           | (green & ~p_small & ~p_big & (size >= (tb * psize).abs())))
    off = (~crumb & ~big_crumb & ~green) | (green & big) | ~alert
    buy = (~off).to_numpy()
    prev = np.concatenate(([False], buy[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy & ~prev, index=ix), pd.Series(~buy & prev, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
