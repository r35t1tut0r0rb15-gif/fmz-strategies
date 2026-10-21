"""Ehlers' stochastic cyber cycle turns, traded opposite, 3-minute bars: the smoothed signal turning down goes long, turning up goes short; reversing; a position more than 8 bars old that is losing at the close
is closed.
Port of FMZ strategy #439084 "Ehlers Stochastic Cyber Cycle Strategy" (Ehlers Stochastic Cyber Cycle Strategy).

FMZ source id: 439084

Source
    https://www.fmz.com/strategy/439084 (PineScript v3, FMZ last modified 2024-01-17 16:03:30).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 170-198), source hl2; alpha 0.07; stochastic 8; opposite trade on; pyramiding 1; 100 % of equity, commission 0.1 %
    cycle = Ehlers cyber cycle of hl2 (alpha 0.07);  v1 = stoch(cycle, 8) / 100;  signal = 2 ((4 v1 + 3 v1[1] + 2 v1[2] + v1[3]) / 10 - 0.5)
    opposite on: crossunder(signal, signal[1]) -> entry Long;  crossover(signal, signal[1]) -> entry Short;  open profit < 0 and bars since entry > 8 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * barsSinceEntry counts bars, resets to 0 while flat and on every entry signal (even an ignored
      same-side one). The open profit is read at the close against the fill price. The cycle seeds with
      the second difference until cycle[7] exists, as written. strategy.entry reverses: REVERSAL
      INTENDED. The size and commission are sizing / costs. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested loss exit.
    2 generic: PASS, cyber cycle stochastic turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, pyramiding and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439084 (2 members, best partner #442078, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439084_ehlers_stoch_cyber_cycle_opposite"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "alpha": [0.07, 0.15],
    "len": [8, 16],
}
DEFAULT_PARAMS = {"alpha": 0.07, "len": 8, "opposite": True, "max_bars": 8}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = ((h + lo) / 2).to_numpy(dtype=float)
    m = len(src)
    sm = np.full(m, np.nan)
    for i in range(3, m):
        sm[i] = (src[i] + 2 * src[i - 1] + 2 * src[i - 2] + src[i - 3]) / 6
    a = float(p["alpha"])
    cyc = np.full(m, np.nan)
    for i in range(m):
        if i < 7 or np.isnan(cyc[i - 7]):
            cyc[i] = (src[i] - 2 * src[i - 1] + src[i - 2]) / 4 if i >= 2 else np.nan
        else:
            cyc[i] = ((1 - .5 * a) ** 2 * (sm[i] - 2 * sm[i - 1] + sm[i - 2]) + 2 * (1 - a) * cyc[i - 1]
                      - (1 - a) ** 2 * cyc[i - 2])
    cs = pd.Series(cyc, index=c.index)
    n = int(p["len"])
    lo_, hi_ = cs.rolling(n).min(), cs.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        v1 = (cs - lo_) / (hi_ - lo_)
    v2 = 2 * ((4 * v1 + 3 * v1.shift(1) + 2 * v1.shift(2) + v1.shift(3)) / 10 - 0.5)
    xo = ((v2 > v2.shift(1)) & (v2.shift(1) <= v2.shift(2))).to_numpy()
    xu = ((v2 < v2.shift(1)) & (v2.shift(1) >= v2.shift(2))).to_numpy()
    go_l, go_s = (xu, xo) if p["opposite"] else (xo, xu)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    mb = int(p["max_bars"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, ep, bse = 0, None, np.nan, 0
    for i in range(m):
        if pend is not None:                             # orders of the last bar fill at this open
            pos = pend
            ep = ov[i] if pend != 0 else np.nan
            pend = None
        bse = bse + 1
        if pos == 0:
            bse = 0
        if go_l[i]:
            if pos != 1 and i + 1 < m:
                le[i], pend = True, 1
            bse = 0
        if go_s[i]:
            if pos != -1 and i + 1 < m:
                se[i], pend = True, -1
            bse = 0
        if pos != 0 and (cv[i] - ep) * pos < 0 and bse > mb:
            if pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pend, bse = 0, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
