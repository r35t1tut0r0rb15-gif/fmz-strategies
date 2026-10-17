"""HPotter's reverse-engineered RSI, broker days: the price at which the Wilder RSI 14 would equal 50 is computed each bar;
when it is above the close the state turns short, below the close long; always in the state's direction.
Port of FMZ strategy #433569 "逆向工程RSI策略Reverse-Engineering-RSI-Strategy" (Reverse Engineering RSI, by Giorgos Siligardos).

FMZ source id: 433569

Source
    https://www.fmz.com/strategy/433569 (PineScript v2, FMZ last modified 2023-11-28 15:50:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-202), value 50, Wilder period 14, reverse false
    K = 2 / (2 x 14 - 1 + 1);  AUC / ADC = exponential averages of up / down closes (seeded with 1)
    nVal = 13 (ADC x 50 / 50 - AUC);  nRes = nVal >= 0 ? close + nVal : close + nVal x 50 / 50;  pos = nRes > close ? -1 : nRes < close ? 1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages start from 1 (nz(.., 1)), as written. The state holds when nRes equals the close.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the close against an RSI-derived price.
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

NAME = "fmz_433569_reverse_engineered_rsi"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "value": [50, 60],
    "wild_per": [14, 28],
}
DEFAULT_PARAMS = {"value": 50, "wild_per": 14}


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
    cv = bars_df["close"].to_numpy(dtype=float)
    val, wp = float(p["value"]), int(p["wild_per"])
    k = 2 / (2 * wp - 1 + 1)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    auc = adc = 1.0
    pos = 0
    for i in range(m):
        if i > 0 and cv[i] > cv[i - 1]:
            auc = k * (cv[i] - cv[i - 1]) + (1 - k) * auc
            adc = (1 - k) * adc
        elif i > 0:
            auc = (1 - k) * auc
            adc = k * (cv[i - 1] - cv[i]) + (1 - k) * adc
        else:
            auc, adc = (1 - k) * auc, (1 - k) * adc
        nv = (wp - 1) * (adc * val / (100 - val) - auc)
        nres = cv[i] + nv if nv >= 0 else cv[i] + nv * (100 - val) / val
        if nres > cv[i]:
            pos = -1
        elif nres < cv[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
