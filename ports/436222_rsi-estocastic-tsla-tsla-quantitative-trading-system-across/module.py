"""Oversold RSI buys with a stochastic exit, 1-hour bars, long only: the RSI 5 and the RSI 14 (of the chart's own close, sampled from the 1-minute series) both under 30 buy; a 14-bar stochastic over 78
closes. The 3 % "stop" compares the 10-bar high with 3 % of the average price and never fires.
Port of FMZ strategy #436222 "基于RSI和Estocastic指标的TSLA交易策略TSLA-Quantitative-Trading-System-Across-Multiple-Timeframes" (Estrategia de Trading TSLA).

FMZ source id: 436222

Source
    https://www.fmz.com/strategy/436222 (PineScript v5, FMZ last modified 2023-12-22 12:50:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 116-140), RSI 5 and RSI 14; stochastic 14 at 78; stop = average price x 0.03
    condicion_entrada = rsi(close, 5) < 30 and rsi(security(tickerid, "1", close), 14) < 30 -> entry long (qty 2);  exit: stoch(14) > 78 or highest(high, 10) <= avg price x 0.03 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security call is the same instrument at the 1-minute resolution: on a 1-hour bar it returns the last
      minute's close, which is the chart's close, so the second RSI is the RSI 14 of the chart's close (the
      comments name a US100 chart but the symbol is the same). The "stop" tests a price against 3 % of the
      average price (a price level far under the market), so it is never true and is not ported (the
      intended 3 % stop is owed). Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436222_rsi_pair_oversold_long_stoch_exit"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_fast": [5, 3],
    "stoch_exit": [78, 70],
}
DEFAULT_PARAMS = {"rsi_fast": 5, "rsi_slow": 14, "stoch_exit": 78, "stoch_len": 14}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stoch_len"])
    with np.errstate(invalid="ignore", divide="ignore"):
        stoch = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    le = ((_rsi(c, int(p["rsi_fast"])) < 30) & (_rsi(c, int(p["rsi_slow"])) < 30)).fillna(False)
    lx = (stoch > float(p["stoch_exit"])).fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return (le & ~lx).astype(bool), lx.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
