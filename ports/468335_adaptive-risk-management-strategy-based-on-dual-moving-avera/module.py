"""SMA 50 / 200 golden crosses, daily bars, long only: the cross up with the close over 98.5 % of the SMA 200 buys; a close under the SMA 200 sells.
Port of FMZ strategy #468335 "Adaptive Risk Management Strategy Based on Dual Moving Average Golden Cross" (Golden Cross with 1.5% Stop-Loss & MA Exit).

FMZ source id: 468335

Source
    https://www.fmz.com/strategy/468335 (PineScript v5, FMZ last modified 2024-09-26 16:17:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-149), SMA 50 / 200; "stop" = SMA 200 x 0.985 used only for the size (no stop order); size = 2.5 % of equity / stop distance
    crossover(sma50, sma200) and close - sma200 x 0.985 > 0 -> entry Long (qty = risk / distance);  close < sma200 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1.5 % level only sizes the trade; no stop order is sent. The entry is called before the close;
      the close acts only on a long held into the bar. The risk-based quantity is not ported (sizing is
      the optimisation layer's). Long only. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, golden crosses with an SMA 200 exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity-risk quantity stored, not ported.
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

NAME = "fmz_468335_golden_cross_sma200_close_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    a, b = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    buy = ((a > b) & (a.shift(1) <= b.shift(1)) & (c - b * 0.985 > 0)).to_numpy()
    sell = (c < b).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif sell[i] and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
