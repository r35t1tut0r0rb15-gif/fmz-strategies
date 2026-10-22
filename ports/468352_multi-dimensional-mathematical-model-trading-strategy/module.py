"""Up days with the 14-bar regression end over the EMA 50, daily bars, long only: a close over the previous close with the linear-regression value over the EMA 50 buys; a close under the previous close with the regression at or under the EMA sells.
Port of FMZ strategy #468352 "Multi Dimensional Mathematical Model Trading Strategy" (Advanced Math Strategy).

FMZ source id: 468352

Source
    https://www.fmz.com/strategy/468352 (PineScript v5, FMZ last modified 2024-09-26 17:36:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-176), ROC 1; linreg(close, 14, 0); EMA 50; sigmoid of the 1-bar change (> 0.5 exactly when the change is positive)
    roc > 0 and linreg > ema50 and sigmoid(close - close[1]) > 0.5 -> entry Buy;  roc <= 0 and linreg <= ema50 and sigmoid(...) < 0.5 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sigmoid of the price change is over 0.5 exactly when the change is positive and under 0.5
      when it is negative, so it repeats the ROC sign test; derivativeSignal is -1 for a zero change, but
      the sigmoid test then fails (it equals 0.5). The entry and exit tests cannot hold on the same bar.
      Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, up / down days with a regression-vs-EMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468352_up_day_linreg14_over_ema50_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reg_len": [14, 30],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"reg_len": 14, "ema_len": 50}


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


def _linreg_end(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(a.mean() + np.dot(w, a) / sxx * (n - 1) / 2.0), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ch = c - c.shift(1)
    lr = _linreg_end(c, p["reg_len"])
    lp = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (ch > 0) & (lr > lp)
    lx = (ch < 0) & ~(lr > lp)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
