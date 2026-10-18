"""MACD signal tester with an ATR bracket, 1-hour bars: five MACD signal types (continuation, reversal, histogram and zero-line crossings) open long and short (reversing); each
trade carries a stop of 1.5 ATR and a target of 1 ATR.
Port of FMZ strategy #436213 "MACD金叉死叉趋势跟踪策略MACD-Golden-Cross-Death-Cross-Trend-Following-Strategy" (BV's MACD SIGNAL TESTER).

FMZ source id: 436213

Source
    https://www.fmz.com/strategy/436213 (PineScript v4, FMZ last modified 2023-12-22 11:45:54).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 171-261), MACD 12 / 26 / 9 (EMAs); signal Continuation; SL 1.5 ATR, TP 1 ATR in forex points; years of testing filter
    Continuation: crossover(macd, signal) and macd > 0 (long), crossunder and macd < 0 (short);  Reversal: crossover and macd < 0, crossover(signal, macd) and macd > 0;  Histogram / MACD zero / Signal zero crossings
    entry long / short;  exit(profit = 1 ATR x 100000, loss = 1.5 ATR x 100000)   (points of a 5-digit forex pair)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 100000 factor converts ATR to forex points, so the bracket is 1 ATR target and 1.5
      ATR stop; ported as tp_stop = tp_mult x ATR / close and sl_stop = sl_mult x ATR / close of the signal bar,
      shifted one bar inside stops() (re-based on the fill). The years-of-testing filter is the author's
      window: dropped. The signal type is in the grid. strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, forex-points bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pip adjuster and year inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (10 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436213_macd_signal_types_atr_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "signal": ["Continuation", "Reversal", "Histogram", "MACD Line ZC", "Signal Line ZC"],
    "sl_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"signal": "Continuation", "sl_mult": 1.5, "tp_mult": 1.0, "fast": 12, "slow": 26, "signal_len": 9,
                  "atr_len": 14}


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


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal_len"]), adjust=False).mean()
    hist = macd - sig
    zero = pd.Series(0.0, index=c.index)
    ch = p["signal"]
    if ch == "Continuation":
        lg, sh = _xo(macd, sig) & (macd > 0), _xu(macd, sig) & (macd < 0)
    elif ch == "Reversal":
        lg, sh = _xo(macd, sig) & (macd < 0), _xo(sig, macd) & (macd > 0)
    elif ch == "Histogram":
        lg, sh = _xo(hist, zero), _xu(hist, zero)
    elif ch == "MACD Line ZC":
        lg, sh = _xo(macd, zero), _xu(macd, zero)
    else:
        lg, sh = _xo(sig, zero), _xu(sig, zero)
    false = pd.Series(False, index=bars_df.index)
    return lg.fillna(False).astype(bool), false, sh.fillna(False).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr_frac = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).shift(1)
    return {"sl_stop": atr_frac * float(p["sl_mult"]), "tp_stop": atr_frac * float(p["tp_mult"])}


def portfolio_kwargs(**params):
    return {}
