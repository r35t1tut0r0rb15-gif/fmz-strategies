"""HPotter combo, 15-minute bars: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the Percentage Volume Oscillator state (+1 when the PVO 12 / 26 is under its EMA 9 signal, -1 when above) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #438823 "Dual Confirmation Quant Trading Strategy" (Combo Backtest 123 Reversal & Percentage Volume Oscillator (PVO) (HPotter)).

FMZ source id: 438823

Source
    https://www.fmz.com/strategy/438823 (PineScript v4, FMZ last modified 2024-01-15 15:21:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-178), 123 reversal: length 14, K smoothing 1, D length 3, level 50; PVO 12 / 26 / 9; reverse off
    xPVO = (ema(volume, 12) - ema(volume, 26)) / ema(volume, 26) * 100;  posPVO = signal < xPVO ? -1 : signal > xPVO ? 1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The PVO state is +1 when the PVO is BELOW its signal line and -1 above, as written (the
      description says a rising PVO confirms; weird case). reverse is off. REVERSAL INTENDED. No sizing
      code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and volume-oscillator states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Percentage Volume Oscillator; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438823_reversal123_percentage_volume_oscillator_combo_15m_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "pvo_signal": [9, 5],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "pvo_short": 12, "pvo_long": 26,
                  "pvo_signal": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    r123 = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    es = v.ewm(span=int(p["pvo_short"]), adjust=False).mean()
    el = v.ewm(span=int(p["pvo_long"]), adjust=False).mean()
    pvo = (es - el) / el.where(el != 0) * 100
    sig = pvo.ewm(span=int(p["pvo_signal"]), adjust=False).mean()
    raw = np.where(sig < pvo, -1, np.where(sig > pvo, 1, 0))
    m = len(raw)
    pv = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pv[i] = q
    s = np.where((r123 == 1) & (pv == 1), 1, np.where((r123 == -1) & (pv == -1), -1, 0))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if s[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif s[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif s[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif s[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
