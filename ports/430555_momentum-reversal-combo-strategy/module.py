"""HPotter combo, 1-hour bars: the 123 reversal and Ehlers' detrended synthetic price (EMA 14 minus EMA 28 of hl2, its
price-unit band as an ATR fraction; as written long above -band, otherwise short) must agree; both long holds a long,
both short holds a short, any disagreement closes everything.
Port of FMZ strategy #430555 "Momentum Reversal Combo Strategy" (Combo Backtest 123 Reversal & D_DSP (Detrended Synthetic Price) V 2).

FMZ source id: 430555

Source
    https://www.fmz.com/strategy/430555 (PineScript v4, FMZ last modified 2023-10-30 11:49:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 156-195), stochastic 14 / 1 / 3, level 50; DSP 14, SellBand -25, BuyBand 25 (price units)
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    dsp = ema(hl2, 14) - ema(hl2, 28); dsp > -25 -> 1; dsp < 25 -> -1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the second state is 1 whenever dsp > SellBand (-25) and -1 otherwise (the BuyBand
      test is then always true): kept.
    * Criterion 2: the band 25 is in price units; it becomes zone_atr x Wilder ATR(14) of the same bar
      (25 USD is about 0.15 ATR on 1-hour BTC).
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit band -> an ATR fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430555 (2 members, best partner #440511, Jaccard 0.847); ND426888 (31 members, best partner #431408, Jaccard 0.661); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430555_combo_123_dsp"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "length_dsp": [14, 28],
    "zone_atr": [0.15, 0.5],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_dsp": 14, "zone_atr": 0.15}


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


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    hl2 = (h + lo) / 2
    L = int(p["length_dsp"])
    dsp = hl2.ewm(span=L, adjust=False).mean() - hl2.ewm(span=2 * L, adjust=False).mean()
    band = float(p["zone_atr"]) * _atr(bars_df, ATR_LEN)
    pos2 = _hold((dsp > -band).to_numpy(), (dsp < band).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
