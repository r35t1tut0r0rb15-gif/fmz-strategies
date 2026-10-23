"""The volume flow indicator (130 bars, capped and direction-signed volume) against an EMA 5 signal +/- one 20-bar sd, 3-hour bars: the VFI crossing under the lower band closes a short, or goes long when flat; crossing over the upper band closes a long, or goes short when flat.
Port of FMZ strategy #430594 "VB Strategy Based on Volume Balances" (VB Strategy).

FMZ source id: 430594

Source
    https://www.fmz.com/strategy/430594 (PineScript v3, FMZ last modified 2023-10-30 17:03:02).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 209-264), VFI 130, coef 0.2, max 2.5; signal EMA 5; band sd 20; smoothing off
    buysignal = crossunder(vfi, vfima - stdev(vfi, 20)):  short -> close SHORT;  long -> strategy.order LONG +1;  flat -> entry LONG
    sellsignal = crossover(vfi, vfima + stdev(vfi, 20)):  long -> close LONG;  short -> strategy.order SHORT +1;  flat -> entry SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * A signal against the open position only closes it (the entry branch needs a flat position at the
      same bar's close), so the next opposite signal opens the new side. The strategy.order adds while in
      a position are sizing: the port holds one position. Crossing UNDER the lower band buys and crossing
      OVER the upper band sells, as written. The when = (low + high) / 2 arguments are always true. No
      sizing code beyond the 1-unit adds. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume flow indicator band extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1-unit strategy.order adds stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VFI (capped signed volume over its 130-bar average); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430594_vfi130_band_extreme_flat_entries"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [130, 50],
    "signal_length": [5, 10],
}
DEFAULT_PARAMS = {"length": 130, "signal_length": 5, "coef": 0.2, "vcoef": 2.5, "length2": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    typ = (h + lo + c) / 3
    inter = np.log(typ) - np.log(typ.shift(1))
    cut = float(p["coef"]) * inter.rolling(30).std(ddof=0) * c
    vave = v.rolling(n).mean().shift(1)
    vc = v.where(v < vave * float(p["vcoef"]), vave * float(p["vcoef"]))
    mf = typ - typ.shift(1)
    vcp = pd.Series(np.where(mf > cut, vc, np.where(mf < -cut, -vc, 0.0)), index=c.index)
    vfi = vcp.rolling(n).sum() / vave
    vfima = vfi.ewm(span=int(p["signal_length"]), adjust=False).mean()
    sd = vfi.rolling(int(p["length2"])).std(ddof=0)
    lower, upper = vfima - sd, vfima + sd
    buy = ((vfi < lower) & (vfi.shift(1) >= lower.shift(1))).to_numpy()
    sell = ((vfi > upper) & (vfi.shift(1) <= upper.shift(1))).to_numpy()
    m = len(buy)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if buy[i]:
            if pos == -1:
                sx[i], pos = True, 0
            elif pos == 0 and i + 1 < m:
                le[i], pos = True, 1
        elif sell[i]:
            if pos == 1:
                lx[i], pos = True, 0
            elif pos == 0 and i + 1 < m:
                se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
