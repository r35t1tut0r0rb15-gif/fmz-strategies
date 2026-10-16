"""CCI turns with an EMA filter, 1-hour bars: CCI 14 of hlc3 crossing up through -140 above the EMA 55 goes long, crossing
down through 150 below the EMA goes short; CCI crossing up through 150 closes the long, down through -140 closes the
short; 10 % target and 10 % stop from the entry.
Port of FMZ strategy #430170 "动量追踪CCI策略Momentum-Tracking-CCI-Strategy" (CCI+EMA Strategy with Percentage or ATR TP/SL [Alifer]).

FMZ source id: 430170

Source
    https://www.fmz.com/strategy/430170 (PineScript v5, FMZ last modified 2023-10-25 17:37:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 235-300), CCI 14 (hlc3), levels 150 / -140, EMA 55 of hlc3, percentage TP / SL 10 % / 10 %
    crossover(cci, -140) and close > ema55 -> entry long; crossunder(cci, 150) and close < ema55 -> entry short
    long: exit(limit = avg x 1.10, stop = avg x 0.90); short: exit(limit = avg x 0.90, stop = avg x 1.10)
    crossover(cci, 150) -> close long;  crossunder(cci, -140) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Default method: percentage TP / SL from the average entry price: tp_stop 0.10, sl_stop 0.10 of
      the fill. The ATR method is an off-by-default option (not ported).
    * A bar that both enters and closes the same side (CCI jumping from under -140 to over 150) keeps
      the entry (stated approximation; the source would end flat when already long).
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed percentage bracket.
    2 generic: PASS, CCI levels, an EMA and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 10 % of equity stored in original_sizing.txt.
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

NAME = "fmz_430170_cci_turn_ema_pct_bracket"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 20],
    "tp_sl_pct": [10.0, 5.0],
}
DEFAULT_PARAMS = {"length": 14, "overbought": 150, "oversold": -140, "ema_len": 55, "tp_sl_pct": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (src - ma) / (0.015 * dev.replace(0.0, np.nan))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    src = (bars_df["high"] + bars_df["low"] + c) / 3
    cci = _cci(src, int(p["length"]))
    ema = src.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    xo_os = (cci > os_) & (cci.shift(1) <= os_)
    xu_ob = (cci < ob) & (cci.shift(1) >= ob)
    xo_ob = (cci > ob) & (cci.shift(1) <= ob)
    xu_os = (cci < os_) & (cci.shift(1) >= os_)
    long_e = (xo_os & (c > ema)).astype(bool)
    short_e = (xu_ob & (c < ema)).astype(bool)
    long_x = (xo_ob & ~long_e).astype(bool)
    short_x = (xu_os & ~short_e).astype(bool)
    return long_e, long_x, short_e, short_x


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["tp_sl_pct"]) / 100
    return {"sl_stop": f, "tp_stop": f}


def portfolio_kwargs(**params):
    return {}
