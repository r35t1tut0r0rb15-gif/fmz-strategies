"""SMA 9 / 21 golden crosses bought with a 1 % stop / 1 % target from the entry, closed on the death cross, long only,
daily (broker-day) bars.
Port of FMZ strategy #482846 "双均线止盈止损趋势交易策略-Dual-Moving-Average-Trend-Trading-Strategy-with-Stop-Loss-and-Take-Profit" (Moving Average Crossover with Stop Loss and Take Profit).

FMZ source id: 482846

Source
    https://www.fmz.com/strategy/482846 (PineScript v6, FMZ last modified 2025-02-27 17:36:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 94-119), SMA 9 / 21, SL 1 %, TP 1 %
    long = crossover(sma9, sma21): entry + exit(stop / limit = avg_price x (1 -+ 1 %)); death cross -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is issued on the signal bar from strategy.position_avg_price, na while flat: as written no stop or
      target is ever placed (crosses alternate, so no later re-issue). The port applies the 1 % / 1 % bracket from the
      fill (the evident intent), as #489289. Decision owed: keep this, or the literal behaviour (cross exits only).
    * Long only; the death-cross close is an exit signal. Stop module: portfolio_kwargs {} (D4). Daily bars are broker
      days (17:00 America/New_York) stamped with their first minute (as #430984); stops on daily bars:
      coarse_bar_stop. FREQ = "1D" from the backtest header (the 15-minute comments are labels).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (decision owed).
    2 generic: PASS, moving averages and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482846_sma9_21_golden_cross_pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 3.0],
    "tp_pct": [1.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "sl_pct": 1.0, "tp_pct": 1.0}


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
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
