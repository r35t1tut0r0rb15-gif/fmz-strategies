"""EMA 12 / 26 crosses confirmed by the MACD side, closed when the MACD side turns, with a 2 % stop / 5 % target,
1-hour bars: EMA 12 crossing above EMA 26 with MACD above its signal goes long; the mirror goes short; a long closes on
the opposite EMA cross or MACD below its signal (a short mirrored).
Port of FMZ strategy #483121 "动态趋势动量交叉策略-基于双重EMA与MACD指标的量化交易系统-Dynamic-Trend-Momentum-Crossover-Strategy-Quantitative-Trading-System-Based-on-Dual-EMA-and-MACD-Indicators" (EMA + MACD Strategy).

FMZ source id: 483121

Source
    https://www.fmz.com/strategy/483121 (PineScript v5, FMZ last modified 2025-02-27 16:56:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 89-136), EMA 12 / 26, MACD 12 / 26 / 9, SL 2 %, TP 5 %
    long = crossover(ema12, ema26) and macd > signal; entry + exit(stop = close x 0.98, limit = close x 1.05)
    short mirrored; exitLong = crossunder(ema12, ema26) or macd < signal -> close long (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar's close: 2 % / 5 % fractions re-based on the fill (house
      rule). A same-side signal while held re-places it: mark trailing_stop_pending; the port keeps the entry's bracket.
    * A short signal while long also meets exitLong: close + entry is a reversal, so only the entry is emitted (never an
      exit plus the opposite entry on one bar); the long side mirrored.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, MACD and percentage distances.
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

NAME = "fmz_483121_ema12_26_macd_side_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [2.0, 3.0],
    "tp_pct": [5.0, 8.0],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                  "sl_pct": 2.0, "tp_pct": 5.0}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = (c.ewm(span=int(p["macd_fast"]), adjust=False).mean()
            - c.ewm(span=int(p["macd_slow"]), adjust=False).mean())
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    x_up = (f > s) & (f.shift(1) <= s.shift(1))
    x_dn = (f < s) & (f.shift(1) >= s.shift(1))
    long_e = (x_up & (macd > sig)).astype(bool)
    short_e = (x_dn & (macd < sig)).astype(bool)
    long_x = ((x_dn | (macd < sig)) & ~short_e).astype(bool)
    short_x = ((x_up | (macd > sig)) & ~long_e).astype(bool)
    return long_e, long_x, short_e, short_x


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
