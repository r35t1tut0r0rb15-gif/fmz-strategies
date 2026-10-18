"""123 reversal state with a range action verification index state, 1-hour bars: both long opens a long, both short opens a short, any other combination
closes (the "Trade reverse" input flips the side).
Port of FMZ strategy #436094 "Dual Indicator Quantitative Strategy" (Combo Backtest 123 Reversal & RAVI).

FMZ source id: 436094

Source
    https://www.fmz.com/strategy/436094 (PineScript v4, FMZ last modified 2023-12-21 10:59:16).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 143-184), stoch 14 (K smoothing 1, D 3, level 50); RAVI = (SMA 7 - SMA 65) / SMA 65 x 100 against 0.14
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  the mirror -> -1;  else the last state
    RAVI: pos = xRAVI > 0.14 ? 1 : xRAVI < 0.14 ? -1 : last;  pos = both 1 -> 1;  both -1 -> -1;  else 0;  possig = reverse ? -pos : pos;  entry long / short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Two persistent states combined; a flip from one agreed side to the other on one bar is a
      reversal (REVERSAL INTENDED); any disagreement closes. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pattern state and a percent index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #440094, Jaccard 0.655); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436094_reversal_123_ravi"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "fast_ma": [7, 5],
}
DEFAULT_PARAMS = {"reverse": False, "fast_ma": 7, "slow_ma": 65, "trade_line": 0.14, "length": 14, "k_smooth": 1,
                  "d_len": 3, "level": 50}


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


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    vf = raw.rolling(int(p["k_smooth"])).mean()
    vs = vf.rolling(int(p["d_len"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lv = float(p["level"])
    a = _state(((c2 < c1) & (c > c1) & (vf < vs) & (vf > lv)).to_numpy(),
               ((c2 > c1) & (c < c1) & (vf > vs) & (vf < lv)).to_numpy())
    maf, mas = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    ravi = (maf - mas) / mas * 100
    tl = float(p["trade_line"])
    b = _state((ravi > tl).to_numpy(), (ravi < tl).to_numpy())
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
