"""Strong-bodied closes outside the Bollinger band (20, 2) between 07:30 and 16:00 UTC-5 go long above / short below,
with the stop at the bar's low (high) and a 3 R target, two-hour bars.
Port of FMZ strategy #482434 "动态布林带结合PSAR指标的高级量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-Dynamic-Bollinger-Bands-with-PSAR-Indicator" (Estrategia Bollinger con PSAR y TP Máximo/ Mínimo).

FMZ source id: 482434

Source
    https://www.fmz.com/strategy/482434 (PineScript v6, FMZ last modified 2025-02-18 14:11:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-166), BB 20 / 2, body >= 33 % of the range, window 07:30-16:00 GMT-5
    close > upper and body ratio >= 0.33 and in the window -> entry long with exit(stop = low,
    limit = close + 3 (close - low)); short mirrored below the lower band

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (check 9 / C6): the window is 07:30-16:00 at a FIXED UTC-5 ("GMT-5", no DST) on the bar's opening
      time, i.e. 12:30-21:00 UTC; two-hour bars opening at 14:00, 16:00, 18:00 and 20:00 UTC qualify.
    * The PSAR is only drawn.
    * The bracket is placed with the entry from the signal bar: (close - low) / close and 3 x that (shorts
      mirrored), picked by the signal's side, shifted one bar inside stops() and re-based on the fill (house rule); a
      zero-length stop emits no entry. A later same-side signal while held re-places the bracket: fixed at entry,
      mark trailing_stop_pending (as #491506).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-placed bracket fixed at entry (marked).
    2 generic: PASS, Bollinger bands, candle proportions and the signal bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 07:30-16:00 at fixed UTC-5 (12:30-21:00 UTC, no DST) on the bar's open, as written.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482434_bb_break_strong_body_window_bar_stop_rr3"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_mult": [2.0, 1.5],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "body_min": 0.33, "rr": 3.0}
WIN_START, WIN_END = pd.Timedelta(hours=12, minutes=30), pd.Timedelta(hours=21)   # 07:30-16:00 at UTC-5


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


def _parts(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    ratio = (c - o).abs() / (h - lo)
    tod = bars_df.index - bars_df.index.normalize()
    win = pd.Series((tod >= WIN_START) & (tod <= WIN_END), index=c.index)
    sl_l, sl_s = (c - lo) / c, (h - c) / c
    long_e = (c > basis + dev) & (ratio >= p["body_min"]) & win & (sl_l > 0)
    short_e = (c < basis - dev) & (ratio >= p["body_min"]) & win & (sl_s > 0)
    return long_e.astype(bool), short_e.astype(bool), sl_l.where(long_e, sl_s)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _parts(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
