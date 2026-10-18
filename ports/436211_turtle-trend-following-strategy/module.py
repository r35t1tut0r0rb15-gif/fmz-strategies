"""Counter-trend Turtle breakouts with pin-bar exits, 1-minute bars: a close over the 50-bar high of five bars back in a down trend (EMA 15 under SMA 220) goes SHORT; a close under the 50-bar low of five bars
back in an up trend (EMA 15 over SMA 220, open over it) goes LONG; a bullish pin bar closes the short and a bearish pin bar closes the long.
Port of FMZ strategy #436211 "Turtle trend Following Strategy" (帆船探险寻找传说 (Turtle trend)).

FMZ source id: 436211

Source
    https://www.fmz.com/strategy/436211 (PineScript v5, FMZ last modified 2023-12-22 11:41:30).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 136-179), channel 50; EMA 15 / SMA 120 / SMA 220; trend test on the long average; date window true
    shortTrend = ema15 < sma220;  longTrend = ema15 > sma220 and open > sma220;  close > highest(50)[5] and shortTrend -> entry short;  close < lowest(50)[5] and longTrend -> entry long
    bullPinBar -> close short;  bearPinBar -> close long   (pin bars from the candle's body and wicks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(50) / lowest(50) read the highs / lows; the channel is taken five bars back. The pin-bar
      shapes use fractions of the bar's own range (0.66 / 0.9 / 0.75): no price constants. The four orders
      of one bar are filled in the script's call order at the next open (entry short, entry long, close
      short, close long). REVERSAL INTENDED. The date window is the default (always true). FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts and candle shapes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436211_turtle_counter_trend_pin_exits"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [50, 100],
    "length3": [220, 100],
}
DEFAULT_PARAMS = {"a": 50, "length1": 15, "length3": 220}


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
    a = int(p["a"])
    shallow = h.rolling(a).max().shift(5)
    deep = lo.rolling(a).min().shift(5)
    s1 = c.ewm(span=int(p["length1"]), adjust=False).mean()
    s3 = c.rolling(int(p["length3"])).mean()
    long_trend = (s1 > s3) & (o > s3)
    short_trend = s1 < s3
    rng = h - lo
    bull_pin = ((c > o) & ((o - lo) > 0.66 * rng)) | ((c < o) & ((c - lo) > 0.9 * rng))
    bear_pin = ((c > o) & ((h - c) > 0.75 * rng)) | ((c < o) & ((h - o) > 0.9 * rng))
    e_s = ((c > shallow) & short_trend).fillna(False).to_numpy()
    e_l = ((c < deep) & long_trend).fillna(False).to_numpy()
    c_s = bull_pin.fillna(False).to_numpy()
    c_l = bear_pin.fillna(False).to_numpy()
    m = len(e_s)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a1, b1, c1, d1 = pend
            if a1 and pos >= 0:
                pos = -1
            if b1 and pos <= 0:
                pos = 1
            if c1 and pos == -1:
                pos = 0
            if d1 and pos == 1:
                pos = 0
        held[i] = pos
        pend = (bool(e_s[i]), bool(e_l[i]), bool(c_s[i]), bool(c_l[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
