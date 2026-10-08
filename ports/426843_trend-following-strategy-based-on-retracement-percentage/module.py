"""Buy the dip from the 90-bar high, long only: from flat, a close at least 6 % under the 90-bar
highest high goes long; a 6 % take-profit closes it.
Port of FMZ strategy #426843 "Trend Following Strategy Based on Retracement Percentage".

Source
    https://www.fmz.com/strategy/426843 (PineScript v4, FMZ last modified 2023-09-14 19:49:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 126-139), range 90, retrace 3 %, take profit 6 %,
basis points 100
    close <= highest(high, 90) * (1 - take_profit_percent / 100) and flat -> entry long
    on the fill bar: exit(profit = close * 6 % * basis_points ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the entry uses the take-profit percent (6 %), not the retrace input (3 %);
      kept (decision owed: likely a slip).
    * The target is 6 % of the fill bar's close in ticks scaled by basis_points = 100, i.e. 6 %
      only when the tick is 0.01 (the author's assumption; on BTC_USDT's 0.1 tick it is 60 %).
      Criterion 2: ported as meant, tp_stop = 6 % of the fill price.
    * Entries need a flat position, so simulate() mirrors the engine's target from the fill bar
      on. Long only.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
      Target on daily bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426843_dip_from_high_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "range_of_tops": [60, 90, 120],
    "take_profit_percent": [6, 10],
}
DEFAULT_PARAMS = {"range_of_tops": 90, "take_profit_percent": 6}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = p["take_profit_percent"] / 100
    top = bars_df["high"].rolling(int(p["range_of_tops"])).max()
    dip = (bars_df["close"] <= top * (1 - tp)).to_numpy()
    o, h = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    m = len(o)
    le = np.zeros(m, dtype=bool)
    pos, pending, target = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, target, pending = 1, o[i] * (1 + tp), False
        if pos == 1 and h[i] >= target:
            pos = 0
        if pos == 0 and not pending and dip[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": p["take_profit_percent"] / 100}


def portfolio_kwargs(**params):
    return {}
