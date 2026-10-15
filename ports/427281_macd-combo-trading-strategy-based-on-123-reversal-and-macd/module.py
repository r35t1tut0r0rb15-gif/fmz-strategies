"""Combo: 123 reversal and Ergodic MACD: long while both the 123-reversal state (stochastic 14 /
1 / 3, level 50) and the EMA 14/21 MACD-versus-signal state are long, short while both are short,
flat otherwise.
Port of FMZ strategy #427281 "Combo Trading Strategy Based on 123 Reversal and MACD".

FMZ source id: 427281

Source
    https://www.fmz.com/strategy/427281 (PineScript v4, FMZ last modified 2023-09-19 17:17:30).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 197-246), 123: 14 / 1 / 3 / 50; MACD r 14, slow 21, signal 5
    vFast = sma(stoch(close, high, low, 14), 1); vSlow = sma(vFast, 3)
    p123 = close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 ? 1
         : close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < 50 ? -1 : p123[1]
    m = ema(close, 14) - ema(close, 21); pM = m < ema(m, 5) ? -1 : m > ema(m, 5) ? 1 : pM[1]
    both 1 -> entry long; both -1 -> entry short; otherwise -> close_all

Interpretation choices (Pine rules in SURVEY_README.md; as worker A's 123-reversal combos)
    * fADX is defined but never used. "Trade reverse" is off.
    * A long-to-short change in one bar reverses (REVERSAL INTENDED); disagreement closes.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427281_combo_123_ergodic_macd"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "level": [50, 40],
    "r": [14, 9],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "r": 14,
                  "length_macd": 21, "smth_len": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _state(up, dn):
    """iff(up, 1, iff(dn, -1, nz(prev, 0))) as a persistent state."""
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
    return out


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
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    fast = st.rolling(int(p["k_smoothing"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lvl = p["level"]
    up123 = ((c2 < c1) & (c > c1) & (fast < slow) & (fast > lvl)).to_numpy()
    dn123 = ((c2 > c1) & (c < c1) & (fast > slow) & (fast < lvl)).to_numpy()
    s123 = _state(up123, dn123)
    macd = c.ewm(span=int(p["r"]), adjust=False).mean() - c.ewm(span=int(p["length_macd"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["smth_len"]), adjust=False).mean()
    smacd = _state((macd > sig).to_numpy(), (macd < sig).to_numpy())
    tgt = np.where((s123 == 1) & (smacd == 1), 1, np.where((s123 == -1) & (smacd == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
