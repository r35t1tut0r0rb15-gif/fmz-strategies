"""RSI 14 extremes with wide percent brackets, 2-hour bars: an RSI under 30 goes long, over 70 goes short (reversing); each trade carries a 50 % stop and a 50 % target of the price
(the closes by the opposite signal sit inside the entry blocks and never fire).
Port of FMZ strategy #436237 "基于相对强弱指数RSI指标的量化交易策略The-RSI-breakout-strategy-is-a-quantitative-trading-strategy" (My New Strategy (RSI breakout)).

FMZ source id: 436237

Source
    https://www.fmz.com/strategy/436237 (PineScript v4, FMZ last modified 2023-12-22 14:06:45).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 140-194), RSI 14 at 30 / 70; stop 50 %, target 50 %, in ticks of the close
    buy_signal = rsi < 30;  sell_signal = rsi > 70;  if buy_signal: entry long, exit(loss = close 50 % ticks, profit = close 50 % ticks), close long when sell_signal;  if sell_signal: entry short, exit(...), close short when buy_signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The explicit closes are called inside the block that requires the opposite signal to be false,
      so they never fire; the position changes by the opposite entry (reversal) or by its bracket. The
      loss / profit amounts are percents of the price turned into ticks and back: distances of 50 % of the signal close,
      ported as fractions of the fill price (sl_stop = tp_stop = pct: 0.5 as written, 0.1 as an alternative).
      A signal bar after a bracket exit enters again (the signal is a state). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, percent amounts in ticks -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436237_rsi_extremes_wide_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pct": [0.5, 0.1],
    "length": [14, 7],
}
DEFAULT_PARAMS = {"pct": 0.5, "length": 14}


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
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    false = pd.Series(False, index=bars_df.index)
    return (rsi < 30).fillna(False).astype(bool), false, (rsi > 70).fillna(False).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["pct"]), "tp_stop": float(p["pct"])}


def portfolio_kwargs(**params):
    return {}
