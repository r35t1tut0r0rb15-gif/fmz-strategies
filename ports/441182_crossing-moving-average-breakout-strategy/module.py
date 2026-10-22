"""Stacked-MA breakouts with a signal-bar stop and a 3-bar time exit, broker days: from flat, SMA 5 > 10 > 20 with the high at its 10-bar high and the close crossing over the previous 10-bar high goes
long with a stop at the signal bar's low; the mirror goes short with a stop at its high; 3 bars after the latest flat setup bar the position closes.
Port of FMZ strategy #441182 "Crossing Moving Average Breakout Strategy" (Cross - HOBBIE).

FMZ source id: 441182

Source
    https://www.fmz.com/strategy/441182 (PineScript v5, FMZ last modified 2024-02-06 15:02:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-209), MAs 20 / 10 / 5 (SMA); candles back 10; bars to exit 3
    longCondition = sma5 > sma10 and sma10 > sma20 and high == highest(10);  longCondition_entry = longCondition and flat
    longCondition_entry and crossover(close, highest(10)[1]) -> entry Long, exit(stop = low);  barssince(longCondition_entry) >= 3 -> close Long  (short mirrored with low == lowest(10), stop = high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's low (high for a short): sl = (close - low) / close of the signal bar,
      shifted one bar inside stops() and re-based on the fill. barssince counts from the latest bar with the
      setup while flat, which while a position is held is its signal bar, so the time exit comes 3 bars
      after it. Entries need a flat position: opposite entries cannot occur (entries only from flat). Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, stacked SMAs, channel breakout and bar count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441182_stacked_sma_breakout_bar_stop_3bar_exit"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "candles_back": [10, 20],
    "bars_valid": [3, 5],
}
DEFAULT_PARAMS = {"candles_back": 10, "bars_valid": 3, "long_period": 20, "medium_period": 10, "short_period": 5}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s5, s10, s20 = (c.rolling(int(p[k])).mean() for k in ("short_period", "medium_period", "long_period"))
    n = int(p["candles_back"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    lcond = (s5 > s10) & (s10 > s20) & (h == hh)
    scond = (s5 < s10) & (s10 < s20) & (lo == ll)
    xo = (c > hh.shift(1)) & (c.shift(1) <= hh.shift(2))
    xu = (c < ll.shift(1)) & (c.shift(1) >= ll.shift(2))
    # long stop at the signal low, short stop at the signal high (the two setups never meet on one bar)
    sl = ((c - lo) / c).where(~(scond & xu), (h - c) / c)
    return lcond.to_numpy(), scond.to_numpy(), xo.to_numpy(), xu.to_numpy(), sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    lcond, scond, xo, xu, sl_ser = _setup(bars_df, p)
    sl = sl_ser.to_numpy()
    kb = int(p["bars_valid"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    last_l = last_s = None
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        lce = lcond[i] and pos == 0
        sce = scond[i] and pos == 0
        if lce:
            last_l = i
        if sce:
            last_s = i
        if lce and xo[i] and i + 1 < m:
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
        elif sce and xu[i] and i + 1 < m:
            se[i], pos, entry_i, s_ = True, -1, i + 1, sl[i]
        elif pos == 1 and i >= entry_i and last_l is not None and i - last_l >= kb:
            lx[i], pos = True, 0
        elif pos == -1 and i >= entry_i and last_s is not None and i - last_s >= kb:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = _setup(bars_df, p)[4]
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
