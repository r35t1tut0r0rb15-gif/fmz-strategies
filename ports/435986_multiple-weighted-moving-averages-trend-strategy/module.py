"""Five weighted averages in order, 30-minute bars: WMA 29 > WMA 5 > WMA 3 > WMA 2 > WMA 1 (the close) goes long; the reverse order goes short
(reversing). The stop and target inputs are zero (off).
Port of FMZ strategy #435986 "Multiple Weighted Moving Averages Trend Strategy" (EURCHF Scalp 3 minutes).

FMZ source id: 435986

Source
    https://www.fmz.com/strategy/435986 (PineScript v5, FMZ last modified 2023-12-20 15:59:56).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 92-133), WMA 29 / 5 / 3 / 2 / 1; stop and target 0
    wma_signal = wma29 > wma5 and wma5 > wma3 and wma3 > wma2 and wma2 > wma1;  wma_sell_signal = the reverse order;  entry long / short;  exit only if stop_loss > 0 or take_profit > 0 (both 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * WMA 1 is the close. The conditions are states re-sent every bar; vbt ignores a same-side signal.
      The stop and target are zero, so the exit branches never run. strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "30min" from the backtest header (the title says 3 minutes).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weighted average order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop and risk inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435986 (2 members, best partner #436529, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435986_wma_order_stack"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [29, 20],
    "len2": [5, 8],
}
DEFAULT_PARAMS = {"len1": 29, "len2": 5, "len3": 3, "len4": 2}


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


def _wma(s, n):
    n = int(n)
    if n == 1:
        return s
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    w1, w2, w3, w4 = (_wma(c, p[k]) for k in ("len1", "len2", "len3", "len4"))
    w5 = c
    le = ((w1 > w2) & (w2 > w3) & (w3 > w4) & (w4 > w5)).fillna(False).astype(bool)
    se = ((w1 < w2) & (w2 < w3) & (w3 < w4) & (w4 < w5)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
