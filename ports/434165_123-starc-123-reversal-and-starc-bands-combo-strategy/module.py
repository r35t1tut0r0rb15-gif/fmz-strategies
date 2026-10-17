"""HPotter combo of the 123 reversal and STARC bands, 45-minute bars: long while both sides say up, short while both say
down, flat otherwise. The STARC side is up after a close above SMA 5 + 1.33 ATR 15 and down after a close below SMA 5 -
1.33 ATR 15.
Port of FMZ strategy #434165 "123反转与STARC波段组合策略123-Reversal-and-STARC-Bands-Combo-Strategy" (Combo Backtest 123 Reversal & STARC Bands).

FMZ source id: 434165

Source
    https://www.fmz.com/strategy/434165 (PineScript v4, FMZ last modified 2023-12-04 13:38:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 169-211), stoch 14 / 1 / 3, level 50; STARC MA 5, ATR 15, K 1.33; reverse false
    p123 as Reversal123(14, 1, 3, 50);  pstarc = close > sma(5) + 1.33 atr(15) ? 1 : close < sma(5) - 1.33 atr(15) ? -1 : pstarc[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      reverse is false. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and ATR bands.
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

NAME = "fmz_434165_combo_123_starc"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "k": [1.33, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "ma_len": 5, "atr_len": 15, "k": 1.33}


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
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    ma = c.rolling(int(p["ma_len"])).mean()
    up, dn = ma + atr * float(p["k"]), ma - atr * float(p["k"])
    pst = _hold((c > up).to_numpy(), (c < dn).to_numpy())
    tgt = np.where((p123 == 1) & (pst == 1), 1, np.where((p123 == -1) & (pst == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
