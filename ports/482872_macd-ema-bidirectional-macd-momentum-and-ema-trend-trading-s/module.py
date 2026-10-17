"""MACD crosses on the far side of zero in the EMA 200 trend, with a 1 % stop / 2 % target, 1-minute bars: above
EMA 200, MACD crossing above its signal while below zero goes long; below EMA 200, MACD crossing below its signal while
above zero goes short.
Port of FMZ strategy #482872 "双向MACD动量与EMA趋势判定交易策略-Bidirectional-MACD-Momentum-and-EMA-Trend-Trading-Strategy" (Strategy with MACD and EMA).

FMZ source id: 482872

Source
    https://www.fmz.com/strategy/482872 (PineScript v5, FMZ last modified 2025-02-20 15:58:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 114-156), EMA 200, MACD 12 / 26 / 9, TP 2 %, SL 1 %, Long & Short
    long = close > ema200 and crossover(macd, signal) and macd < 0: entry + exit(stop = close x 0.99,
    limit = close x 1.02); short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal close: 1 % / 2 % re-based on the fill (house rule). A later
      same-side signal while held re-places it: mark trailing_stop_pending.
    * The operation type (Long & Short / Long) is a GRID variant. Entries reverse (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, an EMA, MACD and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_482872_macd_zero_side_cross_ema200_bracket"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "operation": ["Long & Short", "Long"],
    "tp_pct": [2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 200, "sl_pct": 1.0, "tp_pct": 2.0, "operation": "Long & Short"}


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
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    long_e = ((c > ema) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0)).astype(bool)
    short_e = ((c < ema) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (macd > 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    if p["operation"] == "Long":
        short_e = false.copy()
    elif p["operation"] == "Short":
        long_e = false.copy()
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
