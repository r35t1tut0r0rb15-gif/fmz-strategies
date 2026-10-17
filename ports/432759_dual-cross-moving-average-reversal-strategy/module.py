"""HPotter combo of the 123 reversal and Gimelfarb's bear power, 10-minute bars: long while both sides say up, short while
both say down, flat otherwise. The bear-power side (the source's nested bar-shape cases, in price units) is down above
its sell level and up at or below its buy level; the levels 30 / 3 become ATR fractions.
Port of FMZ strategy #432759 "Dual Cross Moving Average Reversal Strategy" (Combo Backtest 123 Reversal & Bear Power).

FMZ source id: 432759

Source
    https://www.fmz.com/strategy/432759 (PineScript v3, FMZ last modified 2023-11-21 11:28:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 163-208), stoch 14 / 1 / 3, level 50, bear power sell 30 / buy 3 (price units), reverse false
    value = the source's nested iff cases on close / open / high / low / close[1] (bear pressure, price units)
    pbp = value > 30 ? -1 : value <= 3 ? 1 : pbp[1];  p123 as Reversal123(14, 1, 3, 50)
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels 30 / 3 are price units; they become sell_atr / buy_atr x Wilder ATR(14)
      of the same bar (about 0.3 / 0.03 ATR on 10-minute BTC, ATR about 100 USD). The nested iff cases
      are transcribed exactly (as #430543).
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      reverse is false. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit bear-power levels -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430543 (3 members, best partner #430543, Jaccard 0.660); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432759_combo_123_bear_power"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sell_atr": [0.3, 1.0],
    "buy_atr": [0.03, 0.3],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50, "atr_len": 14, "sell_atr": 0.3,
                  "buy_atr": 0.03}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _bear_power(o, h, lo, c, c1):
    """The source's nested iff cases, transcribed one for one."""
    if c < o:
        return max(c - o, h - lo) if c1 > o else h - lo
    if c > o:
        return max(c1 - lo, h - c) if c1 > o else max(o - lo, h - c)
    if h - c > c - lo:
        return max(c1 - o, h - lo) if c1 > o else h - lo
    if h - c < c - lo:
        return max(c - lo, h - c) if c > o else o - lo
    if c > o:
        return max(c1 - o, h - c)
    return max(o - lo, h - c) if c1 < o else h - lo


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    lv = float(p["level"])
    c1s, c2s = c.shift(1), c.shift(2)
    a_up = ((c2s < c1s) & (c > c1s) & (k < d) & (k > lv)).to_numpy()
    a_dn = ((c2s > c1s) & (c < c1s) & (k > d) & (k < lv)).to_numpy()
    tr = pd.concat([h - lo, (h - c1s).abs(), (lo - c1s).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    ov, hv, lw, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    sa, ba = float(p["sell_atr"]), float(p["buy_atr"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = s2 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        if i >= 1:
            v = _bear_power(ov[i], hv[i], lw[i], cv[i], cv[i - 1])
            if v > sa * atr[i]:
                s2 = -1
            elif v <= ba * atr[i]:
                s2 = 1
        tgt[i] = 1 if (s1 == 1 and s2 == 1) else (-1 if (s1 == -1 and s2 == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
