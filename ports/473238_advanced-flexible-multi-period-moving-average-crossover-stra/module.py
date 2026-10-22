"""Weekly reviews against a weekly EMA 30, daily bars, long only: on the first bar of each broker week (and on the first bar of the data) a close at or over the last completed week's EMA 30 of weekly closes buys if flat, and a close under it sells.
Port of FMZ strategy #473238 "Advanced Flexible Multi Period Moving Average Crossover Strategy" (Flexible Moving Average Strategy).

FMZ source id: 473238

Source
    https://www.fmz.com/strategy/473238 (PineScript v5, FMZ last modified 2024-11-28 15:18:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-169), review "Weekly"; MA "EMA" 30 on request.security("W") (no lookahead); 100 % of equity; close_all on the last history bar
    first bar of a week (or the first bar): close < ma_W -> close Long (if long);  else -> entry Long (if flat)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The review bar is the first bar of each new broker week (time("W") changes), and the "period end"
      values it stores are that bar's own close and MA, as written. The "W" request without lookahead is
      read as the last completed broker week (Monday label, #437508), EMA 30 of the weekly closes. On
      the very first bar the MA is na, so the test falls to the buy branch, as written. The close_all on
      the last history bar is the end of the data and is not ported. Long only. The equity share is not
      ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, weekly close-vs-EMA reviews.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker week (Monday label) review bars.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473238_weekly_review_close_vs_weekly_ema30_long"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [30, 10],
}
DEFAULT_PARAMS = {"ma_length": 30}


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
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")         # the Monday of the broker week
    wk_close = c.groupby(week).last()
    w_ema = wk_close.ewm(span=int(p["ma_length"]), adjust=False).mean().shift(1)   # last completed week
    ma = w_ema.reindex(week).to_numpy()
    wk = np.asarray(week)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        review = i == 0 or wk[i] != wk[i - 1]
        if not review:
            continue
        if cv[i] < ma[i]:
            if pos == 1:
                lx[i], pos = True, 0
        elif pos == 0:
            le[i], pos = True, 1                 # an na MA falls to the buy branch, as written
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
