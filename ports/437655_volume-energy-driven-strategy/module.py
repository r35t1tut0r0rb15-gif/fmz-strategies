"""Broker days: the first bar of a "bull zone" (the VWMA 11 of the bar's bullish volume share above the bearish one by more than the 15 % flat filter) goes long and closes a short; the first bar of a "bear zone" goes short and closes a long; reversing.
Port of FMZ strategy #437655 "Volume Energy Driven Strategy" (Volume fight strategy (Shuttle_Club)).

FMZ source id: 437655

Source
    https://www.fmz.com/strategy/437655 (PineScript v5, FMZ last modified 2024-01-04 15:38:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 127-168), direction ANY; search range 11; flat smoothing 15 %
    bull_vol = open < close ? volume : volume x (high - open) / (high - low);  bear_vol = open > close ? volume : volume x (open - low) / (high - low);  avg_* = vwma(*_vol, 11)
    bull = avg_bull > avg_bear and (avg_bull + avg_bear) / 2 / avg_bull < 0.85;  up counts bull bars (reset by bear);  bull and up == 1 -> close Short, entry Long;  bear mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume shares and their VWMAs are compared as ratios, so the units cancel. A doji's split
      divides by a zero range and gives no value for that window, as written. The closes come before the
      entries; with direction ANY the entry reverses anyway. "Show each setup in zone" is off. REVERSAL
      INTENDED. 10000 cash per trade is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bullish / bearish volume share zones.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10000 cash per trade, capital 10000, commission 0.04 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) split into bullish / bearish shares and their VWMAs; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437655_bull_bear_volume_share_zone_start_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma": [11, 20],
    "delta": [15.0, 10.0],
}
DEFAULT_PARAMS = {"ma": 11, "delta": 15.0}


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


def _vwma(x, v, n):
    s = v.rolling(n).sum()
    return (x * v).rolling(n).sum() / s.where(s != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    rng = (h - lo).where(h != lo)
    bull_v = pd.Series(np.where(o < c, v, v * (h - o) / rng), index=c.index)
    bear_v = pd.Series(np.where(o > c, v, v * (o - lo) / rng), index=c.index)
    n = int(p["ma"])
    ab, ar = _vwma(bull_v, v, n), _vwma(bear_v, v, n)
    flat = (ab + ar).abs() / 2
    k = 1 - float(p["delta"]) / 100
    bull = ((ab > ar) & (flat / ab < k)).to_numpy()
    bear = ((ab < ar) & (flat / ar < k)).to_numpy()
    m = len(bull)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    up = dn = 0
    for i in range(m):
        if bull[i]:
            up, dn = up + 1, 0
        if bear[i]:
            dn, up = dn + 1, 0
        le[i] = bull[i] and up == 1
        se[i] = bear[i] and dn == 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se & ~le, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
