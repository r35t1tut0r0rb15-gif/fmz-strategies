"""Broker days: each time the volume oscillator (EMA 5 against EMA 10 of volume, in percent) crosses zero, the strategy goes long if the previous positive swing's peak was no larger than the previous negative swing's depth, otherwise short; reversing.
Port of FMZ strategy #435091 "Volume Oscillator Long and Short Term Moving Average Crossover Strategy" (SB_Volume_oscillator_Prev_high_low).

FMZ source id: 435091

Source
    https://www.fmz.com/strategy/435091 (PineScript v3, FMZ last modified 2023-12-12 11:19:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-232), EMA 5 / 10 of volume; zero 0; swing peaks tracked from the crossings
    osc = 100 x (ema(v, 5) - ema(v, 10)) / ema(v, 10);  crossover(osc, 0): high_val := osc, where := 1, prev_low_val := low_val, low_val := osc;  crossunder mirror (prev_high_val := high_val)
    where 1: high_val := max(high_val, osc);  where -1: low_val := min(low_val, osc);  on either crossing: prev_high_val <= abs(prev_low_val) ? entry long : entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing bookkeeping runs as written, before the entries on the same bar; the inputs start every
      level at 0. Both crossings use the same test, so the direction comes only from the last completed
      swings' sizes. The oscillator is a ratio of volume EMAs, so the volume's units cancel. REVERSAL
      INTENDED. 100 % of equity is sizing. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume oscillator swing comparison at zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume oscillator (EMA 5 / 10 of volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435091_volume_oscillator_swing_size_zero_cross_reversal"
FAMILY = "volume_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "shortlen": [5, 10],
    "longlen": [10, 20],
}
DEFAULT_PARAMS = {"shortlen": 5, "longlen": 10}


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
    v = bars_df["volume"]
    s = v.ewm(span=int(p["shortlen"]), adjust=False).mean()
    lg = v.ewm(span=int(p["longlen"]), adjust=False).mean()
    osc = 100 * (s - lg) / lg.where(lg != 0)
    co = ((osc > 0) & (osc.shift(1) <= 0)).to_numpy()
    cu = ((osc < 0) & (osc.shift(1) >= 0)).to_numpy()
    ov = osc.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    where = 0
    lo_v = hi_v = p_hi = p_lo = 0.0
    for i in range(m):
        if co[i]:
            hi_v, where, p_lo, lo_v = ov[i], 1, lo_v, ov[i]
        if cu[i]:
            lo_v, where, p_hi, hi_v = ov[i], -1, hi_v, ov[i]
        if where == 1 and hi_v < ov[i]:
            hi_v = ov[i]
        if where == -1 and lo_v > ov[i]:
            lo_v = ov[i]
        if co[i] or cu[i]:
            if p_hi <= abs(p_lo):
                le[i] = True
            else:
                se[i] = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
