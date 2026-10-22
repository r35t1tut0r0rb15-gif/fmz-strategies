"""DonovanWall's Range Filter (period 20, multiplier 3.5), daily bars: the first close above a rising filter after a short signal goes long, the first close below a falling filter after a long signal goes
short; reversing (the stop / take prices are computed but never sent).
Port of FMZ strategy #444034 "Range Filter Buy Sell Signals Strategy" ([Doan]_RF-B&S Signals (Range Filter - B&S Signals)).

FMZ source id: 444034

Source
    https://www.fmz.com/strategy/444034 (PineScript v5, FMZ last modified 2024-03-08 17:06:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-258), swing source close; period 20; multiplier 3.5; EMA 200 (plot only); stop / take 1 % (unused)
    rng = ema(ema(|x - x[1]|, 20), 39) x 3.5;  filt steps toward x -+ rng only when x moves beyond it;  fdir = sign of the filter's change (kept)
    longCond = x > filt and upward;  shortCond = x < filt and downward;  CondIni latches the last side;  longCondition = longCond and CondIni[1] == -1 -> entry Long;  shortCondition mirrored -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and take prices are computed from the average price but no exit is ever sent, so
      positions end at the opposite entry. The EMA only plots. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range-filter direction changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG444034 (2 members, best partner #435516, Jaccard 0.816); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444034_range_filter_direction_flip_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rng_per": [20, 50],
    "rng_qty": [3.5, 2.0],
}
DEFAULT_PARAMS = {"rng_per": 20, "rng_qty": 3.5}


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
    x = bars_df["close"]
    n = int(p["rng_per"])
    avrng = (x - x.shift(1)).abs().ewm(span=n, adjust=False, ignore_na=True).mean()
    rng = (avrng.ewm(span=n * 2 - 1, adjust=False, ignore_na=True).mean() * float(p["rng_qty"])).to_numpy()
    xv = x.to_numpy(dtype=float)
    m = len(xv)
    filt = np.full(m, np.nan)
    f = xv[0] if m else np.nan
    for i in range(m):
        prev = f
        if not np.isnan(rng[i]):
            if xv[i] - rng[i] > prev:
                f = xv[i] - rng[i]
            if xv[i] + rng[i] < prev:
                f = xv[i] + rng[i]
        filt[i] = f
    fdir = np.zeros(m)
    d = 0.0
    for i in range(1, m):
        if filt[i] > filt[i - 1]:
            d = 1.0
        elif filt[i] < filt[i - 1]:
            d = -1.0
        fdir[i] = d
    x1 = np.concatenate(([np.nan], xv[:-1]))
    with np.errstate(invalid="ignore"):
        lc = (xv > filt) & (fdir == 1) & ((xv > x1) | (xv < x1))
        sc = (xv < filt) & (fdir == -1) & ((xv < x1) | (xv > x1))
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ci = 0
    for i in range(m):
        prev = ci
        if lc[i]:
            ci = 1
        elif sc[i]:
            ci = -1
        le[i] = lc[i] and prev == -1
        se[i] = sc[i] and prev == 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
