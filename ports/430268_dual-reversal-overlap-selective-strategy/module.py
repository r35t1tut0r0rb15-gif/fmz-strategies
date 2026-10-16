"""HPotter combo, 1-hour bars: the 123 reversal and Bressert's double-smoothed stochastic (10 / 9, trigger 5) must agree;
both long holds a long, both short holds a short, any disagreement closes everything.
Port of FMZ strategy #430268 "Dual Reversal Overlap Selective Strategy" (Combo Backtest 123 Reversal & DSS Bressert).

FMZ source id: 430268

Source
    https://www.fmz.com/strategy/430268 (PineScript v4, FMZ last modified 2023-10-26 16:56:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 203-243), stochastic 14 / 1 / 3, level 50; DSS PDS 10, EMA 9, trigger 5, 80 / 20
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    DSS: pre = ema(stoch(close, high, low, 10), 9); dss = ema(stoch(pre, pre, pre, 10), 9); trig = ema(dss, 5)
         trig < dss and trig < 20 -> -1;  trig > dss and trig > 80 -> 1;  else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels.
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

NAME = "fmz_430268_combo_123_dss_bressert"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pds": [10, 20],
    "ema_len": [9, 5],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "pds": 10, "ema_len": 9,
                  "trigger_len": 5, "overbought": 80, "oversold": 20}


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


def _stoch(src, h, lo, n):
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    return 100 * (src - ll) / (hh - ll).replace(0.0, np.nan)


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
    k = _stoch(c, h, lo, int(p["length"])).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    n, e = int(p["pds"]), int(p["ema_len"])
    pre = _stoch(c, h, lo, n).ewm(span=e, adjust=False).mean()
    dss = _stoch(pre, pre, pre, n).ewm(span=e, adjust=False).mean()
    trig = dss.ewm(span=int(p["trigger_len"]), adjust=False).mean()
    pos2 = _hold(((trig > dss) & (trig > p["overbought"])).to_numpy(),
                 ((trig < dss) & (trig < p["oversold"])).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
