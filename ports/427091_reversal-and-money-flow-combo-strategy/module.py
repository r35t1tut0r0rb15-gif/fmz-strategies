"""HPotter's combo of the 123 reversal state (stochastic 14 / 1 / 3 at 50) and a volume money-flow state (EMA 3 against EMA 10 of summed (close - open) / range x volume), 4-hour bars: both long goes long, both short goes short, otherwise flat; reversing.
Port of FMZ strategy #427091 "Reversal and Money Flow Combo Strategy" (Combo Backtest 123 Reversal & Money Flow Indicator).

FMZ source id: 427091

Source
    https://www.fmz.com/strategy/427091 (PineScript v4, FMZ last modified 2023-09-17 22:58:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 151-196), Reversal123 14 / 1 / 3, level 50; money flow fast 3, slow 10; reverse off
    posReversal123 as in the combo family;  posMFI = ema(sum(flow, 10), 10) - ema(sum(flow, 3), 3) > 0 ? 1 : < 0 ? -1 : posMFI[1], flow = (high - low) x volume > 0 ? (close - open) / (high - low) x volume : 0
    pos = both 1 -> 1, both -1 -> -1, else 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 state starts at zero and holds until the opposite pattern (as the combo family). The money
      flow state is EMA(sum over 10) minus EMA(sum over 3) of the flow, as written (the slow minus the
      fast), holding its last sign on a zero. REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combo of a reversal pattern and a money-flow state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the money flow (close - open) / range x volume; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427091_combo_reversal123_volume_money_flow_reversal"
FAMILY = "combo_reversal"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "slow": [10, 20],
}
DEFAULT_PARAMS = {"length": 14, "slow": 10, "k_smooth": 1, "d_len": 3, "level": 50.0, "fast": 3}


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


def _money_flow(bars_df, fast, slow):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    lmax, lmin = max(fast, slow), min(fast, slow)
    rng = h - lo
    flow = ((c - o) / rng.where(rng != 0) * v).where(rng * v > 0, 0.0)
    nres = (flow.rolling(lmax).sum().ewm(span=lmax, adjust=False).mean()
            - flow.rolling(lmin).sum().ewm(span=lmin, adjust=False).mean()).to_numpy()
    out = np.zeros(len(nres), dtype=np.int8)
    q = 0
    for i in range(len(nres)):
        if nres[i] > 0:
            q = 1
        elif nres[i] < 0:
            q = -1
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    b = _money_flow(bars_df, int(p["fast"]), int(p["slow"]))
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
