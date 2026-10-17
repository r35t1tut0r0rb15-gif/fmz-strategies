"""Smoothed vortex spread (Guz), 1-hour bars: the EMA 7 smoothed VI+ minus VI- (300 bars) crossing above +0.162 goes long,
below -0.162 goes short; the spread crossing zero closes everything; fixed percentage brackets (long 1.5 % / 2.5 %,
short 1.7 % / 2.5 %).
Port of FMZ strategy #432100 "Quantitative Trading Strategy Based on Improved Vortex Indicator" (%-[Guz] Vortex Indicator Custom).

FMZ source id: 432100

Source
    https://www.fmz.com/strategy/432100 (PineScript v4, FMZ last modified 2023-11-14 14:40:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 174-220), length 300, EMA 7, threshold 16.2 %, long TP 1.5 / SL 2.5, short TP 1.7 / SL 2.5
    VIP = ema(sum(|high - low[1]|, 300) / sum(atr(1), 300), 7); VIM likewise with |low - high[1]|
    crossover(VIP - VIM, 0.162) -> entry long;  crossunder(VIP - VIM, -0.162) -> entry short;  cross(VIP - VIM, 0) -> close_all
    exit long: limit = avg x 1.015, stop = avg x 0.975;  exit short: limit = avg x 0.983, stop = avg x 1.025

Interpretation choices (Pine rules in SURVEY_README.md)
    * The brackets are fixed fractions of the entry price, by side. A close_all written after an
      entry acts on the position held at the bar's start and leaves the bar flat (C31-C39
      convention). "Flat" follows the house bracket on bars. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed percentage brackets.
    2 generic: PASS, a vortex spread and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 10 % position size in the comments only; no sizing code.
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

NAME = "fmz_432100_vortex_spread_threshold"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [300, 100],
    "thresh": [16.2, 8.0],
}
DEFAULT_PARAMS = {"period": 300, "ema_len": 7, "thresh": 16.2, "sl_long": 2.5, "tp_long": 1.5, "sl_short": 2.5,
                  "tp_short": 1.7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["period"])
    vmp = (h - lo.shift(1)).abs().rolling(n).sum()
    vmm = (lo - h.shift(1)).abs().rolling(n).sum()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    st = tr.rolling(n).sum()
    e = int(p["ema_len"])
    d = ((vmp / st).ewm(span=e, adjust=False).mean() - (vmm / st).ewm(span=e, adjust=False).mean())
    t = float(p["thresh"]) / 100
    d1 = d.shift(1)
    el = ((d > t) & (d1 <= t)).to_numpy()
    es = ((d < -t) & (d1 >= -t)).to_numpy()
    cl = (((d > 0) & (d1 <= 0)) | ((d < 0) & (d1 >= 0))).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sll, tpl = float(p["sl_long"]) / 100, float(p["tp_long"]) / 100
    sls, tps = float(p["sl_short"]) / 100, float(p["tp_short"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - sll) or hv[i] >= ep * (1 + tpl)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + sls) or lv[i] <= ep * (1 - tps)):
                pos = 0
        start = pos
        if el[i]:
            pos = 1
        if es[i]:
            pos = -1
        if cl[i]:
            pos = 0
        if pos != start and pos != 0:
            e_i = i + 1
            sl_arr[i], tp_arr[i] = (sll, tpl) if pos == 1 else (sls, tps)
        tgt[i] = pos
    return tgt, sl_arr, tp_arr


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
    tgt, _, _ = _run(bars_df, p)
    return _emit(tgt, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
