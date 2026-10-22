"""WaveTrend [LazyBear] level re-crossings, 3-hour bars: WT1 crossing back over -60 or -53 goes long, under 60 or 53 goes short; reversing. Each trade has a 50 % stop, a 5 % target and a trail of 2 % of the close in ticks (0.2 %) armed at +3 %.
Port of FMZ strategy #474965 "Multi Wave Trend Crossing Risk Management Quantitative Strategy" (WT_LB_RM).

FMZ source id: 474965

Source
    https://www.fmz.com/strategy/474965 (PineScript v5, FMZ last modified 2024-12-13 10:51:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-157), channel 10, average 21; levels 60 / 53 / -60 / -53; stop 50 %, target 5 %, trail activation 3 %, trail offset close x 2 % (ticks)
    crossover(wt1, -60) or crossover(wt1, -53) -> entry Long, exit(stop = close x 0.5, limit = close x 1.05, trail_price = close x 1.03, trail_offset = close x 0.02);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset is in ticks: close x 0.02 ticks at the 0.1 tick is close x 0.002 in price, a 0.2 %
      trail, read as the house percent trail behind the best price (anchor high_low), armed after a 3 %
      gain from the fill (the source arms it at 3 % over the signal close; stated approximation), mark
      trailing_stop. The stop and target come from the signal close, sent as fractions of the fill open
      (a level at or through it is marketable and closed one bar late, as #458256). A repeat signal
      inside a trade re-sends the exit and is not followed (mark trailing_stop_pending). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket and a house percent trail.
    2 generic: PASS, WaveTrend level re-crossings with a bracket and trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474965_wavetrend_level_recross_bracket_pct_trail_reversal"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.002, 0.01],
    "activate": [0.03, 0.01],
}
DEFAULT_PARAMS = {"trail_pct": 0.002, "activate": 0.03, "sl_pct": 0.5, "tp_pct": 0.05, "n1": 10, "n2": 21}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    n1, n2 = int(p["n1"]), int(p["n2"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=n2, adjust=False).mean()

    def xo(lv):
        return (wt1 > lv) & (wt1.shift(1) <= lv)

    def xu(lv):
        return (wt1 < lv) & (wt1.shift(1) >= lv)

    le = xo(-60) | xo(-53)
    se = xu(60) | xu(53)
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    trail = {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
             "activate_after": float(p["activate"])}
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0), "trail": trail}


def portfolio_kwargs(**params):
    return {}
