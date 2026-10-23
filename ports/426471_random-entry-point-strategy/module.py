"""A "random" entry taken from the day's volume (volume mod 6 under 3), broker days, long only: when flat, such a day buys at its close; the long closes when the close is more than 5 % under or 15 % over that signal close.
Port of FMZ strategy #426471 "Random Entry Point Strategy" (Random entry points).

FMZ source id: 426471

Source
    https://www.fmz.com/strategy/426471 (PineScript v4, FMZ last modified 2023-09-12 14:11:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-119), random integer 6 (volume % 6 < 3); stop -5 %, target +15 % of the signal close (close tests); strategy() commented out
    random = volume % 6;  random < 3 and not in_deal -> in_deal, start_price = close, entry long
    profit = (close / start_price - 1) x 100;  profit < -5 or profit > 15 -> close long, in_deal = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "random" draw is the bar's volume modulo 6, as written: with broker tick volume summed per
      broker day it is a pseudo-random filter, not the exchange's draw (weird case). The tests use the
      close against the signal close; the close fills at the next open, and a new entry can be signalled
      on the bar after a close. Long only. strategy() is commented out; the cash size (500) is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target / stop.
    2 generic: PASS, volume-parity entry with a fixed close-based target / stop (a random-entry benchmark).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash 500 (commented strategy()) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the entry draw volume % 6 < 3; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426471_volume_mod6_random_entry_long_close_bracket"
FAMILY = "random_benchmark"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "i": [6, 10],
    "take_profit": [15.0, 8.0],
}
DEFAULT_PARAMS = {"i": 6, "take_profit": 15.0, "stop_loss": -5.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    k = int(p["i"])
    draw = ((v % k) < (k / 2)).to_numpy()
    cv = c.to_numpy(dtype=float)
    sl, tp = float(p["stop_loss"]), float(p["take_profit"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_deal, start = False, np.nan
    for i in range(m):
        profit = 0.0
        if draw[i] and not in_deal:
            in_deal, start = True, cv[i]
            le[i] = True
        if in_deal:
            profit = (cv[i] / start - 1) * 100
        if profit < sl or profit > tp:
            lx[i] = True
            in_deal = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
