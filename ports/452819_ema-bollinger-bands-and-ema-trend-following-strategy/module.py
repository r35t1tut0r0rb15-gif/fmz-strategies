"""EMA 9 crossings beyond the Bollinger bands, 1-hour bars: the close crossing over the EMA 9 while over the upper band (20 / 2) goes long, crossing under it while under the lower band goes short; each with a 0.5 % stop and a 1 % target from the signal close; reversing.
Port of FMZ strategy #452819 "波林格带和EMA趋势跟踪策略-Bollinger-Bands-and-EMA-Trend-Following-Strategy" (Bollinger Bands and EMA Strategy).

FMZ source id: 452819

Source
    https://www.fmz.com/strategy/452819 (PineScript v5, FMZ last modified 2024-05-29 16:49:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-161), Bollinger 20 / 2; EMA 9; stop 0.5 %, target 1 % of the signal close; risk 1 % sizing
    crossover(close, ema9) and close > upper -> entry Long, exit(Take Profit, limit = close x 1.01), exit(Stop Loss, stop = close x 0.995);  the mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed on the signal bar from its close: ported as the fixed fractions 0.005 /
      0.01 of the fill (as #437751). A repeat signal inside the trade re-issues them from that bar's
      close, which stops() cannot express: the port keeps the opening levels and marks
      trailing_stop_pending (as #434428). The exit ids are shared by both sides, so an opposite entry's
      call replaces them. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The risk
      quantity is sizing (stored). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-close bracket as fixed fractions; re-issued levels pending (mark).
    2 generic: PASS, EMA crossings beyond the bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452819_ema9_cross_beyond_bollinger_bracket_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [9, 21],
    "sl_pct": [0.005, 0.01],
    "tp_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"ema_len": 9, "sl_pct": 0.005, "tp_pct": 0.01, "bb_len": 20, "bb_mult": 2.0}


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
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    c1, e1 = c.shift(1), ema.shift(1)
    le = (c > ema) & (c1 <= e1) & (c > basis + dev)
    se = (c < ema) & (c1 >= e1) & (c < basis - dev)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
