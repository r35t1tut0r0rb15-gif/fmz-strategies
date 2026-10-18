"""123 reversal state with a price-to-average distance state, 3-minute bars: both long opens a long, both short opens a short, any other
combination closes (the "Trade reverse" input flips the side).
Port of FMZ strategy #435701 "Dual Moving Average Reversal Breakout Strategy" (Combo Backtest 123 Difference between price and MA).

FMZ source id: 435701

Source
    https://www.fmz.com/strategy/435701 (PineScript v4, FMZ last modified 2023-12-18 10:24:08).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 173-213), stoch 14 (K smoothing 1, D 3, level 50); distance to the SMA 14 in percent, zones 0.03 (buy) / 0.54 (sell)
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  the mirror -> -1;  else the last state
    DBP: nRes = |close - sma(close, 14)| 100 / close;  pos = nRes < 0.03 ? 1 : nRes > 0.54 ? -1 : last
    pos = both 1 -> 1;  both -1 -> -1;  else 0;  possig = reverse ? -pos : pos;  entry long / short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Two persistent states combined; a flip from one agreed side to the other on one bar is a
      reversal (REVERSAL INTENDED); any disagreement closes. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pattern state and a percent distance to an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #427883, Jaccard 0.657); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435701_reversal_123_price_ma_distance"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length_dbp": [14, 28],
}
DEFAULT_PARAMS = {"reverse": False, "length_dbp": 14, "sell_zone": 0.54, "buy_zone": 0.03, "length": 14,
                  "k_smooth": 1, "d_len": 3, "level": 50}


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
    dist = (c - c.rolling(int(p["length_dbp"])).mean()).abs() * 100 / c
    b = _state((dist < float(p["buy_zone"])).to_numpy(), (dist > float(p["sell_zone"])).to_numpy())
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
