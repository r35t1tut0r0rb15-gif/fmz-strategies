"""First closes over the EMA 20 with the EMA 20 over the EMA 200, daily bars, long only: a buy after each close under the EMA 20 re-arms the signal. The 0.5 % / 1.5 % bracket is set from the position price on the signal bar, which is na from flat, so it is armed only by a repeat signal inside a trade: not ported (pending), no exit.
Port of FMZ strategy #473270 "Dual Moving Average Trend Following Trading System with Risk Reward Ratio Optimization Strategy" (Estrategia de Compra con Ratio 3:1).

FMZ source id: 473270

Source
    https://www.fmz.com/strategy/473270 (PineScript v5, FMZ last modified 2024-11-28 17:20:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-139), EMA 20 / 200 (constants); bracket avg x 0.995 / x 1.015 sent on the signal bar only
    close > ema20 and ema20 > ema200 and not done -> entry Compra, done := true, exit(stop = avg x 0.995, limit = avg x 1.015);  close < ema20 -> done := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.position_avg_price on the signal bar is na from flat, so the first bracket of a trade
      carries no level; only a later signal inside the same trade (after a close under the EMA 20 and a
      new first close over it) sends real levels. A bracket armed only by repeat signals is not ported
      (as #437800): kept pending (mark trailing_stop_pending), so the port has no exit. The flag is
      followed in a loop. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, first EMA 20 closes in an EMA 20 / 200 uptrend; bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473270_first_close_over_ema20_ema200_trend_long_bracket_pending"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    e20, e200 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    cond = ((c > e20) & (e20 > e200)).to_numpy()
    reset = (c < e20).to_numpy()
    le = np.zeros(len(c), dtype=bool)
    done = False
    for i in range(len(c)):
        if cond[i] and not done:
            le[i], done = True, True
        if reset[i]:
            done = False
    false = pd.Series(False, index=bars_df.index)
    return pd.Series(le, index=bars_df.index), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
