"""HPotter combo, hourly bars: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the Klinger volume oscillator state (EMA 34 / 55 of signed volume against its EMA 13 trigger) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #432845 "Quant Trading Double Click Reversal Strategy" (Combo Backtest 123 Reversal & Klinger Volume Oscillator).

FMZ source id: 432845

Source
    https://www.fmz.com/strategy/432845 (PineScript v4, FMZ last modified 2023-11-22 10:03:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 141-181), 123 reversal: length 14, K smoothing 1, D length 3, level 50; KVO: trigger 13, fast 34, slow 55; reverse off
    posReversal123 as HPotter;  xTrend = hlc3 > hlc3[1] ? volume x 100 : -volume x 100;  xKVO = ema(xTrend, 34) - ema(xTrend, 55);  posKVO = xKVO > ema(xKVO, 13) ? 1 : xKVO < trigger ? -1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Klinger oscillator compares two EMAs of signed volume with their own EMA, so only the volume's
      shape matters, not its units. The x 100 factor cancels. reverse is off. REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and volume-oscillator states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Klinger volume oscillator (signed volume EMAs 34 / 55, trigger 13); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432845_reversal123_klinger_volume_oscillator_combo_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_x": [34, 20],
    "slow_x": [55, 89],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "trig_len": 13, "fast_x": 34, "slow_x": 55}


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
    hlc3 = (h + lo + c) / 3
    xt = pd.Series(np.where(hlc3 > hlc3.shift(1), v * 100, -v * 100), index=c.index)
    kvo = xt.ewm(span=int(p["fast_x"]), adjust=False).mean() - xt.ewm(span=int(p["slow_x"]), adjust=False).mean()
    trig = kvo.ewm(span=int(p["trig_len"]), adjust=False).mean()
    raw = np.where(kvo > trig, 1, np.where(kvo < trig, -1, 0))
    pk = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pk[i] = q
    sig = np.where((r123 == 1) & (pk == 1), 1, np.where((r123 == -1) & (pk == -1), -1, 0))
    m = len(sig)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if sig[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif sig[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif sig[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif sig[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
