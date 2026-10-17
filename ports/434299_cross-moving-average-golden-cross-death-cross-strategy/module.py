"""Ichimoku trend entries with a cooldown, broker days, long only: with the bar body above the Tenkan and above Senkou A
and a bullish cloud (A above B), a green bar crossing up through Senkou A or a bullish cloud twist goes long, unless a
long signal was taken in the previous 5 bars; with the body below the Tenkan and below Senkou B and a bearish cloud, a
red bar crossing down through Senkou B or a bearish twist closes the long.
Port of FMZ strategy #434299 "Cross Moving Average Golden Cross Death Cross Strategy" (Ichimoku Kinko Hyo Strategy).

FMZ source id: 434299

Source
    https://www.fmz.com/strategy/434299 (PineScript v4, FMZ last modified 2023-12-05 11:11:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 177-280), Tenkan 9, Kijun 26, Senkou B 52, offset 26 (plots only), cooldown 5, Chikou check off
    bullish_trend = min(open, close) > tenkan and min(open, close) > ssa and ssa > ssb;  buy1 = close > open and close > ssa and open < ssa;  buy2 = ssa > ssb and ssa[1] < ssb[1]
    go_long = bullish_trend and (buy1 or buy2), false if go_long[1..5] -> entry long
    exit_long = bearish_trend and (sell1 or sell2) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are the current Donchian midpoints (the offset only shifts the plots). The cooldown
      reads the variable's own past values, i.e. the go_long signals that survived the cooldown, so
      it is a loop. A signal while long is ignored (pyramiding 0). The Chikou check is off (both
      flags true). Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines and cloud twists.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
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

NAME = "fmz_434299_ichimoku_twist_long"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "cooldown": [5, 0],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "ssb_len": 52, "cooldown": 5}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    don = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    tenkan, kijun, ssb = don(int(p["tenkan"])), don(int(p["kijun"])), don(int(p["ssb_len"]))
    ssa = (tenkan + kijun) / 2
    bmin, bmax = np.minimum(o, c), np.maximum(o, c)
    bull, bear = ssa > ssb, ssa < ssb
    bull_tr = (bmin > tenkan) & (bmin > ssa) & bull
    bear_tr = (bmax < tenkan) & (bmax < ssb) & bear
    buy1 = (c > o) & (c > ssa) & (o < ssa)
    buy2 = bull & bear.shift(1, fill_value=False)
    sell1 = (c < o) & (c < ssb) & (o > ssb)
    sell2 = bear & bull.shift(1, fill_value=False)
    raw = (bull_tr & (buy1 | buy2)).to_numpy()
    ex = (bear_tr & (sell1 | sell2)).to_numpy()
    m, cd = len(raw), int(p["cooldown"])
    go = np.zeros(m, dtype=bool)
    for i in range(m):
        go[i] = raw[i] and not go[max(0, i - cd):i].any()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(go, index=ix), pd.Series(ex, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
