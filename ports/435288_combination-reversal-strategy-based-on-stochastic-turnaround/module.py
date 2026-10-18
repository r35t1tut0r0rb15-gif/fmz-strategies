"""123 reversal state with a key-reversal-up bar, 15-minute bars: a long is taken on a bar where the stochastic 123 pattern state is
long and the bar made a new low under the previous low but closed above the previous close; the position is closed on the
next bar (the key reversal is a one-bar event). The "Trade reverse" input trades the opposite side.
Port of FMZ strategy #435288 "Combination Reversal Strategy Based on Stochastic Turnaround Factor and Key Reversal Signal" (Combo Backtest 123 Reversal & Key Reversal Up).

FMZ source id: 435288

Source
    https://www.fmz.com/strategy/435288 (PineScript v4, FMZ last modified 2023-12-13 17:54:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 151-186), stoch 14 (K smoothing 1, D 3, level 50); key reversal over 1 bar
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  the mirror -> -1;  else the last state
    KRU: low < lowest(low[1], n) and close > close[1];  pos = 123 == 1 and KRU ? 1 : 123 == -1 and KRU == -1 ? -1 : 0   (KRU is 1 or 0, never -1)
    possig = reverse ? -pos : pos;  possig == 1 -> entry long;  possig == -1 -> entry short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The key-reversal state is never -1, so the "-1" branch of the combination cannot occur: the
      strategy opens only on the long condition (or only shorts with the reverse input) and closes
      on the next bar: one-bar trades, as written. A signal bar followed by another signal bar keeps
      the position. The 123 state starts at zero and holds until the opposite pattern. FREQ =
      "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, the short branch cannot occur: one-bar trades as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432921, Jaccard 0.765); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435288_reversal_123_key_reversal_up"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "n_length": [1, 5],
}
DEFAULT_PARAMS = {"reverse": False, "n_length": 1, "length": 14, "k_smooth": 1, "d_len": 3, "level": 50}


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


def _reversal123(h, lo, c, length, k_smooth, d_len, level):
    """Pine's Reversal123 state: 1 / -1 on the pattern, else the last state (0 before any)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(length).min()) / (h.rolling(length).max() - lo.rolling(length).min())
    vf = raw.rolling(k_smooth).mean()
    vs = vf.rolling(d_len).mean()
    c1, c2 = c.shift(1), c.shift(2)
    up = ((c2 < c1) & (c > c1) & (vf < vs) & (vf > level)).to_numpy()
    dn = ((c2 > c1) & (c < c1) & (vf > vs) & (vf < level)).to_numpy()
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
    a = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    ll = lo.shift(1).rolling(int(p["n_length"])).min()
    kru = ((lo < ll) & (c > c.shift(1))).to_numpy()
    pos = np.where((a == 1) & kru, 1, 0).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
