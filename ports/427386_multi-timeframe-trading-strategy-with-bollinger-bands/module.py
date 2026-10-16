"""Underworld Hunter, broker days: a close above the upper band (triple-EMA 75 +- 1.9 stdev 75) goes
long from flat, a close below the lower band goes short from flat; three closes in a row back inside
the band close the position.
Port of FMZ strategy #427386 "Multi-timeframe Trading Strategy with Bollinger Bands".

FMZ source id: 427386

Source
    https://www.fmz.com/strategy/427386 (PineScript v4, FMZ last modified 2023-09-20 15:47:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 162-238), length 75, deviation 1.9, mean-reversion test off
    basis = na(basis[1]) ? sma(close, 75) : ema(ema(ema(close, 75), 75), 75)
    upper / lower = basis +- 1.9 stdev(close, 75)
    close > upper and no open trade -> long ("Hunt Up"); three closes < upper -> close long
    close < lower and no open trade -> short ("Hunt Down"); three closes > lower -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * basis is the SMA on the first bar it exists and the nested EMA of EMA of EMA from the next bar
      on, as written. stdev is the population standard deviation. The CCI only colours bars.
    * The "Sneak" (mean-reversion) branch is off by default (mean false): not ported.
    * Entries only from flat (opentrades == 0): Opposite entries cannot occur. The order size
      floor(50000 / close) is sizing.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands in standard deviations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the order size stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427386_underworld_hunter_bands"
FAMILY = "bollinger_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [75, 40, 150],
    "mult": [1.9, 2.5],
}
DEFAULT_PARAMS = {"length": 75, "mult": 1.9}


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
    n = int(p["length"])
    c = bars_df["close"]
    sma = c.rolling(n).mean().to_numpy()
    e3 = c.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean().to_numpy()
    m = len(c)
    basis = np.full(m, np.nan)
    for i in range(m):
        basis[i] = sma[i] if (i == 0 or np.isnan(basis[i - 1])) else e3[i]
    dev = p["mult"] * c.rolling(n).std(ddof=0).to_numpy()
    upper, lower = basis + dev, basis - dev
    cv = c.to_numpy(dtype=float)
    below_u = cv < upper
    above_l = cv > lower
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        three_in_u = i >= 2 and below_u[i] and below_u[i - 1] and below_u[i - 2]
        three_in_l = i >= 2 and above_l[i] and above_l[i - 1] and above_l[i - 2]
        if pos == 1 and three_in_u:
            lx[i], pos = True, 0
        elif pos == -1 and three_in_l:
            sx[i], pos = True, 0
        elif pos == 0 and cv[i] > upper[i]:
            le[i], pos = True, 1
        elif pos == 0 and cv[i] < lower[i]:
            se[i], pos = True, -1
    idx = bars_df.index
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def portfolio_kwargs(**params):
    return {}
