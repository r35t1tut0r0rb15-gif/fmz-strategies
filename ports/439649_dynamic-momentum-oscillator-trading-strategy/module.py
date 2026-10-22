"""Wall's Dynamic Momentum Oscillator, broker days: the smoothed stochastic (10) recentred on the midpoint of its lowest and highest values so far; above 77 holds a long, below 23 a short; reversing.
Port of FMZ strategy #439649 "Dynamic Momentum Oscillator Trading Strategy" (Dynamo).

FMZ source id: 439649

Source
    https://www.fmz.com/strategy/439649 (PineScript v2, FMZ last modified 2024-01-22 17:28:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-175), OscLen 10, MALen 20, bands 77 / 23; reverse off
    xOscAvg = sma(stoch(close, high, low, 10), 10);  xMAVal = sma(xOscAvg, 20);  LowestSoFar / HighestSoFar = running min / max of xOscAvg (start 9999999 / 0)
    nRes = (LowestSoFar + HighestSoFar) / 2 - (xMAVal - xOscAvg);  pos = nRes > 77 ? 1 : nRes < 23 ? -1 : previous

Interpretation choices (Pine rules in SURVEY_README.md)
    * The running lowest and highest values cover the data from its first bar (expanding, ending at the
      current bar), as written. The state is a level; the entry is sent on every bar of it and a
      same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a normalised stochastic.
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

NAME = "fmz_439649_hpotter_dynamo_oscillator_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "osc_len": [10, 14],
    "ma_len": [20, 30],
}
DEFAULT_PARAMS = {"osc_len": 10, "ma_len": 20, "hi_band": 77, "low_band": 23}


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
    n = int(p["osc_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        k = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    avg = k.rolling(n).mean()
    mav = avg.rolling(int(p["ma_len"])).mean()
    av, mv = avg.to_numpy(), mav.to_numpy()
    hb, lb = float(p["hi_band"]), float(p["low_band"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    lsf, hsf, pos = 9999999.0, 0.0, 0
    for i in range(m):
        if av[i] < lsf:
            lsf = av[i]
        if av[i] > hsf:
            hsf = av[i]
        res = (lsf + hsf) / 2 - (mv[i] - av[i])
        if res > hb:
            pos = 1
        elif res < lb:
            pos = -1
        tgt[i] = pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
