"""Closes crossing out of the Bollinger band (20, 2) with the CMO 14 beyond -50 / +50, closed at the middle band or
the opposite CMO extreme, two-day bars.
Port of FMZ strategy #482833 "基于动量振荡与布林带的高级量化策略系统-Advanced-Momentum-Oscillator-and-Bollinger-Bands-Quantitative-Strategy-System" (Chande Momentum Oscillator + Bollinger Bands Strategy).

FMZ source id: 482833

Source
    https://www.fmz.com/strategy/482833 (PineScript v5, FMZ last modified 2025-02-20 14:50:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-147), BB 20 / 2, CMO 14 (+50 / -50)
    crossunder(close, lower) and cmo < -50 -> entry long; crossover(close, upper) and cmo > 50 -> entry short
    crossover(close, basis) or cmo > 50 -> close long; crossunder(close, basis) or cmo < -50 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an entry
      on that bar (#430850). State machine: exits emitted only on going flat.
    * Pine's ta.stdev is the population deviation (ddof 0); ta.cmo uses plain sums of up and down changes.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. Two-day bars are blocks of broker-day dates from
      1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and the CMO.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482833_bb_cmo_extreme_reentry_2d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 1.5],
    "cmo_level": [50.0, 40.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "cmo_len": 14, "cmo_level": 50.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def _cmo(c, n):
    d = c.diff()
    sm1 = d.clip(lower=0).rolling(n).sum()
    sm2 = (-d).clip(lower=0).rolling(n).sum()
    return 100 * (sm1 - sm2) / (sm1 + sm2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    cmo = _cmo(c, int(p["cmo_len"]))
    lvl = p["cmo_level"]

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    buy = (xover(lower, c) & (cmo < -lvl)).to_numpy()
    sell = (xover(c, upper) & (cmo > lvl)).to_numpy()
    xl = (xover(c, basis) | (cmo > lvl)).to_numpy()
    xs = (xover(basis, c) | (cmo < -lvl)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and pos != -1:
            se[i], pos = True, -1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
