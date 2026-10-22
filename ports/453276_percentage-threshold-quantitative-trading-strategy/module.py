"""Range breaks of the previous close by 1.04 %, daily bars: a high over the previous close plus 1.04 % goes long, a low under it minus 1.04 % goes short; reversing (a bar doing both ends short).
Port of FMZ strategy #453276 "Percentage Threshold Quantitative Trading Strategy" (GBS Percentage).

FMZ source id: 453276

Source
    https://www.fmz.com/strategy/453276 (PineScript v5, FMZ last modified 2024-06-03 16:41:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 80-120), threshold 1.04 % of close[1]; timeframe 'D' (the chart's own)
    high > close[1] x 1.0104 -> entry Buy;  low < close[1] x 0.9896 -> entry Sell;  the sell condition closes Buy, the buy condition closes Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security on 'D' on the daily header chart returns the chart's own values. The calls run
      in source order: entries first (an entry on the held side ignored, the later call winning a
      same-bar tie, as #437773), then the closes, which act only on the trade held into the bar when
      no earlier call reversed it. A bar breaking both ways therefore ends short (from flat or long)
      or flat (from short). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, previous-close range breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND453276 (2 members, best partner #453281, Jaccard 0.676); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453276_prev_close_pct_range_break_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pct": [1.04, 2.0, 0.5],
}
DEFAULT_PARAMS = {"pct": 1.04}


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
    k = float(p["pct"]) / 100
    c1 = c.shift(1)
    buy = (h > c1 * (1 + k)).to_numpy()
    sell = (lo < c1 * (1 - k)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if buy[i] and cur != 1:
            cur = 1
        if sell[i] and cur != -1:
            cur = -1
        if sell[i] and pos == 1 and cur == 1:
            cur = 0
        if buy[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
