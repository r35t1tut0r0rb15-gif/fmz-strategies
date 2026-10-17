"""HPotter combo of the 123 reversal and a displaced EMA envelope, 2-hour bars: long while both say up, short while both say
down, flat otherwise. The envelope side is up after a close under the EMA 9 of 13 bars ago less 0.5 % and down after a
close over it plus 0.5 %.
Port of FMZ strategy #434611 "Dual Moving Average Price Reversal Breakout Strategy" (Combo Backtest 123 Reversal & MA Displaced Envelope).

FMZ source id: 434611

Source
    https://www.fmz.com/strategy/434611 (PineScript v4, FMZ last modified 2023-12-07 18:15:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 198-241), stoch 14 / 1 / 3, level 50; EMA 9 on close, +/- 0.5 %, displacement 13; reverse false
    p123 as Reversal123(14, 1, 3, 50);  made = close < ema9[13] x 0.995 ? 1 : close > ema9[13] x 1.005 ? -1 : made[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The envelope side has no nz: it is na (neither side) until its first break, then held. The
      envelope is contrarian (a close under it is "up"), as written. strategy.entry reverses:
      REVERSAL INTENDED. reverse is false. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a percent envelope.
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

NAME = "fmz_434611_combo_123_displaced_envelope"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "pct": [0.5, 1.0],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "period": 9, "pct": 0.5, "disp": 13}


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
    p123 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    e = c.ewm(span=int(p["period"]), adjust=False).mean().shift(int(p["disp"]))
    pc = float(p["pct"])
    made = _hold((c < e * (100 - pc) / 100).to_numpy(), (c > e * (100 + pc) / 100).to_numpy())
    tgt = np.where((p123 == 1) & (made == 1), 1, np.where((p123 == -1) & (made == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
