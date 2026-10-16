"""HPotter combo, 1-hour bars: the 123 reversal and Gimelfarb's bull-and-bear balance (its price-unit levels +-15 as ATR
fractions) must agree; both long holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #430543 "Dual Balanced Bulls and Bears Strategy" (Combo Backtest 123 Reversal & Bull And Bear Balance).

FMZ source id: 430543

Source
    https://www.fmz.com/strategy/430543 (PineScript v4, FMZ last modified 2023-10-30 10:32:53).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 146-202), stochastic 14 / 1 / 3, level 50; balance levels -15 / 15 (price units)
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    nBBB = value2 - value (the source's nested bar-shape cases, bull minus bear pressure, price units)
    nBBB < -15 -> -1;  nBBB >= 15 -> 1;  else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels -15 / 15 are price units; they become -+zone_atr x Wilder ATR(14) of the
      same bar (15 USD is about 0.1 ATR on 1-hour BTC). The nested iff cases are transcribed exactly.
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit balance levels -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND430543 (3 members, best partner #443036, Jaccard 0.749); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430543_combo_123_bull_bear_balance"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "zone_atr": [0.1, 0.5],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "zone_atr": 0.1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _balance(bars):
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    c1 = np.concatenate(([np.nan], c[:-1]))
    w = np.where
    mx = np.maximum
    hl = h - lo
    down, up = c < o, c > o
    upper_wick = (h - c) > (c - lo)
    lower_wick = (h - c) < (c - lo)
    value = w(down, w(c1 > o, mx(c - o, hl), hl),
              w(up, w(c1 > o, mx(c1 - lo, h - c), mx(o - lo, h - c)),
                w(upper_wick, w(c1 > o, mx(c1 - o, hl), hl),
                  w(lower_wick, w(up, mx(c - lo, h - c), o - lo),
                    w(up, mx(c1 - o, h - c), w(c1 < o, mx(o - lo, h - c), hl))))))
    value2 = w(down, w(c1 < o, mx(h - c1, c - lo), mx(h - o, c - lo)),
               w(up, w(c1 > o, hl, mx(o - c1, hl)),
                 w(upper_wick, w(c1 < o, mx(h - c1, c - lo), h - o),
                   w(lower_wick, w(c1 > o, hl, mx(o - c, hl)),
                     w(c1 > o, mx(h - o, c - lo), w(c1 < o, mx(o - c, hl), hl))))))
    return value2 - value


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    bbb = _balance(bars_df)
    zone = (float(p["zone_atr"]) * _atr(bars_df, ATR_LEN)).to_numpy()
    sell, buy = bbb < -zone, bbb >= zone
    m = len(c)
    pos2 = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if sell[i]:
            q = -1
        elif buy[i]:
            q = 1
        pos2[i] = q
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
