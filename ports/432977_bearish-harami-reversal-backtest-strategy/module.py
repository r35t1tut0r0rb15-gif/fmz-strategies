"""HPotter bearish harami, 15-minute bars, short only: a red candle with a body of at least the minimum size inside the
previous green body sets the reference price to its close and holds a short; the short is closed after a bar whose low
reaches the reference minus the target distance or whose high reaches the reference plus the stop distance. The pip
distances 20 / 10 / 3 become ATR multiples.
Port of FMZ strategy #432977 "Bearish Harami Reversal Backtest Strategy" (Bearish Harami Backtest).

FMZ source id: 432977

Source
    https://www.fmz.com/strategy/432977 (PineScript v3, FMZ last modified 2023-11-23 11:47:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-152), take profit 20, stop loss 10, min body 3 (price units)
    harami = |close - open| >= 3 and close[1] > open[1] and open > close and open <= close[1] and open[1] <= close and open - close < close[1] - open[1]
    posprice = harami ? close : posprice[1];  pos = posprice > 0 ? -1 : 0;  pos 0 -> close_all;  pos -1 -> entry short
    then posprice := 0 if low <= posprice - 20, or if high >= posprice + 10 (checked on the bar's own high / low)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the three price-unit distances become tp_atr / sl_atr / body_atr x Wilder ATR 14
      (about 0.33 / 0.17 / 0.05 ATR on 15-minute BTC, ATR about 60 USD). The target and stop distances
      use the ATR of the harami bar, frozen with the reference price; the body test uses the bar's own.
    * The reset tests the completed bar's high and low (the pattern bar's own included, as written), so
      the short ends with a close signal on that bar, filled at the next open: an exit signal, not a
      broker stop. A new harami while short moves the reference price.
    * Short only; Opposite entries cannot occur. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked level exits.
    2 generic: ADAPT, price-unit distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND432977 (2 members, best partner #437682, Jaccard 0.797); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432977_bearish_harami_short"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_atr": [0.33, 1.0],
    "sl_atr": [0.17, 0.5],
}
DEFAULT_PARAMS = {"tp_atr": 0.33, "sl_atr": 0.17, "body_atr": 0.05, "atr_len": 14}


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
    o1 = o.shift(1)
    har = (((c - o).abs() >= p["body_atr"] * atr) & (c1 > o1) & (o > c) & (o <= c1) & (o1 <= c)
           & ((o - c) < (c1 - o1))).to_numpy()
    av, hv, lv, cv = atr.to_numpy(), h.to_numpy(), lo.to_numpy(), c.to_numpy()
    tk, sk = float(p["tp_atr"]), float(p["sl_atr"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    ref, dist_a = 0.0, 0.0
    for i in range(m):
        if har[i]:
            ref, dist_a = cv[i], av[i]
        tgt[i] = -1 if ref > 0 else 0
        if ref > 0 and lv[i] <= ref - tk * dist_a:
            ref = 0.0
        if ref > 0 and hv[i] >= ref + sk * dist_a:
            ref = 0.0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (false, false.copy(), pd.Series((tgt == -1) & (prev == 0), index=ix),
            pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
