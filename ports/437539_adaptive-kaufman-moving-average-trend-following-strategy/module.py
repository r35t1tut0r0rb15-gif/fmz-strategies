"""Previous close against Kaufman's adaptive average, broker days: the previous close above the KAMA 21 (efficiency-ratio smoothing between 0.666 and 0.0645, squared) is long, below is short, equal holds; an
optional switch trades the reverse; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #437539 "Adaptive Kaufman Moving Average Trend Following Strategy" (Kaufman Moving Average Adaptive (KAMA)).

FMZ source id: 437539

Source
    https://www.fmz.com/strategy/437539 (PineScript v2, FMZ last modified 2024-01-03 16:01:20).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 195-213), length 21, fast end 0.666, slow end 0.0645, reverse off
    nefratio = |close - close[21]| / sum(|change(close)|, 21);  nsmooth = (nefratio (0.666 - 0.0645) + 0.0645)^2;  nAMA = nz(nAMA[1]) + nsmooth (close - nz(nAMA[1]))
    pos = 1 if close[1] > nAMA, -1 if close[1] < nAMA, else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA starts from 0 (nz) and climbs toward the price, as written (as #436514): the first stretch
      of data is long until it catches up. The test compares the PREVIOUS close with the current KAMA, as
      written. The state is a level, so the entry is sent on every bar of the state. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against an adaptive average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437539_kama_prev_close_state"
FAMILY = "adaptive_average"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 10],
}
DEFAULT_PARAMS = {"length": 21, "fast_end": 0.666, "slow_end": 0.0645, "reverse": False}


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
    c = bars_df["close"]
    n = int(p["length"])
    noise = c.diff().abs().rolling(n).sum()
    sig_ = (c - c.shift(n)).abs()
    with np.errstate(divide="ignore", invalid="ignore"):
        er = (sig_ / noise).where(noise != 0, 0.0)
    fe, se_ = float(p["fast_end"]), float(p["slow_end"])
    sm = ((er * (fe - se_) + se_) ** 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ama = np.full(m, np.nan)
    pos = np.zeros(m)
    prev_pos = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            a1 = ama[i - 1] if i and not np.isnan(ama[i - 1]) else 0.0
            ama[i] = a1 + sm[i] * (cv[i] - a1)
            c1 = cv[i - 1] if i else np.nan
            if c1 > ama[i]:
                prev_pos = 1.0
            elif c1 < ama[i]:
                prev_pos = -1.0
            pos[i] = prev_pos
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
