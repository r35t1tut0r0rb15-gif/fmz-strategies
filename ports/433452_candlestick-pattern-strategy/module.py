"""Eleven bullish and eight bearish candle patterns, 5-minute bars: any bullish pattern (engulfing, harami, piercing line,
morning star, belt hold, three white soldiers, three stars in the south, stick sandwich, meeting line, kicking, ladder
bottom) goes long, any bearish one goes short; each trade carries a 100-tick stop and a 1000-tick target, which become
ATR multiples.
Port of FMZ strategy #433452 "Candlestick Pattern Strategy" (Candle Patterns Strategy (CPS)).

FMZ source id: 433452

Source
    https://www.fmz.com/strategy/433452 (PineScript v4, FMZ last modified 2023-11-27 18:26:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-260), all patterns on; SL 100, TP 1000, trail points 40 (ticks); session "0000-0000"
    SignalUp = any bullish pattern (the source's exact OHLC comparisons, equalities included);  SignalDown = any bearish one
    SignalUp and session_open -> entry long;  SignalDown -> entry short;  exit(profit = 1000, trail_points = 40, loss = 100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bracket is in ticks (10 / 100 USD on the header's BTC_USDT, mintick 0.1, about
      0.2 / 2 ATR of 5-minute BTC, ATR about 50 USD). It becomes sl_atr / tp_atr x Wilder ATR 14 of the
      signal bar as fractions of its close, shifted one bar inside stops() and re-based on the fill.
    * trail_points without trail_offset sets only an activation level, so no trailing stop is placed
      (dropped). The session "0000-0000" is the whole day, so the session close-outs never fire.
    * Both pattern groups on one bar: the short entry is issued last and the bar ends short.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG433452 (3 members, best partner #442121, Jaccard 0.982); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the session "0000-0000" is the whole day).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433452_candle_patterns_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.2, 1.0],
    "tp_atr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.2, "tp_atr": 2.0, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _patterns(bars_df):
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def s(x, k):
        return x.shift(k)

    def avg(a, b):
        return (a + b) / 2

    o1, o2, o3, o4 = s(o, 1), s(o, 2), s(o, 3), s(o, 4)
    h1, h2 = s(h, 1), s(h, 2)
    l1, l2, l3, l4 = s(l, 1), s(l, 2), s(l, 3), s(l, 4)
    c1, c2, c3, c4 = s(c, 1), s(c, 2), s(c, 3), s(c, 4)
    b_eng = (h > h1) & (l < l1) & (o < o1) & (c > c1) & (c > o) & (c1 < c2) & (c > o1)
    s_eng = (h > h1) & (l < l1) & (o > o1) & (c < c1) & (c < o) & (c1 > c2) & (c < o1)
    b_har = (o1 > c1) & (c1 < c2) & (o > c1) & (o < o1) & (c > c1) & (c < o1) & (h < h1) & (l > l1) & (c >= o)
    s_har = (o1 < c1) & (c1 > c2) & (o < c1) & (o > o1) & (c < c1) & (c > o1) & (h < h1) & (l > l1) & (c <= o)
    pierce = (c2 > c1) & (o < l1) & (c > avg(o1, c1)) & (c < o1)
    dark = (c2 < c1) & (o > h1) & (c < avg(o1, c1)) & (c > o1)
    m_star = (c3 > c2) & (c2 < o2) & (o1 < c2) & (c1 < c2) & (o > o1) & (o > c1) & (c > c2) & (o2 - c2 > c - o)
    e_star = (c3 < c2) & (c2 > o2) & (o1 > c2) & (c1 > c2) & (o < o1) & (o < c1) & (c < c2) & (c2 - o2 > o - c)
    b_belt = (c1 < o1) & (l1 > o) & (c1 > o) & (o == l) & (c > avg(c, o))
    s_belt = (c1 > o1) & (h1 < o) & (c1 < o) & (o == h) & (c < avg(c, o))
    tws = ((c3 < o3) & (o2 < c3) & (c2 > avg(c2, o2)) & (o1 > o2) & (o1 < c2) & (c1 > avg(c1, o1)) & (o > o1)
           & (o < c1) & (c > avg(c, o)) & (h1 > h2) & (h > h1))
    tbc = ((c3 > o3) & (o2 > c3) & (c2 < avg(c2, o2)) & (o1 < o2) & (o1 > c2) & (c1 < avg(c1, o1)) & (o < o1)
           & (o > c1) & (c < avg(c, o)) & (l1 < l2) & (l < l1))
    h_2 = h2
    tss = ((o3 > c3) & (o2 > c2) & (o2 == h_2) & (o1 > c1) & (o1 < o2) & (o1 > c2) & (l1 > l2) & (o1 == h1)
           & (o > c) & (o < o1) & (o > c1) & (o == h) & (c == l) & (c >= l1))
    stick = (o2 > c2) & (o1 > c2) & (o1 < c1) & (o > c1) & (o > c) & (c == c2)
    b_ml = (o2 > c2) & (o1 > c1) & (c1 == c) & (o < c) & (o1 >= h)
    s_ml = (o2 < c2) & (o1 < c1) & (c1 == c) & (o > c) & (o1 <= l)
    b_kick = (o1 > c1) & (o1 == h1) & (c1 == l1) & (o > o1) & (o == l) & (c == h) & (c - o > o1 - c1)
    s_kick = (o1 < c1) & (o1 == l1) & (c1 == h1) & (o < o1) & (o == h) & (c == l) & (o - c > c1 - o1)
    ladder = ((o4 > c4) & (o3 > c3) & (o3 < o4) & (o2 > c2) & (o2 < o3) & (o1 > c1) & (o1 < o2) & (o < c) & (o > o1)
              & (l4 > l3) & (l3 > l2) & (l2 > l1))
    up = b_eng | b_har | pierce | m_star | b_belt | tws | tss | stick | b_ml | b_kick | ladder
    dn = s_eng | s_har | dark | e_star | s_belt | tbc | s_ml | s_kick
    return up.to_numpy(), dn.to_numpy()


def _af(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    up, dn = _patterns(bars_df)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up & ~dn, index=ix), false, pd.Series(dn, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _af(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
