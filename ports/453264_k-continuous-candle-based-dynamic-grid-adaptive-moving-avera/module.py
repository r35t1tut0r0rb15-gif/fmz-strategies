"""Three rising closes, daily bars, long only: after three closes in a row each over the one before (up to the previous bar) it buys; three falling closes, or a low at or under 89 % of the previous close of the last signal, sells.
Port of FMZ strategy #453264 "基于连续K线动态网格自适应均线动态止损策略-Continuous-Candle-Based-Dynamic-Grid-Adaptive-Moving-Average-with-Dynamic-Stop-Loss-Strategy" (4 Candle Entry and Exit Strategy).

FMZ source id: 453264

Source
    https://www.fmz.com/strategy/453264 (PineScript v5, FMZ last modified 2024-06-03 16:16:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-122), 3 rising / falling closes (bars 1-4 back); stop 11 % under close[1] of the latest signal (a bar-close test on the low); quantity 1
    close[3] > close[4] and close[2] > close[3] and close[1] > close[2] -> stop = close[1] x 0.89, entry Long
    the falling mirror, or long and low <= stop -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a bar-close test on the bar's low, filled at the next open, not a stop order; its
      level is reset by every signal (also while long), as written. The tests use the bars before the
      current one only. A close on the signal bar itself finds no trade yet. Long only. The quantity 1
      is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is a close test on the low.
    2 generic: PASS, three-close runs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453264_three_rising_closes_low_test_stop_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [0.11, 0.05],
}
DEFAULT_PARAMS = {"stop_pct": 0.11}


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
    c, lo = bars_df["close"], bars_df["low"]
    c1, c2, c3, c4 = (c.shift(k) for k in (1, 2, 3, 4))
    up = ((c3 > c4) & (c2 > c3) & (c1 > c2)).to_numpy()
    dn = ((c3 < c4) & (c2 < c3) & (c1 < c2)).to_numpy()
    c1v, lv = c1.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = 1 - float(p["stop_pct"])
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, stop = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if up[i]:
            stop = c1v[i] * k
            if pos == 0:
                le[i], pend = True, 1
        if dn[i] or (pos == 1 and lv[i] <= stop):
            if pos == 1:
                lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
