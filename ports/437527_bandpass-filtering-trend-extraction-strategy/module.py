"""Ehlers band-pass trend sign, broker days: the 40-bar mean of a 20-bar band-pass filter of hl2 above zero is long, below is short, at zero the state holds; an optional switch trades the reverse; entries are
sent on every bar of the state, reversing.
Port of FMZ strategy #437527 "Bandpass Filtering Trend Extraction Strategy" (Extracting The Trend Strategy Backtest).

FMZ source id: 437527

Source
    https://www.fmz.com/strategy/437527 (PineScript v2, FMZ last modified 2024-01-03 15:22:49).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 123-141), length 20, delta 0.5, trigger 0, reverse off
    bp = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) nz(bp[1]) - alpha nz(bp[2]);  xMean = sma(bp, 40);  pos = 1 if xMean > 0, -1 if < 0, else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * beta, gamma and alpha use the script's 3.1415 for pi, as written (the band-pass of #436791). The
      state is a level, so the entry is sent on every bar of the state; a same-side entry while in the
      position is ignored (pyramiding 0). REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-pass sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430069 (3 members, best partner #430069, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437527_bandpass_trend_sign_state"
FAMILY = "cycle_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "delta": [0.5, 0.3],
}
DEFAULT_PARAMS = {"length": 20, "delta": 0.5, "trigger": 0.0, "reverse": False}


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


def _bandpass_mean(bars_df, n, delta):
    pr = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    beta = np.cos(3.1415 * (360.0 / n) / 180.0)
    gamma = 1.0 / np.cos(3.1415 * (720.0 * delta / n) / 180.0)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    m = len(pr)
    bp = np.full(m, np.nan)
    for i in range(2, m):
        b1 = 0.0 if np.isnan(bp[i - 1]) else bp[i - 1]
        b2 = 0.0 if np.isnan(bp[i - 2]) else bp[i - 2]
        bp[i] = 0.5 * (1 - alpha) * (pr[i] - pr[i - 2]) + beta * (1 + alpha) * b1 - alpha * b2
    return pd.Series(bp, index=bars_df.index).rolling(2 * n).mean().to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    xm = _bandpass_mean(bars_df, int(p["length"]), float(p["delta"]))
    trig = float(p["trigger"])
    m = len(xm)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if xm[i] > trig:
                prev = 1.0
            elif xm[i] < trig:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
