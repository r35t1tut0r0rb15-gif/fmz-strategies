"""Range filter trend entries, broker days: a smoothed-range filter of the close (EMA 100 of the absolute change, smoothed by EMA 199, times 3); a rising close above a rising filter goes long, a falling
close below a falling filter goes short; reversing.
Port of FMZ strategy #440367 "Smooth Volatility Band Strategy" (1SmSm1 Strategy).

FMZ source id: 440367

Source
    https://www.fmz.com/strategy/440367 (PineScript v4, FMZ last modified 2024-01-29 16:22:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-185), source close; sampling period 100; range multiplier 3
    smrng = ema(ema(|close - close[1]|, 100), 199) x 3;  filt = close > filt[1] ? max(filt[1], close - smrng) : min(filt[1], close + smrng);  upward / downward = counts of rising / falling filter bars
    longCondition = close > filt and close > close[1] and upward > 0 -> entry Buy;  shortCondition = close < filt and close < close[1] and downward > 0 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filter keeps the script's nz() start (the first previous filter is 0). The conditions are
      levels; an entry while already in that direction does nothing. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range filter of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440367_range_filter_trend_daily"
FAMILY = "range_filter_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [100, 50],
    "mult": [3.0, 1.5],
}
DEFAULT_PARAMS = {"per": 100, "mult": 3.0}


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


def _filter(c, rng):
    cv, rv = c.to_numpy(dtype=float), rng.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    f_prev = np.nan
    for i in range(len(cv)):
        pv = 0.0 if np.isnan(f_prev) else f_prev
        x, r = cv[i], rv[i]
        if x > pv:
            f = pv if (x - r) < pv else x - r
        else:
            f = pv if (x + r) > pv else x + r
        out[i] = f
        f_prev = f
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    t = int(p["per"])
    avr = (c - c.shift(1)).abs().ewm(span=t, adjust=False).mean()
    rng = avr.ewm(span=2 * t - 1, adjust=False).mean() * float(p["mult"])
    filt = _filter(c, rng)
    fv = filt.to_numpy()
    m = len(fv)
    upw, dnw = np.zeros(m), np.zeros(m)
    u = d = 0.0
    for i in range(1, m):
        if fv[i] > fv[i - 1]:
            u, d = u + 1, 0.0
        elif fv[i] < fv[i - 1]:
            u, d = 0.0, d + 1
        upw[i], dnw[i] = u, d
    long_ = (c > filt) & (c > c.shift(1)) & (upw > 0)
    short_ = (c < filt) & (c < c.shift(1)) & (dnw > 0)
    false = pd.Series(False, index=c.index)
    return long_, false, short_, false.copy()


def portfolio_kwargs(**params):
    return {}
