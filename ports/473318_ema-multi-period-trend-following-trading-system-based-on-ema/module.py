"""EMA 300 bands of 2 standard deviations (300 bars), 2-hour bars: a close crossing back over the lower band goes long, under the upper band goes short; reversing. The 0.98 % limit re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #473318 "基于EMA均线波动带的多周期趋势跟踪交易系统-Multi-Period-Trend-Following-Trading-System-Based-on-EMA-Volatility-Bands" (Estrategia de Compra/Venta en Bandas de EMA 300).

FMZ source id: 473318

Source
    https://www.fmz.com/strategy/473318 (PineScript v5, FMZ last modified 2024-11-29 10:49:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-170), EMA 300, stdev 300, 2 sd; exit limit close x (1 +/- 0.98 %) re-sent every bar
    crossover(close, lower) -> entry Compra;  crossunder(close, upper) -> entry Venta;  while long: exit(limit = close x 1.0098);  while short: exit(limit = close x 0.9902)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The limits are re-sent on every bar from that bar's close, so the level moves after entry:
      stops() cannot express a level re-set every bar, so it is kept pending (as #438034, mark
      trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL INTENDED. No
      sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA band re-entries; per-bar limit described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent limit stored.
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

NAME = "fmz_473318_ema300_2sd_band_reentry_reversal_limit_pending"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [300, 150],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 300, "mult": 2.0}


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
    n = int(p["length"])
    e = c.ewm(span=n, adjust=False).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = e + dev, e - dev
    le = (c > dn) & (c.shift(1) <= dn.shift(1))
    se = (c < up) & (c.shift(1) >= up.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
