"""Alternating Ichimoku trend entries with a percent bracket, broker days: with the tenkan above the kijun, a positive
25-bar momentum, the close above the cloud of 25 bars ago and a green cloud, a long opens unless the last signal was
already a long; the bearish mirror opens a short only after a long signal. Each trade carries a 5 % stop and a 20 %
target.
Port of FMZ strategy #433148 "Ichimoku Backtester with TP SL and Cloud Confirmation" (Ichimoku Backtester with TP and SL).

FMZ source id: 433148

Source
    https://www.fmz.com/strategy/433148 (PineScript v4, FMZ last modified 2023-11-24 17:32:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-269), tenkan 9, kijun 26, span B 52, offsets 26; wait for cloud on; SL 5 %, TP 20 % both sides
    bullish = tenkan > kijun and mom(close, 25) > 0 and close > max(spanA, spanB)[25] and spanA > spanB;  bearish mirrors (spanA <= spanB)
    open_long = bullish and not in_long -> in_long := true, entry long;  open_short = bearish and in_long -> in_long := false, entry short
    exit(stop = avg (1 -/+ 5 %), limit = avg (1 +/- 20 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * in_long is a signal toggle, not the position: a long signal needs the last signal to have been a
      short (or none) and a short signal needs a long before it, so the entries alternate even after
      a stop or target exit. The closes on the other side's signal only apply when a side is disabled.
    * The bracket is symmetric: sl_stop 0.05, tp_stop 0.20 of the fill. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; stops on daily bars: mark
      coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, Ichimoku lines, momentum sign and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 95 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433148_ichimoku_alternating_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.05, 0.1],
    "tp_pct": [0.2, 0.1],
}
DEFAULT_PARAMS = {"ts_bars": 9, "ks_bars": 26, "ssb_bars": 52, "offset": 26, "sl_pct": 0.05, "tp_pct": 0.2}


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

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    ten, kij = mid(p["ts_bars"]), mid(p["ks_bars"])
    sa, sb = (ten + kij) / 2, mid(p["ssb_bars"])
    k = int(p["offset"]) - 1
    hi = pd.concat([sa.shift(k), sb.shift(k)], axis=1).max(axis=1, skipna=False)
    lw = pd.concat([sa.shift(k), sb.shift(k)], axis=1).min(axis=1, skipna=False)
    mom = c - c.shift(k)
    green = sa > sb
    bull = ((ten > kij) & (mom > 0) & (c > hi) & green).to_numpy()
    bear = ((ten < kij) & (mom < 0) & (c < lw) & ~green).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_long = False
    for i in range(m):
        ol = bull[i] and not in_long
        os_ = bear[i] and in_long
        if ol:
            in_long, le[i] = True, True
        if os_:
            in_long, se[i] = False, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
