"""HPotter Fast and Slow Kurtosis, broker days: the change of the 3-bar momentum is smoothed by EMA 65
(FK) and a 3-bar WMA of that (FSK); both above 0 holds a long, otherwise a short (always in the market).
Port of FMZ strategy #427673 "Fast and Slow Kurtosis Trading Strategy".

FMZ source id: 427673

Source
    https://www.fmz.com/strategy/427673 (PineScript v2, FMZ last modified 2023-09-23 15:27:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 220-243), BuyZone 0
    xMOM_R = mom(mom(close, 3), 1); FK = ema(xMOM_R, 65); FSK = wma(FK, 3)
    pos = FK > 0 and FSK > 0 ? 1 : -1 -> entry long / entry short every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) is fixed off; BuyZone 0 fixed.
    * pos is -1 while the averages are na (iff false branch): the first valid bar can open short,
      as written (strategy.entry needs a price, so the first order is on the first bar with a close).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum of closes, zero level.
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

NAME = "fmz_427673_hpotter_fast_slow_kurtosis"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mom_len": [3, 5],
    "ema_len": [65, 30],
}
DEFAULT_PARAMS = {"mom_len": 3, "ema_len": 65, "wma_len": 3, "buy_zone": 0.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mom = c - c.shift(int(p["mom_len"]))
    x = mom - mom.shift(1)
    fk = x.ewm(span=int(p["ema_len"]), adjust=False).mean()
    fsk = _wma(fk, int(p["wma_len"]))
    z = p["buy_zone"]
    tgt = np.where((fk > z) & (fsk > z), 1, -1).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
