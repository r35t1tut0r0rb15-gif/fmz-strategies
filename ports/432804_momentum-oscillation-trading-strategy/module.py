"""Bollinger basis crosses from flat with a close-checked target, 1-minute bars: the close crossing above the SMA 20 goes
long, crossing below goes short, each only from flat; a close 0.5 % beyond the fill in the trade's favour closes it (the
95 % stop never binds in practice).
Port of FMZ strategy #432804 "Momentum Oscillation Trading Strategy" (BURATINO).

FMZ source id: 432804

Source
    https://www.fmz.com/strategy/432804 (PineScript v4, FMZ last modified 2023-11-21 16:57:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 113-141), BB 20 x 2 (basis only), target 0.5 %, stop 95 %
    cross(close, basis) and close[1] < basis[1] and flat -> entry long;  cross(basis, close) and close[1] > basis[1] and flat -> entry short
    close >= avg x 1.005 or close <= avg x 0.05 -> close long;  close <= avg x 0.995 or close >= avg x 1.95 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are strategy.close on the close: rule 3, close-based exit signals from simulate()
      (not sl_stop / tp_stop), against the fill price (the open after the entry signal). The bands
      only draw.
    * Entries only from flat (position_size == 0 at the signal bar's close); a close and an entry on
      one bar: the entry needs flat at the bar's start, so it waits. Opposite entries cannot occur.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, basis crosses and percentages of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the close-checked exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432804_basis_cross_close_target"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "target_pct": [0.5, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "target_pct": 0.5, "stop_pct": 95.0}


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
    o, c = bars_df["open"], bars_df["close"]
    b = c.rolling(int(p["length"])).mean()
    el = ((c > b) & (c.shift(1) < b.shift(1))).to_numpy()
    es = ((c < b) & (c.shift(1) > b.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tg, st = float(p["target_pct"]) / 100, float(p["stop_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        start = pos
        if start == 0 and el[i]:
            pos, e_i = 1, i + 1
        elif start == 0 and es[i]:
            pos, e_i = -1, i + 1
        if start == 1 and (cv[i] >= ov[e_i] * (1 + tg) or cv[i] <= ov[e_i] * (1 - st)):
            pos = 0
        if start == -1 and (cv[i] <= ov[e_i] * (1 - tg) or cv[i] >= ov[e_i] * (1 + st)):
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
