"""Donchian 50 breakouts, broker days, long only from flat: a close crossing above the previous bar's 50-bar high goes long;
a close crossing under the previous 12-bar low, or a new 12-bar low, closes it; a monetary stop of 1000 on a 10000
position is a 10 % stop from the fill.
Port of FMZ strategy #434675 "Donchian Channels Breakout Quantitative Trading Strategy" (ChannelsBreakout).

FMZ source id: 434675

Source
    https://www.fmz.com/strategy/434675 (PineScript v4, FMZ last modified 2023-12-08 11:00:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 165-199), channel 50, exit channel 50 / 4 = 12 (integer division); money 10000 per trade, monetary stop 1000; first year 2000
    crossover(close, highest(high, 50)[1]) and position_size == 0 -> entry long (qty = int(10000 / close))
    crossunder(close, lowest(low, 12)[1]) or lowest(low, 12) < lowest(low, 12)[1] -> close long;  exit(stop = avg - 1000 / position_size)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop distance is the monetary stop over the quantity, 1000 / (10000 / close) = 10 % of the
      fill (sl_stop 0.10; the quantity's integer rounding is sizing). The year filter (2000) is the
      author's window: dropped. 50 / 4 is 12 (Pine v4 integer division).
    * Entries only from flat: "flat" follows the house stop on bars and the exit signal. Long only.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, channel breakouts and a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the money-per-trade quantity and the monetary stop stored (the stop re-expressed as 10 %).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434675_donchian50_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [50, 20],
    "sl_pct": [0.10, 0.05],
}
DEFAULT_PARAMS = {"period": 50, "sl_pct": 0.10}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["period"])
    up1 = h.rolling(n).max().shift(1)
    dn = lo.rolling(n // 4).min()
    dn1 = dn.shift(1)
    buy = ((c > up1) & (c.shift(1) <= up1.shift(1))).to_numpy()
    ex = (((c < dn1) & (c.shift(1) >= dn1.shift(1))) | (dn < dn1)).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    s_ = float(p["sl_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ei = 0, -1
    for i in range(m):
        if pos == 1 and i >= ei and lv[i] <= ov[ei] * (1 - s_):    # the house stop from the fill price
            pos = 0
        if pos == 1 and i >= ei and ex[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos, ei = True, 1, i + 1
    return le, lx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
