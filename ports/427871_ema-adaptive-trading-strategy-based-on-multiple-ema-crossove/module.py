"""Separate EMA pairs per side, 12-hour bars: EMA 11 crossing above EMA 33 above the EMA 144 trend goes
long (closed when EMA 3 crosses under EMA 40, stop 1.7 %); EMA 5 crossing under EMA 11 below the EMA 89
trend goes short (closed when EMA 4 crosses above EMA 7, stop 0.4 %).
Port of FMZ strategy #427871 "Adaptive Trading Strategy Based on Multiple EMA Crossovers" (str1nger).

FMZ source id: 427871

Source
    https://www.fmz.com/strategy/427871 (PineScript v4, FMZ last modified 2023-09-26 14:41:00).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 114-211)
    openlong = crossover(ema11, ema33) and close > ema144; closelong = crossover(ema40, ema3)
    openshort = crossover(ema11, ema5) and close < ema89; closeshort = crossover(ema4, ema7)
    exit(stop = avg price x (1 - 1.7 %)) while long; (1 + 0.4 %) while short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (one position).
    * The two stops differ by side: sl_stop is a per-bar series set from the signal bar (1.7 % after
      a long signal, 0.4 % after a short one), shifted one bar onto the fill.
    * A close on the bar of the opposite entry is dropped (the entry reverses). A long close on the
      bar of a new long signal while long: Pine ends flat, the port stays long (rare; stated).
    * The date range is dropped (inDateRange is true).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * Stops on 12-hour bars: mark coarse_bar_stop. FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stops fixed at entry.
    2 generic: PASS, EMA lengths and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() sizing stored; the stops quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427871_side_ema_pairs_pct_stops"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lttl": [144, 89],
    "long_sl": [1.7, 3.4],
    "short_sl": [0.4, 1.0],
}
DEFAULT_PARAMS = {"lof": 11, "los": 33, "lcf": 3, "lcs": 40, "sof": 5, "sos": 11, "scf": 4, "scs": 7,
                  "lttl": 144, "ltts": 89, "long_sl": 1.7, "short_sl": 0.4}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))
    ol = xo(e(p["lof"]), e(p["los"])) & (c > e(p["lttl"]))
    cl = xo(e(p["lcs"]), e(p["lcf"]))
    os_ = xo(e(p["sos"]), e(p["sof"])) & (c < e(p["ltts"]))
    cs = xo(e(p["scf"]), e(p["scs"]))
    return ol, cl, os_, cs


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ol, cl, os_, cs = _signals(bars_df, p)
    le = ol.astype(bool)
    se = (os_ & ~ol).astype(bool)
    lx = (cl & ~le & ~se).astype(bool)
    sx = (cs & ~le & ~se).astype(bool)
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ol, _, os_, _ = _signals(bars_df, p)
    lsl, ssl = float(p["long_sl"]) / 100, float(p["short_sl"]) / 100
    sl = pd.Series(np.where(ol, lsl, np.where(os_, ssl, lsl)), index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
