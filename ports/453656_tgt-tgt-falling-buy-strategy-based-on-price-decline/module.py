"""Buying 5 % down days, daily bars, long only: a close more than 5 % under the previous close buys; the first close over the fill price sells.
Port of FMZ strategy #453656 "TGT基于价格下跌买入策略-TGT-Falling-Buy-Strategy-Based-on-Price-Decline" (TGT Falling Buy).

FMZ source id: 453656

Source
    https://www.fmz.com/strategy/453656 (PineScript v5, FMZ last modified 2024-06-07 15:33:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-142), drop threshold 5 %; quantity balance / close (balance 1000)
    (close - close[1]) / close[1] x 100 < -5 -> entry Buy Trading (qty balance / close);  close > position_avg_price -> close Buy Trading

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit compares the close with the average (fill) price, which is na while flat: a sign-only
      test of the open trade, ported as the close against the fill bar's open (as #440336), checked
      from the fill bar on in a loop. A repeat signal while long is refused (pyramiding 1). The balance
      bookkeeping only sizes the next entry. The weekday flags are unused. Long only. The quantity is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the profit test against the fill price.
    2 generic: PASS, big-drop dip buying.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the balance-based quantity stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453656_five_pct_drop_buy_close_over_fill_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "drop_pct": [5.0, 3.0, 8.0],
}
DEFAULT_PARAMS = {"drop_pct": 5.0}


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
    go = ((c - c.shift(1)) / c.shift(1) * 100 < -float(p["drop_pct"])).to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos, avg = 1, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        if go[i] and pos == 0:
            le[i], pend = True, 1
        if pos == 1 and cv[i] > avg:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
