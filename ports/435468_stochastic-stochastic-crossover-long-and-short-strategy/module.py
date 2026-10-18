"""Stochastic crossover state, broker days: %K under %D with both over 70 holds a long, %K at or over %D with both under 20 a short
(reversing); otherwise the last side is kept; the "Trade reverse" input flips the side.
Port of FMZ strategy #435468 "基于Stochastic指标的长短交叉策略Stochastic-Crossover-Long-and-Short-Strategy" (Strategy Stochastic Crossover).

FMZ source id: 435468

Source
    https://www.fmz.com/strategy/435468 (PineScript v2, FMZ last modified 2023-12-15 10:29:29).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 166-181), stoch 7, %D SMA 3, overbought 70, oversold 20
    vFast = stoch(close, high, low, 7);  vSlow = sma(vFast, 3);  pos = vFast < vSlow and vFast > 70 and vSlow > 70 ? 1 : vFast >= vSlow and vFast < 20 and vSlow < 20 ? -1 : nz(pos[1], 0);  possig = reverse ? -pos : pos
    possig == 1 -> entry long;  possig == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the long state is the cross DOWN above 70 and the short state the cross UP below
      20 (a fade); the "Trade reverse" input gives the trend reading. The state holds until the
      other condition; strategy.entry reverses: REVERSAL INTENDED. The signal is sent on the change of
      state only. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic cross state.
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

NAME = "fmz_435468_stochastic_cross_state"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length": [7, 14],
}
DEFAULT_PARAMS = {"reverse": False, "length": 7, "d_len": 3, "oversold": 20, "overbought": 70}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    with np.errstate(invalid="ignore", divide="ignore"):
        vf = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    vs = vf.rolling(int(p["d_len"])).mean()
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    to_long = ((vf < vs) & (vf > ob) & (vs > ob)).to_numpy()
    to_short = ((vf >= vs) & (vf < os_) & (vs < os_)).to_numpy()
    m = len(to_long)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if to_long[i]:
            q = 1
        elif to_short[i]:
            q = -1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
