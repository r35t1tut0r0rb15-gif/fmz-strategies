"""Trend continuation factor (M.H. Pee), broker days: the 35-bar plus TCF above the minus TCF holds a long,
below it holds a short.
Port of FMZ strategy #428719 "Momentum Trend Continuation Factor Strategy" (Trend continuation factor).

FMZ source id: 428719

Source
    https://www.fmz.com/strategy/428719 (PineScript v2, FMZ last modified 2023-10-08 16:15:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 221-240), length 35, reverse false
    ch = mom(close,1); plus = max(ch,0); minus = max(-ch,0)
    plusCF = plus == 0 ? 0 : plus + plusCF[1] (nz 1); minusCF likewise
    plusTCF = sum(plus - minusCF, 35); minusTCF = sum(minus - plusCF, 35)
    pos = plusTCF > minusTCF ? 1 : plusTCF < minusTCF ? -1 : pos[1]; pos 1 -> entry long; -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both sums are in price units, but only their comparison is used: scale-free.
    * "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED; same-direction entries while in a position are
      ignored (pyramiding 0).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a comparison of two sums in the same units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428719_trend_continuation_factor"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [35, 20, 50],
}
DEFAULT_PARAMS = {"length": 35}


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
    ch = c.diff().to_numpy()
    plus = np.where(ch > 0, ch, 0.0)
    minus = np.where(ch < 0, -ch, 0.0)
    m = len(ch)
    pcf, mcf = np.zeros(m), np.zeros(m)
    for i in range(m):
        pcf[i] = 0.0 if plus[i] == 0 else plus[i] + (pcf[i - 1] if i >= 1 else 1.0)
        mcf[i] = 0.0 if minus[i] == 0 else minus[i] + (mcf[i - 1] if i >= 1 else 1.0)
    n = int(p["length"])
    pt = pd.Series(plus - mcf, index=c.index).rolling(n).sum().to_numpy()
    mt = pd.Series(minus - pcf, index=c.index).rolling(n).sum().to_numpy()
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if pt[i] > mt[i]:
            q = 1
        elif pt[i] < mt[i]:
            q = -1
        pos[i] = q
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(pos == 1, index=idx), false, pd.Series(pos == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
