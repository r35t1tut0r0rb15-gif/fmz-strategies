"""Breaks of the reversal bar of the 50-bar extreme, daily bars: a close under the low of the bar that made the 50-bar high goes short, a close above the high of the bar that made the 50-bar low goes long,
each once until a new extreme re-arms it; reversing.
Port of FMZ strategy #451076 "Multi Timeframe Reversal Confirmation Trading Strategy" (Reversal Confimation Strategy).

FMZ source id: 451076

Source
    https://www.fmz.com/strategy/451076 (PineScript v5, FMZ last modified 2024-05-11 17:38:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-139), lookback 50; EMA 50 (unused)
    high == highest(50) -> re-arm down;  dnRv = low of the oldest bar in the window whose high equals the 50-bar high;  close < dnRv and armed -> entry Sell, disarm
    low == lowest(50) -> re-arm up;  upRv = high of the oldest bar whose low equals the 50-bar low;  close > upRv and armed -> entry Buy, disarm

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loop over the window assigns at every match, so the level is the one from the oldest
      matching bar, as written. A level fires once and is re-armed when a bar makes a new extreme. The
      levels start at 0, so the very first bar's close above 0 goes long, as written.
      When both fire, the later long wins (as #437773). No exit: positions end at the opposite entry.
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, breaks of the extreme bar's opposite end.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451076_extreme_bar_reversal_break_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 20],
}
DEFAULT_PARAMS = {"lookback": 50}


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
    hv = bars_df["high"].to_numpy(dtype=float)
    lv = bars_df["low"].to_numpy(dtype=float)
    cv = bars_df["close"].to_numpy(dtype=float)
    n = int(p["lookback"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dn_rv = up_rv = 0.0
    dn_trig = up_trig = False
    for i in range(m):
        if i < n - 1:
            fh = fl = np.nan                     # ta.highest / ta.lowest are na before n bars (no match;
        else:                                    # the levels keep their 0 start, so the first bar goes long)
            fh, fl = hv[i - n + 1:i + 1].max(), lv[i - n + 1:i + 1].min()
        if hv[i] == fh:
            dn_trig = False
        if lv[i] == fl:
            up_trig = False
        for k in range(n):                       # i = 0 .. n-1 back; the last match (the oldest) wins
            j = i - k
            if j < 0:
                break
            if hv[j] == fh:
                dn_rv = lv[j]
            if lv[j] == fl:
                up_rv = hv[j]
        dn_sig = cv[i] < dn_rv and not dn_trig
        up_sig = cv[i] > up_rv and not up_trig
        if dn_sig:
            dn_trig = True
        if up_sig:
            up_trig = True
        se[i] = dn_sig and not up_sig
        le[i] = up_sig
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
