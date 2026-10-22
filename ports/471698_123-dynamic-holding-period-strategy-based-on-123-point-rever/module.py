""""123" lower-low reversal set-ups, daily bars, long only: a low under yesterday's, yesterday's under the low 3 days ago, the low 2 days ago under the low 4 days ago and the high 2 days ago under the high 3 days ago buys; 7 bars after the last set-up, or a close at or over the SMA 200, sells.
Port of FMZ strategy #471698 "基于123点位反转的动态持仓期策略-Dynamic-Holding-Period-Strategy-Based-on-123-Point-Reversal-Pattern" (123 Reversal Trading Strategy).

FMZ source id: 471698

Source
    https://www.fmz.com/strategy/471698 (PineScript v5, FMZ last modified 2024-11-12 15:15:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-210), conditions on low / low[1] / low[3], low[2] / low[4], high[2] / high[3]; hold 7 bars; SMA 200 exit (the comments say 20-day)
    low < low[1] and low[1] < low[3] and low[2] < low[4] and high[2] < high[3] -> entry Buy;  barssince(set-up) >= 7 or close >= sma200 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The holding count runs from the last set-up bar (a new set-up while held restarts it), as written.
      The entry is called before the close; the close acts only on a long held into the bar. The
      moving average is the SMA 200 (the input's default), though the comments call it 20-day. Long
      only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lower-low reversal set-ups with a timed exit.
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

NAME = "fmz_471698_123_lower_low_reversal_timed_or_sma200_exit_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "days_to_hold": [7, 3],
    "ma_len": [200, 20],
}
DEFAULT_PARAMS = {"days_to_hold": 7, "ma_len": 200}


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
    setup = ((lo < lo.shift(1)) & (lo.shift(1) < lo.shift(3)) & (lo.shift(2) < lo.shift(4))
             & (h.shift(2) < h.shift(3))).to_numpy()
    ma = c.rolling(int(p["ma_len"])).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    hold = int(p["days_to_hold"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, last = 0, None
    for i in range(m):
        if setup[i]:
            last = i
        since_ok = last is not None and i - last >= hold
        out = since_ok or cv[i] >= ma[i]
        if setup[i] and pos == 0:
            le[i], pos = True, 1
        elif out and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
