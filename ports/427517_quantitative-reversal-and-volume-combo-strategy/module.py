"""HPotter's combo of the 123 reversal state (stochastic 14 / 1 / 3 at 50) and the volatility-adjusted Finite Volume Elements state (22-bar signed volume share against its EMA 40), 15-minute bars: both long goes long, both short goes short, otherwise flat; reversing.
Port of FMZ strategy #427517 "Quantitative Reversal and Volume Combo Strategy" (Combo Backtest 123 Reversal & Volatility Finite Volume Elements).

FMZ source id: 427517

Source
    https://www.fmz.com/strategy/427517 (PineScript v4, FMZ last modified 2023-09-21 21:07:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 222-282), Reversal123 14 / 1 / 3, level 50; FVE samples 22, EMA 40, cutoffs 0.1 / 0.1; reverse off
    FveFactor = MF > CutOff x close ? 1 : MF < -CutOff x close ? -1 : 0, MF = close - hl2 + hlc3 - hlc3[1], CutOff = 0.1 stdev(sma(log(h / l), 22), 22) + 0.1 stdev(sma(log(hlc3 / hlc3[1]), 22), 22)
    xFVE = 100 sum(volume x FveFactor, 22) / sum(volume, 22);  posFVI = xFVE > ema(xFVE, 40) ? 1 : < ? -1 : pos[1];  pos = both 1 -> 1, both -1 -> -1, else 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 state starts at zero and holds until the opposite pattern (as the combo family). stdev is
      Pine's population stdev. A bar whose cutoff is not yet defined counts as factor 0. REVERSAL
      INTENDED. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combo of a reversal pattern and a volume-elements state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the FVE signed volume share; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427517_combo_reversal123_volatility_fve_reversal"
FAMILY = "combo_reversal"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "perma": [40, 20],
}
DEFAULT_PARAMS = {"length": 14, "perma": 40, "k_smooth": 1, "d_len": 3, "level": 50.0, "samples": 22,
                  "cintra": 0.1, "cinter": 0.1}


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


def _fve(bars_df, n, perma, cintra, cinter):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    hlc3 = (h + lo + c) / 3
    intra = np.log(h) - np.log(lo)
    inter = np.log(hlc3) - np.log(hlc3.shift(1))
    vintra = intra.rolling(n).mean().rolling(n).std(ddof=0)
    vinter = inter.rolling(n).mean().rolling(n).std(ddof=0)
    cut = cintra * vintra + cinter * vinter
    mf = c - (h + lo) / 2 + hlc3 - hlc3.shift(1)
    fac = pd.Series(np.where(mf > cut * c, 1.0, np.where(mf < -cut * c, -1.0, 0.0)), index=c.index)
    xfve = (v * fac).rolling(n).sum() / v.rolling(n).sum() * 100
    ema = xfve.ewm(span=perma, adjust=False).mean()
    raw = np.where(xfve > ema, 1, np.where(xfve < ema, -1, 0))
    out = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    b = _fve(bars_df, int(p["samples"]), int(p["perma"]), float(p["cintra"]), float(p["cinter"]))
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
