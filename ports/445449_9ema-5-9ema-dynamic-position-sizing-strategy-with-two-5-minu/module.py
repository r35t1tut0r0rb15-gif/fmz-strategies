"""Two strong closes above the EMA 9, daily bars, long only: two bars in a row closing within 1 % of their high and above the EMA 9 go long; the first close under the EMA 9 closes (the 09:30-09:40 window is
computed but never used).
Port of FMZ strategy #445449 "基于9EMA动态仓位的5分钟双收盘价强势突破策略9EMA-Dynamic-Position-Sizing-Strategy-with-Two-5-Minute-Close-Breakouts" (Two 5min Closes Above 9EMA Strategy with Dynamic Position Size).

FMZ source id: 445449

Source
    https://www.fmz.com/strategy/445449 (PineScript v5, FMZ last modified 2024-03-19 15:03:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-173), EMA 9; close >= 0.99 x high; session 09:30-09:40 (unused); qty 1000 / close
    c = close >= high x 0.99 and close > ema9;  c and c[1] -> entry Buy (qty 1000 / close);  close < ema9 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The title names 5-minute bars but the backtest header runs it on daily bars; timeCondition is
      computed and never used, so the entry has no time window, as written. A repeated entry while long
      is ignored (one position). Long only. The 1000 / close quantity is sizing. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, strong closes above the EMA, EMA exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1000 / close quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the time window is never applied).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445449_two_strong_closes_above_ema9_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [9, 20],
    "near_high": [0.99, 0.98],
}
DEFAULT_PARAMS = {"ema_len": 9, "near_high": 0.99}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ok = (c >= h * float(p["near_high"])) & (c > e)
    le = ok & ok.shift(1, fill_value=False)
    lx = c < e
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
