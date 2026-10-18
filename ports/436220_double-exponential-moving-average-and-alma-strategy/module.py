"""Second EMA against an Arnaud Legoux moving average, broker days: the EMA 10 over the ALMA (50, 0.85, 6) goes long, under it goes short (reversing). The EMA 5 term is
only a truthy value in the script's condition.
Port of FMZ strategy #436220 "Double Exponential Moving Average and ALMA Strategy" (Double Exponential Moving Average & ALMA Strategy).

FMZ source id: 436220

Source
    https://www.fmz.com/strategy/436220 (PineScript v3, FMZ last modified 2023-12-22 12:44:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-148), EMA 5 / 10; ALMA window 50, offset 0.85, sigma 6
    longCondition = e1 and e2 > alma(close, 50, 0.85, 6)  (that is e1 and (e2 > alma));  shortCondition = e1 and e2 < alma;  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "e1 and e2 > alma" reads as e1 AND (e2 > alma): the EMA 5 is a nonzero number, so true; the rule is the EMA 10 against
      the ALMA. ALMA weights: m = floor(offset (window - 1)), s = window / sigma, w_i = exp(-(i - m)^2 / (2 s^2)),
      normalised, i = 0 for the oldest bar of the window. The conditions are states re-sent every bar.
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average against an adaptive average.
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

NAME = "fmz_436220_ema_vs_alma"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "windowsize": [50, 30],
    "l2": [10, 5],
}
DEFAULT_PARAMS = {"windowsize": 50, "offset": 0.85, "sigma": 6.0, "l2": 10}


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


def _alma(s, window, offset, sigma):
    m = np.floor(offset * (window - 1))
    sd = window / sigma
    w = np.exp(-((np.arange(window) - m) ** 2) / (2 * sd * sd))
    w = w / w.sum()
    return s.rolling(window).apply(lambda a: float(np.dot(a, w)), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e2 = c.ewm(span=int(p["l2"]), adjust=False).mean()
    alma = _alma(c, int(p["windowsize"]), float(p["offset"]), float(p["sigma"]))
    le = (e2 > alma).fillna(False).astype(bool)
    se = (e2 < alma).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
