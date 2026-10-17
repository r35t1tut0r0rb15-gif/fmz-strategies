"""DAKELAX asymmetric Bollinger fade, broker days, long only: a close under the SMA 20 - 2.2 sd band buys; a close over the
SMA 20 + 1.5 sd band closes everything. Adds are not ported.
Port of FMZ strategy #430877 "DAKELAX-XRPUSDT-波尔带回归均线策略DAKELAX-XRPUSDT-Bollinger-Band-Mean-Reversion-Strategy" (Tradebotler DAKELAX Binance:XRPUSDT Strategy).

FMZ source id: 430877

Source
    https://www.fmz.com/strategy/430877 (PineScript v3, FMZ last modified 2023-11-02 16:18:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-199), SMA 20, lower 2.2 sd, upper 1.5 sd, buyAmount 20
    lower_BB = sma(close, 20) - 2.2 stdev;  upper_BB = sma(close, 20) + 1.5 stdev
    close < lower_BB -> strategy.order('Buy', long, 20)  (adds 20 units on every such bar)
    close > upper_BB -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order adds 20 units on every bar below the band; the first opens the long, later
      ones add and are not ported (one net position; the exit closes all of it, so the position is
      not a running sum of buys and sells as in #426364). The EMA 7 / 18 alerts and the contraction
      colours are plot-only.
    * stdev is the population deviation. Buy and exit cannot meet on one bar. Long only; Opposite
      entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (Binance:XRPUSDT in the title and the pair in the header only; the rule reads the chart's own closes).
    4 signals only: 20 units per order stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430877_asymmetric_bb_fade_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "lower_mult": [2.2, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "lower_mult": 2.2, "upper_mult": 1.5}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    buy = (c < basis - p["lower_mult"] * sd).to_numpy()
    out = (c > basis + p["upper_mult"] * sd).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif out[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
