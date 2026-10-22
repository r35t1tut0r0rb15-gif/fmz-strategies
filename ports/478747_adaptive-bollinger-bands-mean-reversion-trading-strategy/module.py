"""Bollinger 20 / 2 re-entries, 10-minute bars: the close crossing back over the lower band goes long, back under the upper band goes short, each with a 1 % stop and 2 % target from the signal close; the close crossing the basis against the position closes it; reversing.
Port of FMZ strategy #478747 "Adaptive Bollinger Bands Mean Reversion Trading Strategy" (Bollinger Bands Strategy).

FMZ source id: 478747

Source
    https://www.fmz.com/strategy/478747 (PineScript v5, FMZ last modified 2025-01-17 16:37:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-183), BB 20 / 2; stop 1 %, target 2 %; 200 % of equity
    crossover(close, lower) -> entry Long + exit(stop = close x 0.99, limit = close x 1.02);  crossunder(close, upper) -> entry Short + exit(mirror);  crossunder(close, basis) and long -> close Long;  crossover(close, basis) and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close: the opening signal's levels are ported, sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256); a second re-entry inside a trade re-sends it, which is not followed (as #434428, mark
      trailing_stop_pending). A close acts only on the held position and leaves a same-bar reversal
      standing (as #441963). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 200 % of
      equity size is sizing. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, Bollinger re-entries with basis closes and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478747_bb20_reentry_basis_close_pct_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_length": [20, 50],
    "tp_pct": [0.02, 0.01],
}
DEFAULT_PARAMS = {"bb_length": 20, "tp_pct": 0.02, "sl_pct": 0.01, "bb_std": 2.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    le = (c > dn) & (c.shift(1) <= dn.shift(1))
    se = (c < up) & (c.shift(1) >= up.shift(1))
    xl = (c < basis) & (c.shift(1) >= basis.shift(1))
    xs = (c > basis) & (c.shift(1) <= basis.shift(1))
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, xl, xs, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, xl, xs, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = ((lf & l_thr) | xl) & ~se & ~le
    sx = ((sf & s_thr) | xs) & ~le & ~se
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, xl, xs, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
