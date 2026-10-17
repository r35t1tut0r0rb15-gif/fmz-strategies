"""EMA 21 / 55 crosses with the 2-bar extreme as the stop and a 2 R target, 1-hour bars: EMA 21 crossing above EMA 55
goes long (stop the 2-bar low, target close + 2 x (close - stop)); crossing below goes short (mirrored with the high).
Port of FMZ strategy #482849 "自适应均线交叉动态头寸风险管理策略-Adaptive-EMA-Crossover-Dynamic-Position-Risk-Management-Strategy" (EMA Crossover Strategy).

FMZ source id: 482849

Source
    https://www.fmz.com/strategy/482849 (PineScript v5, FMZ last modified 2025-02-27 17:36:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-134), EMA 21 / 55, RR 2, risk 1 %
    long = crossover(ema21, ema55): entry (qty = 1 % risk / (close - stop)) + exit(stop = lowest(low, 2),
    limit = close + 2 (close - stop)); short mirrored with highest(high, 2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: sl = (close - lowest low 2) / close, tp = rr x sl
      ((highest high 2 - close) / close for a short), picked by side, shifted one bar inside stops() and re-based on the
      fill (house rule). A signal whose stop is not beyond the close emits no entry (as #490798). Crosses alternate:
      no re-placement. The risk-based qty is sizing: not ported.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, moving averages and the bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported; the bracket via stops().
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

NAME = "fmz_482849_ema21_55_cross_two_bar_stop_2r"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 3.0],
    "stop_bars": [2, 5],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 55, "rr": 2.0, "stop_bars": 2}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    k = int(p["stop_bars"])
    d_long, d_short = (c - lo.rolling(k).min()) / c, (h.rolling(k).max() - c) / c
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (d_long > 0)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (d_short > 0)).astype(bool)
    return long_e, short_e, d_long, d_short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, d_long, d_short = _signals(bars_df, p)
    sl = d_long.where(long_e, d_short)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
