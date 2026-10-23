"""Broker days: the finite volume element line (volume signed by whether close - hl2 + the hlc3 change exceeds 0.3 % of the close, over its SMA 22, accumulated) rising above both of its last two values goes long, falling below both goes short (the last state kept otherwise); reversing.
Port of FMZ strategy #440552 "Bilateral Three Point Moving Average Quantitative Trading Strategy" (Finite Volume Elements (FVE) Backtest (HPotter)).

FMZ source id: 440552

Source
    https://www.fmz.com/strategy/440552 (PineScript v2, FMZ last modified 2024-01-31 16:11:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-191), period 22; factor 0.3; reverse off
    nMF = close - hl2 + hlc3 - hlc3[1];  nVlm = nMF > 0.3 x close / 100 ? volume : nMF < -0.3 x close / 100 ? -volume : 0;  nRes = nz(nRes[1]) + nVlm / sma(volume, 22) / 22 x 100
    pos = nRes > nRes[1] and nRes > nRes[2] ? 1 : nRes < nRes[1] and nRes < nRes[2] ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The accumulation is undefined until the volume SMA exists and then starts from 0 (nz). Entries
      repeat every bar of a state and add nothing while in it. reverse is off. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, finite-volume-element direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the signed volume over its SMA 22 in the FVE line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440552_finite_volume_elements_direction_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [22, 50],
    "factor": [0.3, 0.1],
}
DEFAULT_PARAMS = {"period": 22, "factor": 0.3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["period"])
    hl2, hlc3 = (h + lo) / 2, (h + lo + c) / 3
    mf = c - hl2 + hlc3 - hlc3.shift(1)
    cut = float(p["factor"]) * c / 100
    vlm = pd.Series(np.where(mf > cut, v, np.where(mf < -cut, -v, 0.0)), index=c.index).where(mf.notna())
    sv = v.rolling(n).mean()
    term = (vlm / sv.where(sv != 0) / n * 100).to_numpy(dtype=float)
    m = len(term)
    res = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        base = 0.0 if np.isnan(prev) else prev
        res[i] = base + term[i]
        prev = res[i]
    r = pd.Series(res, index=c.index)
    raw = np.where((r > r.shift(1)) & (r > r.shift(2)), 1, np.where((r < r.shift(1)) & (r < r.shift(2)), -1, 0))
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if raw[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif raw[i] == -1 and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
