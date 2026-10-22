"""10 % daily moves, daily bars, long only: a close 10 % or more above the previous close goes long (unless the last state was long), with a 6-bar-low test; a 10 % fall, or a low under that 6-bar low,
closes at the next open.
Port of FMZ strategy #446765 "Dynamic Threshold Price Change Breakout Strategy" (Price Change).

FMZ source id: 446765

Source
    https://www.fmz.com/strategy/446765 (PineScript v4, FMZ last modified 2024-04-01 12:03:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-122), change 0.1 (10 %); stop lowest(low, 6) at the entry bar
    priceChange = close / close[1] - 1;  buy = pc >= 0.1 and (na(position) or position == -1) -> entry Long, stop = lowest(low, 6), position = 1
    sell = pc <= -0.1 and (na(position) or position == 1);  sell or low < stop -> close Long, position = -1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a bar-close test of the low against the 6-bar low saved on the entry bar, not an
      order; strategy.close fills at the next open. The script's position flag starts na, so a first
      10 % fall only sets it to -1. A low under the old stop keeps setting the flag to -1 after the
      trade, which only re-allows buying. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is a close-time test.
    2 generic: PASS, large daily moves with a swing-low test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446765_ten_pct_day_up_long_swing_low_test"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "change": [0.1, 0.05],
    "stop_len": [6, 10],
}
DEFAULT_PARAMS = {"change": 0.1, "stop_len": 6}


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
    lo, c = bars_df["low"], bars_df["close"]
    pc = (c / c.shift(1) - 1).to_numpy()
    ll = lo.rolling(int(p["stop_len"])).min().to_numpy()
    lv = lo.to_numpy(dtype=float)
    ch = float(p["change"])
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag = 0                                         # the script's position flag: 0 stands for na
    stop = np.nan
    held = False
    with np.errstate(invalid="ignore"):
        for i in range(m):
            buy = pc[i] >= ch and flag in (0, -1)
            sell = pc[i] <= -ch and flag in (0, 1)
            if buy:
                if not held:
                    le[i] = True
                stop, flag = ll[i], 1
            if sell or lv[i] < stop:
                if held:
                    lx[i] = True                     # strategy.close acts only on a held long
                flag = -1
            held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
