"""Broker days, long only: OBV crossing over its SMA 190 goes long; OBV crossing under its SMA 202 closes it.
Port of FMZ strategy #449808 "基于OBV与MA交叉信号的趋势跟踪策略-Trend-Following-Strategy-Based-on-OBV-and-MA-Crossover-Signals" (OBVious MA Strategy [1000X] (ThousandX_Trader)).

FMZ source id: 449808

Source
    https://www.fmz.com/strategy/449808 (PineScript v5, FMZ last modified 2024-04-29 13:48:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 111-171), direction long; long entry MA 190, long exit MA 202 (short MAs 395 / 300 unused)
    obv = cum(change(close) >= 0 ? volume : -volume);  longCondition = crossover(obv, sma(obv, 190)) and position_size <= 0 -> entry Long Entry
    longExitCondition = crossunder(obv, sma(obv, 202)) -> close Long Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * An unchanged close counts as up in this OBV (>= 0), as written; the first bar's na change counts
      as down. The direction input is "long", so the short branch never fires. Long only. 100 % of
      equity, margin, slippage and commission are sizing and costs. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OBV crossings of long SMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, margin 0.1, commission 0.1 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449808_obv_sma190_202_cross_long_only"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_len": [190, 100],
    "exit_len": [202, 100],
}
DEFAULT_PARAMS = {"entry_len": 190, "exit_len": 202}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    obv = pd.Series(np.where(c.diff() >= 0, v, -v), index=c.index).cumsum()
    me, mx = obv.rolling(int(p["entry_len"])).mean(), obv.rolling(int(p["exit_len"])).mean()
    buy = ((obv > me) & (obv.shift(1) <= me.shift(1))).to_numpy()
    sell = ((obv < mx) & (obv.shift(1) >= mx.shift(1))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and pos == 0:
            new = 1
        if new == pos and pos == 1 and sell[i]:
            new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            else:
                lx[i] = True
            pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
