"""123 reversal state with a Keltner channel state, 1-hour bars: both long opens a long, both short opens a short, any other combination
closes (the "Trade reverse" input flips the side).
Port of FMZ strategy #435837 "Dual Factor Mean Reversion Tracking Strategy" (Combo Backtest 123 Reversal & Keltner Channel).

FMZ source id: 435837

Source
    https://www.fmz.com/strategy/435837 (PineScript v4, FMZ last modified 2023-12-19 11:09:20).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 148-186), stoch 14 (K smoothing 1, D 3, level 50); Keltner period 10 (SMA of hlc3 +- SMA of the range)
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  the mirror -> -1;  else the last state
    Keltner: xPrice = sma(hlc3, 10);  xMove = sma(high - low, 10);  pos = close < xPrice - xMove ? -1 : close > xPrice + xMove ? 1 : last
    pos = both 1 -> 1;  both -1 -> -1;  else 0;  possig = reverse ? -pos : pos;  entry long / short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel state is breakout = trend (a close over the upper band is +1). The "reverse" input
      inside the channel function is a local that is never used; the global one flips the side. Two
      persistent states combined; a flip from one agreed side to the other on one bar is a reversal
      (REVERSAL INTENDED); any disagreement closes. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pattern state and a channel state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.659); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435837_reversal_123_keltner_channel"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "n_period": [10, 20],
}
DEFAULT_PARAMS = {"reverse": False, "n_period": 10, "length": 14, "k_smooth": 1, "d_len": 3, "level": 50}


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
    k = int(p["n_period"])
    price = ((h + lo + c) / 3).rolling(k).mean()
    move = (h - lo).rolling(k).mean()
    b = _state((c > price + move).to_numpy(), (c < price - move).to_numpy())
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
