"""EMA 20 / 50 order, 1-hour bars (the "daily" and "hourly" pairs are both the chart's own): the EMA 20 above the EMA 50 holds long, below holds short; the ATR bracket re-sent while the signal holds is
kept pending; reversing.
Port of FMZ strategy #443092 "Dual Timeframe Trend Following Strategy" (TSLA Enhanced Trend Master 2024).

FMZ source id: 443092

Source
    https://www.fmz.com/strategy/443092 (PineScript v5, FMZ last modified 2024-02-29 10:58:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-154), EMA 20 / 50 on the chart and on 60 minutes; ATR 14 stop 1.5 / target 3; size equity x 2 / close
    buy = ema20 > ema50 and ema20_60 > ema50_60 -> entry Buy (qty), exit(stop = close - 1.5 atr, limit = close + 3 atr)
    sell = both below and shortTradeCount < 0.5 highest(close, 14) -> entry Sell, exit(stop = close + 1.5 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the 1-hour chart the 60-minute request returns the chart's own EMAs, so the two tests are the
      same. The year variable is unused. The short count is compared with half the 14-bar highest close,
      a price: at the BTC reading it never binds, and it is not ported. The bracket is re-sent on every
      bar the (level) signal holds, from that bar's close and ATR: kept pending (mark
      trailing_stop_pending, as #442117); positions end at the opposite signal until then. The
      equity-based quantity is sizing. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, EMA order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND442953 (2 members, best partner #442953, Jaccard 0.799); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_443092_ema20_50_order_reversal_pending_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    false = pd.Series(False, index=c.index)
    return f > s, false, f < s, false.copy()


def portfolio_kwargs(**params):
    return {}
