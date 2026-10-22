"""Double crossings, 1-hour bars, with percent brackets: the close crossing over the SMA 5 while the SMA 5 crosses over the SMA 20 goes long (stop 2 %, target 4 %), the mirror goes short (stop 2 %, target
7 %); the opposite signal closes and reverses.
Port of FMZ strategy #446526 "Dynamic Trend Following Strategy" (Big Runner (Sprinter)).

FMZ source id: 446526

Source
    https://www.fmz.com/strategy/446526 (PineScript v5, FMZ last modified 2024-03-29 11:38:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-274), SMA 5 / 20; ribbon SMA 20 (colour only); long TP 4 % / SL 2 %, short TP 7 % / SL 2 %; 10 % of the portfolio x leverage 1
    crossover(close, sma5) and crossover(sma5, sma20) -> entry Buy, exit(limit = close x 1.04), exit(stop = close x 0.98);  short mirrored with 7 % / 2 %
    sellSignal -> close Buy;  buySignal -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The brackets are fixed percentages of the signal close, so they are ported as fractions of the
      fill: sl_stop 0.02, tp_stop 0.04 for longs and 0.07 for shorts (as #437751). A repeated signal
      inside the trade re-issues the levels from that bar's close: not expressible (mark
      trailing_stop_pending); the opening levels are kept. Each close follows the opposite entry on the
      same bar and leaves the reversal. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      The portfolio share and leverage are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; brackets fixed at entry (re-sent levels marked).
    2 generic: PASS, double SMA crossings with percent brackets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the portfolio share and leverage stored.
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

NAME = "fmz_446526_close_sma5_sma20_double_cross_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow": [20, 50],
    "sl": [0.02, 0.01],
}
DEFAULT_PARAMS = {"slow": 20, "sl": 0.02, "fast": 5, "tp_long": 0.04, "tp_short": 0.07}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    c1, f1, s1 = c.shift(1), f.shift(1), s.shift(1)
    le = (c > f) & (c1 <= f1) & (f > s) & (f1 <= s1)
    se = (c < f) & (c1 >= f1) & (f < s) & (f1 >= s1)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    tp = pd.Series(float(p["tp_long"]), index=ix).where(le, pd.Series(float(p["tp_short"]), index=ix).where(se))
    return {"sl_stop": float(p["sl"]), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
