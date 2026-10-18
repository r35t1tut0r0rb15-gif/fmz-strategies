"""Stochastic cross with a Vortex filter, broker days, long only with no exit: %K crossing over %D while the Vortex +VI is over -VI buys; the script has no exit, so the long is held.
Port of FMZ strategy #436123 "Stochastic Vortex Strategy" (Stochastic and Vortex Strategy).

FMZ source id: 436123

Source
    https://www.fmz.com/strategy/436123 (PineScript v4, FMZ last modified 2023-12-21 15:12:37).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 165-183), stochastic 14 / 3 / 3; Vortex 14
    k = sma(stoch(close, high, low, 14), 3);  d = sma(k, 3);  viPlus = sum(|high - low[1]|, 14) / sum(tr, 14);  viMinus = sum(|low - high[1]|, 14) / sum(tr, 14)
    buyCondition = crossover(k, d) and viPlus > viMinus -> entry long   (no exit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * No exit exists in the script, so the first long is held to the end of the data, as written (the
      intended version with an exit is owed). Long only. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic cross and the Vortex index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436123_stochastic_vortex_entry_hold"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_period": [14, 21],
    "length_vi": [14, 21],
}
DEFAULT_PARAMS = {"k_period": 14, "d_period": 3, "slowing": 3, "length_vi": 14}


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
    n = int(p["k_period"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    k = raw.rolling(int(p["slowing"])).mean()
    d = k.rolling(int(p["d_period"])).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = (h - lo).iloc[0]
    L = int(p["length_vi"])
    vm_plus, vm_minus = (h - lo.shift(1)).abs(), (lo - h.shift(1)).abs()
    with np.errstate(invalid="ignore", divide="ignore"):
        vi_plus = vm_plus.rolling(L).sum() / tr.rolling(L).sum()
        vi_minus = vm_minus.rolling(L).sum() / tr.rolling(L).sum()
    le = ((k > d) & (k.shift(1) <= d.shift(1)) & (vi_plus > vi_minus)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
