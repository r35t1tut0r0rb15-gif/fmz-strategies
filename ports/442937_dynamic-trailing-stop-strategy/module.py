"""A flip-flop trailing line on the day's last 1-minute bar, daily bars: the line trails under the price by 228.5 and over it by 243.5 price units (re-expressed as fractions); the price above the line
holds long, below holds short; reversing.
Port of FMZ strategy #442937 "Dynamic Trailing Stop Strategy" (BitMex Trailing Stop Strategy).

FMZ source id: 442937

Source
    https://www.fmz.com/strategy/442937 (PineScript v3, FMZ last modified 2024-02-27 15:02:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-173), long offset 228.5, short offset 243.5 (price units); high / low / close requested on 1 minute
    trailstop = (lo <= ts[1] and lo[1] >= ts[2]) ? price + 243.5 : (hi >= ts[1] and hi[1] <= ts[2]) ? price - 228.5 : hi > ts[1] ? max(hi - 228.5, ts[1]) : lo < ts[1] ? min(lo + 243.5, ts[1]) : price
    trailstop <= price (green) -> entry Long;  trailstop > price (red) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1-minute requests from a daily chart are a lower time frame: each returns the day's last
      1-minute bar (as #436765), built from minutes in precompute. Criterion 2: the offsets are price
      units: as fractions of the price at the BTC reading of 42000, 0.00544 under and 0.0058 over. The
      entries are level tests, refused while held. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 1-minute values end with the day.
    2 generic: ADAPT, price-unit offsets -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442937_last_minute_flip_trail_line_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_frac": [0.00544, 0.02],
    "short_frac": [0.0058, 0.02],
}
DEFAULT_PARAMS = {"long_frac": 0.00544, "short_frac": 0.0058}


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
    g = df.groupby(lab)
    bars = g.agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    lastm = g.last()                                   # the day's last 1-minute bar
    bars["m_high"], bars["m_low"], bars["m_close"] = lastm["high"], lastm["low"], lastm["close"]
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hi, lo, pr = (bars_df[k].to_numpy(dtype=float) for k in ("m_high", "m_low", "m_close"))
    fl, fs = float(p["long_frac"]), float(p["short_frac"])
    m = len(pr)
    ts = np.full(m, np.nan)
    for i in range(m):
        t1 = ts[i - 1] if i >= 1 else np.nan
        t2 = ts[i - 2] if i >= 2 else np.nan
        lo1 = lo[i - 1] if i >= 1 else np.nan
        hi1 = hi[i - 1] if i >= 1 else np.nan
        if lo[i] <= t1 and lo1 >= t2:
            ts[i] = pr[i] * (1 + fs)
        elif hi[i] >= t1 and hi1 <= t2:
            ts[i] = pr[i] * (1 - fl)
        elif hi[i] > t1:
            ts[i] = max(hi[i] * (1 - fl), t1)
        elif lo[i] < t1:
            ts[i] = min(lo[i] * (1 + fs), t1)
        else:
            ts[i] = pr[i]
    ix = bars_df.index
    green = pd.Series(ts <= pr, index=ix)
    red = pd.Series(ts > pr, index=ix)
    false = pd.Series(False, index=ix)
    return green, false, red, false.copy()


def portfolio_kwargs(**params):
    return {}
