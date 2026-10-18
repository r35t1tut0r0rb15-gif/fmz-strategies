"""Zero-lag EMA against a zero-lag RMA, broker days: the zero-lag RMA (14) under the zero-lag EMA (14) the bar before holds a long, over it a short (reversing).
Port of FMZ strategy #436102 "Dual Moving Average Trend Tracking Strategy" (Kitaec Strategy4).

FMZ source id: 436102

Source
    https://www.fmz.com/strategy/436102 (PineScript v3, FMZ last modified 2023-12-21 11:45:35).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 189-287), smoothing 14 / 14; the ADX, VWMA and 550-bar series are computed and unused
    zlema = ema1 + (ema1 - ema2) with ema1 = ema(close, 14), ema2 = ema(ema1, 14);  zlrmax = rma1 + (rma1 - rma2) likewise;  zlrmax[1] < zlema[1] -> entry long;  zlrmax[1] > zlema[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states re-sent every bar; the signal is sent on the change of state only
      (vbt ignores a same-side signal). The second zero-lag pair and the ADX / VWMA / 550-bar series
      are not used by the orders. The equity-based lot is sizing. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot, capital percent and pyramiding inputs stored.
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

NAME = "fmz_436102_zero_lag_ema_rma_state"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 21],
    "len2": [14, 21],
}
DEFAULT_PARAMS = {"len": 14, "len2": 14}


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
    n1, n2 = int(p["len"]), int(p["len2"])
    ema1 = c.ewm(span=n1, adjust=False).mean()
    ema2 = ema1.ewm(span=n2, adjust=False).mean()
    zlema = ema1 + (ema1 - ema2)
    rma1 = c.ewm(alpha=1 / n1, adjust=False).mean()
    rma2 = rma1.ewm(alpha=1 / n2, adjust=False).mean()
    zlrmax = rma1 + (rma1 - rma2)
    up = (zlrmax.shift(1) < zlema.shift(1)).to_numpy()
    dn = (zlrmax.shift(1) > zlema.shift(1)).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
