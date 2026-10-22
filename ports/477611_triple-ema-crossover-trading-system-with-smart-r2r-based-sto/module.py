"""EMA 8 / 21 crossings on the EMA 89 side with a candle of the same colour, 4-hour bars: the cross up goes long, the cross down goes short, each with a 0.1 % stop and 0.25 % target from the signal close; reversing. The long's move of the stop to break-even is not ported (pending).
Port of FMZ strategy #477611 "Triple EMA Crossover Trading System with Smart R2R based Stop Loss Management" (EMA Crossover with SL to BE).

FMZ source id: 477611

Source
    https://www.fmz.com/strategy/477611 (PineScript v5, FMZ last modified 2025-01-06 16:53:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-152), EMA 8 / 21 / 89; stop 0.1 %, target 0.25 % of the close; R2R 1.0 for the break-even trigger
    crossover(ema8, ema21) and close > ema89 and close > open -> entry BUY + exit(stop = close x 0.999, limit = close x 1.0025);  crossunder and close < ema89 and close < open -> entry SELL + exit(mirror)
    long and high >= avg x 1.001 -> exit("SL to BE", BUY, stop = avg);  the short's break-even sits inside the long-only block and never fires

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close: sent as fractions of the fill open
      (a level at or through it is marketable and closed one bar late, as #458256); the crossings
      alternate, so no repeat signal re-sends it. The break-even stop is a second exit armed by a
      bar-close test of the high and sent from the next bar; it is not followed (as #475627, mark
      trailing_stop_pending). The short's break-even never fires, as written. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill; break-even described (pending).
    2 generic: PASS, EMA crossings on the EMA 89 side with a tight bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop / target fractions stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477611_ema8_21_cross_ema89_side_tight_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.001, 0.005],
    "tp_pct": [0.0025, 0.01],
}
DEFAULT_PARAMS = {"sl_pct": 0.001, "tp_pct": 0.0025}


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
    o, c = bars_df["open"], bars_df["close"]
    e8, e21, e89 = (c.ewm(span=n, adjust=False).mean() for n in (8, 21, 89))
    le = (e8 > e21) & (e8.shift(1) <= e21.shift(1)) & (c > e89) & (c > o)
    se = (e8 < e21) & (e8.shift(1) >= e21.shift(1)) & (c < e89) & (c < o)
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
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
