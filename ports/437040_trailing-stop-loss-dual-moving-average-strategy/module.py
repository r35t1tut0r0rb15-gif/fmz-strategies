"""SMA 21 / 49 crossings with a ratcheting trailing sell, broker days, long only: a fast SMA crossing over the slow one goes long; after a crossing under, a sell level 3 % under that close ratchets up with 97 %
of each bar's high, and a low crossing under it closes the long.
Port of FMZ strategy #437040 "Trailing Stop Loss Dual Moving Average Strategy" (TS).

FMZ source id: 437040

Source
    https://www.fmz.com/strategy/437040 (PineScript v5, FMZ last modified 2023-12-29 16:59:17).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 217-292), SMA 21 / 49, trailing on, deviation 3 %, exit control source low; date filter true
    open = crossover(sma 21, sma 49);  close = crossunder(...);  longExitPrice = close x 0.97 on the close cross (when long), else max(high x 0.97, nz(prev, 999999)) while the close is active and no exit since, else na
    exitLongPosition = crossunder(closeLong ? close : low, longExitPrice) -> close Long Entry;  entry Long Entry on open

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell level is tested on bar closes (a low crossing under the level known at that bar's close),
      so it is a close-based exit signal from simulate(), not a stop (rule 2); percents kept as written.
      barssince() with nz(.., 999999) is followed as written (with no crossing yet, the level is the 999999
      placeholder and cannot be crossed); barssince of the exit flag reads its previous bar's value (the var
      is reassigned after the test). The date filter is always true. Long only. The 100 % of equity size is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trailing level is tested on closes.
    2 generic: PASS, percent trailing level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437040_sma_cross_trailing_sell_long"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 10],
    "dev": [0.03, 0.05],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 49, "dev": 0.03}
BIG = 999999.0


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    o_x = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    c_x = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    d = float(p["dev"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_open = last_close = last_exit = None
    exit_prev = False
    level_prev = np.nan
    src_prev = np.nan
    pos = 0
    for i in range(m):
        if o_x[i]:
            last_open = i
        if c_x[i]:
            last_close = i
        if exit_prev:
            last_exit = i - 1
        bo = BIG if last_open is None else i - last_open
        bc = BIG if last_close is None else i - last_close
        be = BIG if last_exit is None else i - (last_exit + 1)
        try_exit = bo >= bc and be >= bc
        if c_x[i] and pos == 1:
            level = cv[i] * (1 - d)
        elif try_exit:
            level = max(hv[i] * (1 - d), BIG if np.isnan(level_prev) else level_prev)
        else:
            level = np.nan
        src = cv[i] if c_x[i] else lv[i]
        ex = bool(src < level and src_prev >= level_prev)
        if pos == 1 and ex:                              # an entry while long at the bar's close is ignored
            lx[i] = True
            pos = 0
        elif pos == 0 and o_x[i]:
            le[i] = True
            pos = 1
        exit_prev, level_prev, src_prev = ex, level, src
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
