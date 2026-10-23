"""A volume-weighted momentum index (EMA 100 of volume x the 50-bar close change) with N-bar range breaks, hourly bars: a positive index with the high at the 100-bar highest high goes long, a negative index with the low at the 100-bar lowest low goes short; the index turning against the position or a 2 % close against the signal close closes; reversing.
Port of FMZ strategy #128125 "Break High and Low Volume Index Weighting Strategy" (Break High and Low Volume Index Weighting Strategy).

FMZ source id: 128125

Source
    https://www.fmz.com/strategy/128125 (MyLanguage, FMZ last modified 2018-12-15 15:42:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 59-91), MyLanguage, AUTOFILTER; N 100 (backtest args; input default 300), NC 50, SLOSS 2 %; LOTS from MONEYTOT
    VJQ := EMA(V x (C - REF(C, NC)), N);  B := VJQ > 0;  S := VJQ < 0
    BARPOS > N and SKVOL = 0 and S and L <= LLV(L, N) -> SPK;  BARPOS > N and BKVOL = 0 and B and H >= HHV(H, N) -> BPK
    SKVOL > 0 and B -> BP;  BKVOL > 0 and S -> SP;  C >= SKPRICE x 1.02 -> BP;  C <= BKPRICE x 0.98 -> SP

Interpretation choices (rules in SURVEY_README.md)
    * MyLanguage close-price model and AUTOFILTER (SURVEY_README MyLanguage rules): one signal per bar,
      the first valid statement in source order winning; BPK / SPK reverse. BKPRICE / SKPRICE are the
      signal bars' closes, so the 2 % stops are close tests against them (exit signals). N is the
      backtest header's 100 (the input default 300 is in the grid). HHV / LLV include the current bar.
      REVERSAL INTENDED. The LOTS formula (MONEYTOT) is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stops against the signal close.
    2 generic: PASS, volume-weighted momentum sign with range breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: LOTS = max(MINAMOUNT, MONEYTOT / O x 0.8) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in VJQ = EMA(V x (C - REF(C, 50)), N); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_128125_volume_momentum_ema_sign_range_break_pct_stop_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [100, 300],
    "sloss": [2.0, 4.0],
}
DEFAULT_PARAMS = {"n": 100, "sloss": 2.0, "nc": 50}


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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["n"])
    vjq = (v * (c - c.shift(int(p["nc"])))).ewm(span=n, adjust=False).mean()
    b, s = (vjq > 0).to_numpy(), (vjq < 0).to_numpy()
    hh = (h >= h.rolling(n).max()).to_numpy()
    ll = (lo <= lo.rolling(n).min()).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["sloss"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, px = 0, np.nan
    for i in range(m):
        old = pos
        ready = i + 1 > n                                     # BARPOS > N
        if ready and pos != -1 and s[i] and ll[i]:            # SELLPK, SPK
            pos, px = -1, cv[i]
        elif ready and pos != 1 and b[i] and hh[i]:           # BUYPK, BPK
            pos, px = 1, cv[i]
        elif pos == -1 and b[i]:                              # BUYP, BP
            pos = 0
        elif pos == 1 and s[i]:                               # SELLP, SP
            pos = 0
        elif pos == -1 and cv[i] >= px * (1 + k):             # stop, BP
            pos = 0
        elif pos == 1 and cv[i] <= px * (1 - k):              # stop, SP
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
