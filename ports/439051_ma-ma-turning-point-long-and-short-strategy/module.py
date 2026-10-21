"""SMA 25 turning points, broker days: the one-bar rate of change of the SMA 25 crossing over +0.025 % after a down state goes long, crossing under -0.025 % after an up state goes short; reversing.
Port of FMZ strategy #439051 "基于MA转折点的长短策略MA-Turning-Point-Long-and-Short-Strategy" (MA Turning Point Strategy).

FMZ source id: 439051

Source
    https://www.fmz.com/strategy/439051 (PineScript v3, FMZ last modified 2024-01-17 11:56:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 161-203), source close (chart resolution); SMA 25; lookback 1; minimum slope 2.5 x 0.01 (percent units)
    roc1 = roc(sma(close, 25), 1);  crossover(roc1, 0.025) -> up := true, down := false;  crossunder(roc1, -0.025) -> up := false, down := true;  up and down[1] -> entry Long;  down and up[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security() call uses the chart's own resolution, so it is the chart's close. roc is in percent,
      so the threshold 2.5 x 0.01 is 0.025 %, as written. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA rate-of-change turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430020 (4 members, best partner #430020, Jaccard 0.708); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439051_sma25_turning_point"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [25, 50],
    "trend_strength": [2.5, 10.0],
}
DEFAULT_PARAMS = {"ma1": 25, "trend_strength": 2.5, "lookback1": 1}


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
    ma = c.rolling(int(p["ma1"])).mean()
    k = int(p["lookback1"])
    roc = 100 * (ma - ma.shift(k)) / ma.shift(k)
    t = float(p["trend_strength"]) * 0.01
    xo = ((roc > t) & (roc.shift(1) <= t)).to_numpy()
    xu = ((roc < -t) & (roc.shift(1) >= -t)).to_numpy()
    m = len(c)
    up, dn = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    u = d = False
    for i in range(m):
        if xo[i]:
            u, d = True, False
        if xu[i]:
            u, d = False, True
        up[i], dn[i] = u, d
    upp = np.concatenate(([False], up[:-1]))
    dnp = np.concatenate(([False], dn[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up & dnp, index=ix), false, pd.Series(dn & upp, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
