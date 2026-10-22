"""Bollinger 20 / 2 breakouts by full-bodied candles in a 07:30-16:00 GMT-5 window, 2-hour bars: a close above the upper band with a body of at least a third of the range goes long with a stop at the candle's low and a 3 R target; the mirror below the lower band goes short; reversing.
Port of FMZ strategy #482434 "动态布林带结合PSAR指标的高级量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-Dynamic-Bollinger-Bands-with-PSAR-Indicator" (Estrategia Bollinger con PSAR y TP Máximo/ Mínimo).

FMZ source id: 482434

Source
    https://www.fmz.com/strategy/482434 (PineScript v6, FMZ last modified 2025-02-18 14:11:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-180), BB 20 / 2; body >= 1/3 of the range; window 07:30-16:00 GMT-5; stop at the candle's low / high, R:R 1:3; PSAR plotted only
    close > upper and body / range >= 0.33 and in window -> entry Compra + exit(stop = low, limit = close + 3 (close - low));  close < lower and body ratio and in window -> entry Venta + exit(stop = high, limit = close - 3 (high - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The window is fixed at GMT-5 (no DST): bars opening from 12:30 to 21:00 UTC, the bar's own date.
      The bracket is sent on each signal bar from its low / high and close: the opening signal's levels
      are ported, sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256); a repeat breakout inside a trade re-sends it, which is not followed (as
      #434428, mark trailing_stop_pending). The PSAR is plotted only. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing
      code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar candle bracket as fractions of the fill.
    2 generic: PASS, Bollinger breakouts by full-bodied candles in a time window.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 07:30-16:00 GMT-5 (fixed offset, no DST) by bar open time.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482434_bb20_breakout_body_third_window_3r_bracket_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_length": [20, 50],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"bb_length": 20, "rr": 3.0, "bb_std": 2.0, "start_min": 750, "end_min": 1260}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    body = (c - o).abs()
    ratio = body / (h - lo).where(h > lo)
    t = c.index.tz_convert("UTC")
    mins = pd.Series(t.hour * 60 + t.minute, index=c.index)
    win = (mins >= int(p["start_min"])) & (mins <= int(p["end_min"]))      # 07:30-16:00 GMT-5 in UTC minutes
    le = (c > basis + dev) & (ratio >= 0.33) & win
    se = (c < basis - dev) & (ratio >= 0.33) & win
    rr = float(p["rr"])
    lvl = {"l_sl": lo, "l_tp": c + rr * (c - lo), "s_sl": h, "s_tp": c - rr * (h - c)}
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
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
