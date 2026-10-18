"""Range Filter flips, broker days: the close above a Donchian-like adaptive filter that has been rising, after the state was short, goes long; below a falling filter, after the state was long, goes
short (reversing). The Ichimoku, Parabolic SAR, pivot-pattern and MACD blocks are only drawn.
Port of FMZ strategy #436480 "Dynamic Filter Quant Trading Strategy" (5cel Scalp Strategy (Range Filter flips)).

FMZ source id: 436480

Source
    https://www.fmz.com/strategy/436480 (PineScript v5, FMZ last modified 2023-12-25 11:10:09).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 144-610), range filter sampling period 100, multiplier 3.0; all other blocks display only
    smrng = ema(ema(|x - x[1]|, 100), 199) 3;  filt = x > filt[1] ? max(filt[1], x - smrng) : min(filt[1], x + smrng)  (nz start 0);  upward / downward counters;  longCond = src > filt and upward > 0 (rising or falling bar);  CondIni keeps the last side
    longCondition = longCond and CondIni[1] == -1 -> close short, entry long;  shortCondition = shortCond and CondIni[1] == 1 -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders depend only on the Range Filter state flips (the entry flags use the position count, which
      only restates the reversal). The filter is the standard range filter (Donchian-style trailing of the
      price by the smoothed average range); it starts from zero, as written. The Heiken-Ashi security call
      and the table are not used by the orders. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range filter state flips.
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

NAME = "fmz_436480_range_filter_flips"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [100, 50],
    "mult": [3.0, 2.0],
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"]
    t = int(p["per"])
    avrng = src.diff().abs().ewm(span=t, adjust=False).mean()
    smrng = (avrng.ewm(span=t * 2 - 1, adjust=False).mean() * float(p["mult"])).to_numpy()
    x = src.to_numpy(dtype=float)
    m = len(x)
    filt = np.zeros(m)
    for i in range(m):
        prev = filt[i - 1] if i > 0 and not np.isnan(filt[i - 1]) else 0.0
        r = smrng[i]
        if x[i] > prev:
            filt[i] = prev if (x[i] - r) < prev else x[i] - r
        else:
            filt[i] = prev if (x[i] + r) > prev else x[i] + r
    upward = np.zeros(m)
    downward = np.zeros(m)
    for i in range(1, m):
        if filt[i] > filt[i - 1]:
            upward[i], downward[i] = upward[i - 1] + 1, 0
        elif filt[i] < filt[i - 1]:
            upward[i], downward[i] = 0, downward[i - 1] + 1
        else:
            upward[i], downward[i] = upward[i - 1], downward[i - 1]
    s1 = np.concatenate(([np.nan], x[:-1]))
    with np.errstate(invalid="ignore"):
        long_c = ((x > filt) & (x > s1) & (upward > 0)) | ((x > filt) & (x < s1) & (upward > 0))
        short_c = ((x < filt) & (x < s1) & (downward > 0)) | ((x < filt) & (x > s1) & (downward > 0))
    ini = np.zeros(m)
    q = 0.0
    for i in range(m):
        if long_c[i]:
            q = 1.0
        elif short_c[i]:
            q = -1.0
        ini[i] = q
    ini1 = np.concatenate(([0.0], ini[:-1]))
    long_x = long_c & (ini1 == -1)
    short_x = short_c & (ini1 == 1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(long_x, index=ix), false, pd.Series(short_x, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
