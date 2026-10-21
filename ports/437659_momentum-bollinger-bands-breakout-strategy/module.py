"""Lower-band crossings with an upper-band flat, broker days: the close crossing over the lower band (SMA 20 - 2 sigma) goes long, crossing back under it goes short (as written), reversing; the close crossing over
the upper band closes everything.
Port of FMZ strategy #437659 "Momentum Bollinger Bands Breakout Strategy" (Advanced Bollinger Bands Strategy).

FMZ source id: 437659

Source
    https://www.fmz.com/strategy/437659 (PineScript v4, FMZ last modified 2024-01-04 15:52:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 172-210), BB 20 x 2, MA filter 14 off, exit at basis off
    crossover(close, lower) -> entry BBandLE;  crossunder(close, lower) -> entry BBandSE (the short also tests the LOWER band, as written);  close_all on crossover(close, upper) or crossunder(close, lower)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, the short entry tests the lower band too (an intended upper-band version is owed). The
      close_all on a lower-band crossing under coincides with the short entry and only closes a long open
      at the bar's close (call order: entries first), so that bar leaves a short; a crossing over the upper
      band flattens. The OCA group and cancels act on market orders and change nothing. The MA filter and
      basis exit are off. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
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

NAME = "fmz_437659_lower_band_cross_upper_flat"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    lc = ((c > lo) & (c.shift(1) <= lo.shift(1))).to_numpy()
    sc = ((c < lo) & (c.shift(1) >= lo.shift(1))).to_numpy()
    xa = (((c > up) & (c.shift(1) <= up.shift(1))) | ((c < lo) & (c.shift(1) >= lo.shift(1)))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s, changed = pos, False
        if lc[i] and s != 1:
            s, changed = 1, True
        if sc[i] and s != -1:
            s, changed = -1, True
        if xa[i] and pos != 0 and not changed:
            s = 0
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
