"""HPotter's volatility FVE colouring: the bar's money-flow move (close - hl2 + hlc3 change) above a volatility cutoff (0.1 x the 22-bar sd of the log range + 0.1 x the sd of the log hlc3 change, times the close) goes long, below minus the cutoff goes short; broker days, reversing.
Port of FMZ strategy #435887 "Volatility Finite Volume Elements Strategy" (Volatility Finite Volume Elements Strategy (HPotter)).

FMZ source id: 435887

Source
    https://www.fmz.com/strategy/435887 (PineScript v2, FMZ last modified 2023-12-19 15:23:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 111-144), Samples 22; AvgLength 50 (volume MA, plot only); Cintra 0.1, Cinter 0.1; reverse off
    CutOff = 0.1 stdev(log(high) - log(low), 22) + 0.1 stdev(log(hlc3) - log(hlc3[1]), 22);  MF = close - hl2 + hlc3 - hlc3[1]
    pos = MF > CutOff x close ? 1 : MF < -CutOff x close ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Volume is only plotted (the coloured volume bars and their SMA 50): the signal uses price only, so
      volume is not used. stdev is the population form (Pine v2). reverse is off. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, money-flow move against a volatility cutoff.
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

NAME = "fmz_435887_money_flow_move_volatility_cutoff_state_reversal"
FAMILY = "volatility_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "samples": [22, 50],
    "cintra": [0.1, 0.2],
}
DEFAULT_PARAMS = {"samples": 22, "cintra": 0.1, "cinter": 0.1}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["samples"])
    hlc3 = (h + lo + c) / 3
    intra = np.log(h) - np.log(lo)
    inter = np.log(hlc3) - np.log(hlc3.shift(1))
    cut = float(p["cintra"]) * intra.rolling(n).std(ddof=0) + float(p["cinter"]) * inter.rolling(n).std(ddof=0)
    mf = c - (h + lo) / 2 + hlc3 - hlc3.shift(1)
    raw = np.where(mf > cut * c, 1, np.where(mf < -cut * c, -1, 0))
    m = len(raw)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prv = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prv != 1), index=ix), false,
            pd.Series((pos == -1) & (prv != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
