"""Bayesian move counts, broker days: over the last 30 bars the share of 7-bar moves above +0.3 % (and, in the conditional count, those
that followed an RSI-of-the-open jump) gives a probability; the probability crossing over its SMA 3 goes long, the mirror
probability for falls crossing under goes short (reversing).
Port of FMZ strategy #435763 "应用贝叶斯条件判断的RSI交易策略Bayesian-Condition-RSI-Trading-Strategy" (Stealthy7 Bayes Conditional RSI Trader Strategy).

FMZ source id: 435763

Source
    https://www.fmz.com/strategy/435763 (PineScript v2, FMZ last modified 2023-12-18 17:09:00).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 185-241), window 30, move 1.003, look range 7, RSI jump 8, smoothing 3, RSI 14 of the open
    counts over i = 1..30 of close[i] / close[i + 7] > t (and < 2 - t), and of the same with rsi(open, 14)[i + 8] > rsi[i + 9] + 8 (or < rsi[i + 9] - 8)
    bayes = up_b up2_b / (up_b up2_b + dn_b up3_b) 100;  longCondition = crossover(bayes, sma(bayes, 3));  shortCondition = crossunder(bayesS, sma(bayesS, 3))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loops count bars t-1 to t-30: a window of earlier bars only (the current bar is not in it).
      The conditional count uses the RSI of the OPEN price, as written. Each count starts at 1. A
      missing value counts in the "else" branch (Pine's comparisons with na are false). When both
      conditions fire on one bar the short (sent last) stands. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, move counts and an RSI jump.
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

NAME = "fmz_435763_bayes_conditional_rsi_moves"
FAMILY = "bayesian_counts"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p": [30, 20],
    "t": [1.003, 1.01],
}
DEFAULT_PARAMS = {"p": 30, "t": 1.003, "r": 7, "rsit": 8, "bayest": 3, "rsip": 14}


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


def _count(flag, p):
    """Number of true values of `flag` on bars t-1 .. t-p (rolling window ending one bar back)."""
    return flag.astype(float).rolling(p).sum().shift(1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    w, r, t = int(p["p"]), int(p["r"]), float(p["t"])
    n = int(p["rsip"])
    ch = o.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    q = c / c.shift(r)
    a_up, a_dn = q > t, q < 2 - t
    b_up = rsi.shift(r + 1) > rsi.shift(r + 2) + float(p["rsit"])
    b_dn = rsi.shift(r + 1) < rsi.shift(r + 2) - float(p["rsit"])
    with np.errstate(invalid="ignore", divide="ignore"):
        def bayes(a, b):
            up = 1 + _count(a, w)
            dn = 1 + w - _count(a, w)
            up2 = 1 + _count(a & b, w)
            up3 = 1 + w - _count(a & b, w)
            return (up / w) * (up2 / w) / ((up / w) * (up2 / w) + (dn / w) * (up3 / w)) * 100

        by, bs = bayes(a_up, b_up), bayes(a_dn, b_dn)
    k = int(p["bayest"])
    sn1, sn2 = by.rolling(k).mean(), bs.rolling(k).mean()
    le = ((by > sn1) & (by.shift(1) <= sn1.shift(1))).fillna(False).astype(bool)
    se = ((bs < sn2) & (bs.shift(1) >= sn2.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
