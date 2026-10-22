"""Direction of the day's last 2-hour bar, broker days, long only: the first day whose last 2-hour bar closes above its open after one that did not (a fresh up-flip after a down-flip) goes long; the first
down-flip after an up-flip closes.
Port of FMZ strategy #442383 "多时间框架EMA突破与K线形态组合策略Trading-Strategy-Based-on-Multiple-Time-Frame-EMA-Breakthrough-and-K-line-Pattern-Combination" (ck - CryptoSniper Longs (S) v1).

FMZ source id: 442383

Source
    https://www.fmz.com/strategy/442383 (PineScript v2, FMZ last modified 2024-02-21 15:00:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-218), Period "120" on a daily chart; the channel, S/R, EMA and Hull blocks are plotted only; 100 % of equity, capital 100, commission 0.25
    long = crossover(security("120", close), security("120", open));  short = crossunder(..);  last_long / last_short = time of the latest long / short
    crossover(last_long, last_short) -> entry Long Open;  crossover(last_short, last_long) -> close Long Open

Interpretation choices (Pine rules in SURVEY_README.md)
    * A lower timeframe requested from a daily chart returns its last bar inside the chart bar (as
      #436765): the 2-hour bars are counted from the broker day's start (17:00 America/New_York), twelve per
      day, and the last one ends with the day. The time stamps make the entry fire on the first up-flip
      after a down-flip (and the close on the first down-flip after an up-flip). Long only. The 100 % of
      equity size, capital and commission are sizing. Daily bars are broker days, stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 2-hour values end with the daily bar.
    2 generic: PASS, last-2-hour-bar direction flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 2-hour bars counted from the day's start.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442383_last_2h_bar_direction_flip_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tf_minutes": [120, 240],
}
DEFAULT_PARAMS = {"tf_minutes": 120}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # sub-bars counted from each broker day's start (17:00 America/New_York)
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    k = (ny - ny.normalize()) // pd.Timedelta(minutes=int(p["tf_minutes"]))
    sub = df.groupby([lab, np.asarray(k)]).agg({"open": "first", "close": "last"})
    day = sub.index.get_level_values(0)
    last = sub[~day.duplicated(keep="last")]        # the day's last sub-bar
    last.index = last.index.get_level_values(0)
    bars = bars.join(last.rename(columns={"open": "ltf_open", "close": "ltf_close"}))
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    o2, c2 = bars_df["ltf_open"], bars_df["ltf_close"]
    up = ((c2 > o2) & (c2.shift(1) <= o2.shift(1))).to_numpy()
    dn = ((c2 < o2) & (c2.shift(1) >= o2.shift(1))).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_l = last_s = 0
    held = 0
    for i in range(m):
        pl, ps = last_l, last_s
        if up[i]:
            last_l = i + 1
        if dn[i]:
            last_s = i + 1
        ls_sig = last_l > last_s and pl <= ps
        ss_sig = last_s > last_l and ps <= pl
        if held == 0 and ls_sig and i + 1 < m:
            le[i], held = True, 1
        elif held == 1 and ss_sig:
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
