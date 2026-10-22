"""Close crossing over its SMA 20 with a rising polynomial stop, daily bars, long only: the close crossing over the SMA goes long; the stop starts at the 20-bar low of the fill bar and rises by D x n^2 with
the bars held; the close falling through it closes.
Port of FMZ strategy #442646 "Polynomial Trailing Stop Strategy" (polynomic_stop).

FMZ source id: 442646

Source
    https://www.fmz.com/strategy/442646 (PineScript v4, FMZ last modified 2024-02-23 14:43:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-214), decrement D 0.1 (price units); degree 2; SMA 20; lowest low 20; 100 % of equity, capital 1000, commission 0.1
    first bar in a trade: stop = lowest(low, 20);  in a trade: num + 1;  flat: num = 0, stop = lowest(low, 20);  hl = stop + D x num^S
    close[1] < SMA[1] and close > SMA -> entry buy;  crossover(hl, close) -> close buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the step D = 0.1 is in price units; the port scales it to the stop as a fraction at
      the BTC reading of 42000 (D / 42000 = 2.38e-6 x the stop per n^S). The stop is set on the fill bar
      (strategy.opentrades turns 1) and the count runs from 1 on that bar; while flat the line is the
      20-bar low. The exit is a bar-close crossing filled at the next open. Long only. The 100 % of
      equity size, capital and commission are sizing. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit step -> fraction of the stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442646_sma20_cross_polynomial_rising_stop_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "degree": [2, 3],
    "d_frac": [2.38e-06, 2.38e-05],
}
DEFAULT_PARAMS = {"degree": 2, "d_frac": 2.38e-06, "ma": 20, "mn": 20}


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
    lo, c = bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["ma"])).mean()
    go = ((c.shift(1) < sma.shift(1)) & (c > sma)).to_numpy()
    mn = lo.rolling(int(p["mn"])).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    d, s = float(p["d_frac"]), float(p["degree"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, prev_held, stop, num = False, False, np.nan, 0
    hl_prev = np.nan
    for i in range(m):
        if held and not prev_held:
            stop = mn[i]
        if held:
            num += 1
        else:
            num, stop = 0, mn[i]
        hl = stop * (1 + d * num ** s)
        if go[i] and not held:
            le[i] = True
        elif held and hl > cv[i] and i > 0 and hl_prev <= cv[i - 1]:
            lx[i] = True
        hl_prev = hl
        prev_held = held
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
