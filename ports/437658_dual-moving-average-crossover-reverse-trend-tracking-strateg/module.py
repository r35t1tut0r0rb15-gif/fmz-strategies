"""123 reversal and SMA-against-its-EMA combination, 3-minute bars: the 123 reversal state (two closes against a stochastic 14 test) and the SMA 10 above its EMA 10 (long) or below (short) agreeing long go long,
agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437658 "Dual Moving Average Crossover Reverse Trend Tracking Strategy" (Combo Backtest 123 Reversal & EMA & MA Crossover).

FMZ source id: 437658

Source
    https://www.fmz.com/strategy/437658 (PineScript v4, FMZ last modified 2024-01-04 15:48:15).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 192-228), 123: length 14, K smoothing 1, D 3, level 50; MA 10, EMA 10; reverse off
    MACross: xMA = sma(close, 10), xEMA = ema(xMA, 10);  pos = 1 if xEMA < xMA, -1 if xEMA > xMA, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The state is a level, so the entry is sent on every bar of the
      state; state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and an average comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #437515, Jaccard 0.664); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437658_reversal123_ma_ema_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_ma": [10, 20],
}
DEFAULT_PARAMS = {"length": 14, "length_ma": 10, "length_ema": 10, "k_smoothing": 1, "d_length": 3,
                  "level": 50.0, "reverse": False}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    xma = c.rolling(int(p["length_ma"])).mean()
    xema = xma.ewm(span=int(p["length_ema"]), adjust=False).mean()
    lo_, hi_ = (xema < xma).to_numpy(), (xema > xma).to_numpy()
    m = len(c)
    sig = np.zeros(m)
    p123 = pm = 0.0
    for i in range(m):
        if up_[i]:
            p123 = 1.0
        elif dn_[i]:
            p123 = -1.0
        if lo_[i]:
            pm = 1.0
        elif hi_[i]:
            pm = -1.0
        sig[i] = 1.0 if (p123 == 1.0 and pm == 1.0) else (-1.0 if (p123 == -1.0 and pm == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
