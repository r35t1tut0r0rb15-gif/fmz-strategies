"""Moving-average direction state with a tick trailing stop, broker days: the SMA 20 at or above its value two bars back is long, below is short; entries are sent on every bar of the state, reversing; each
trade trails 400 ticks behind the best price once 200 ticks in profit (house trail).
Port of FMZ strategy #437747 "Multi Timeframe Moving Average Crossover Optimization Strategy" (UMA Strategy).

FMZ source id: 437747

Source
    https://www.fmz.com/strategy/437747 (PineScript v2, FMZ last modified 2024-01-05 12:05:42).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 116-186), MA type 1 (SMA), length 20, colour smoothing 2; current resolution; trailing stop on: points 200, offset 400
    out1 = security(tickerid, current, sma(close, 20));  ma_up = out1 >= out1[2];  ma_down = out1 < out1[2]
    entry long when ma_up;  entry short when ma_down;  exit(trail_points = 200, trail_offset = 400) for both;  exit(when = ...) without levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The resolution is the chart's own. Criterion 2: on daily BTC (0.1 tick, ATR about 1000 USD near
      40000) the trail activates after 200 ticks (20 USD, about 0.0005 of the price) and trails 400 ticks
      (40 USD, about 0.04 ATR) behind the best price: the house trail {"type": "volatility", "atr_n": 14,
      "k": 0.04, "anchor": "high_low", "activate_after": 0.0005} (stated approximation, as #429564; mark
      trailing_stop). The level-less exit calls place no order. MA types 2-7 are ported except VWMA
      (volume, check 8); the default is the SMA. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> ATR multiple and a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick trail inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427510 (3 members, best partner #438047, Jaccard 0.753); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_437747_ma_direction_state_trail"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "trail_k": [0.04, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "trail_k": 0.04, "atype": 1, "smoothe": 2, "atr_len": 14, "trail_activate": 0.0005}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _avg(c, n, atype):
    if atype == 1:
        return c.rolling(n).mean()
    if atype == 2:
        return c.ewm(span=n, adjust=False).mean()
    if atype == 3:
        return _wma(c, n)
    if atype == 4:
        return _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    if atype == 6:
        return _rma(c, n)
    if atype == 7:
        e1 = c.ewm(span=n, adjust=False).mean()
        e2 = e1.ewm(span=n, adjust=False).mean()
        return 3 * (e1 - e2) + e2.ewm(span=n, adjust=False).mean()
    raise ValueError("MA type 5 (VWMA) not ported (volume, check 8)")


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    out = _avg(bars_df["close"], int(p["length"]), int(p["atype"]))
    k = int(p["smoothe"])
    up = out >= out.shift(k)
    dn = out < out.shift(k)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
