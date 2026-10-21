"""EMA 25 / 100 crossings with trend re-entries, broker days: the fast EMA crossing over the slow one goes long, and so does a close crossing back over the fast EMA in an uptrend on a bar with a larger body than the
previous one and a close above the last entry signal's close; the mirror goes short; reversing.
Port of FMZ strategy #436787 "Momentum Indicator Crossover Strategy" (EMA Crossover).

FMZ source id: 436787

Source
    https://www.fmz.com/strategy/436787 (PineScript v5, FMZ last modified 2023-12-27 17:04:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 144-195), EMA 25 / 100 (EMA 200 and RSI 14 unused), source close
    up = crossover(ema1, ema2) or (crossover(close, ema1) and ema1 > ema2 and |close - open| > |close[1] - open[1]| and close > entrybar) -> entry Buy, entrybar := close
    down = crossunder(ema1, ema2) or (crossunder(close, ema1) and ema1 < ema2 and larger body and close < entrybar) -> entry Sell, entrybar := close  (var entrybar = first close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * entrybar is the close of the latest bar that sent an entry (also when the entry repeats the open
      side and is ignored), starting at the first bar's close; each bar's tests read it before that bar's
      update. EMA 200, the RSI and the position-size input are not used by the orders. ta.ema is seeded with
      the first value. A same-side entry while in the position is ignored (pyramiding 0). REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and body comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused position-size input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435154 (2 members, best partner #435154, Jaccard 0.719); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436787_ema_cross_body_reentry"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [25, 15],
    "len2": [100, 50],
}
DEFAULT_PARAMS = {"len1": 25, "len2": 100}


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
    o, c = bars_df["open"], bars_df["close"]
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    x_up = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).to_numpy()
    x_dn = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).to_numpy()
    body = (c - o).abs()
    bigger = (body > body.shift(1))
    re_up = ((c > e1) & (c.shift(1) <= e1.shift(1)) & (e1 > e2) & bigger).to_numpy()
    re_dn = ((c < e1) & (c.shift(1) >= e1.shift(1)) & (e1 < e2) & bigger).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    entrybar = cv[0] if m else np.nan
    for i in range(m):
        up = x_up[i] or (re_up[i] and cv[i] > entrybar)
        dn = x_dn[i] or (re_dn[i] and cv[i] < entrybar)
        if up:
            le[i] = True
            entrybar = cv[i]
        if dn:
            se[i] = True
            entrybar = cv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
