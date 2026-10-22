"""A "DCA" long with a close-based trailing take-profit, daily bars, long only: the first bar goes long; each 1 % drop under the last buy close is a further buy (refused at the default pyramiding, but it
resets the reference); once the close is 0.6 % above that reference, a close 0.1 % under the highest such close exits, and the next bar buys again.
Port of FMZ strategy #442635 "带滑点止损的DCA定投策略DCA-Strategy-with-Trailing-Take-Profit" (DCA Strategy with Trailing Take Profit).

FMZ source id: 442635

Source
    https://www.fmz.com/strategy/442635 (PineScript v5, FMZ last modified 2024-02-23 14:01:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-164), take profit 0.6 %; trailing 0.1 %; max DCA orders 10; price deviation 1 %; 10 % of equity, capital 1000
    buyCount < 10 and (na(lastBuyPrice) or close < lastBuyPrice (1 - 1 %)) -> entry Buy, lastBuyPrice = close, buyCount + 1
    close > lastBuyPrice (1 + 0.6 %): trailing = close (1 - 0.1 %) when na or close > trailing;  close < trailing -> close Buy, reset lastBuyPrice / trailing / buyCount

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() call sets no pyramiding, so the default refuses every further "Buy" while one is
      open: one long at a time, not an accumulation. The refused buys still move lastBuyPrice and count
      toward the ten, as written. The take-profit test is a bar-close rule (close against the trailing
      level), filled at the next open. After an exit the reference is na, so the next bar buys. The
      "Price Deviation" table value true is the 1.0 default. Long only. The 10 % of equity size is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, buy-the-dip reference with a close-based trailing take-profit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
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

NAME = "fmz_442635_dip_reference_close_trail_take_profit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_pct": [0.6, 2.0],
    "trail_pct": [0.1, 0.5],
}
DEFAULT_PARAMS = {"tp_pct": 0.6, "trail_pct": 0.1, "max_orders": 10, "deviation_pct": 1.0}


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
    cv = bars_df["close"].to_numpy(dtype=float)
    tp, tr = float(p["tp_pct"]) / 100, float(p["trail_pct"]) / 100
    dev, mx = float(p["deviation_pct"]) / 100, int(p["max_orders"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    last, cnt, trail = np.nan, 0, np.nan
    for i in range(m):
        if cnt < mx and (np.isnan(last) or cv[i] < last * (1 - dev)):
            if not held:
                le[i] = True
            last, cnt = cv[i], cnt + 1
        if not np.isnan(last) and cv[i] > last * (1 + tp):
            if np.isnan(trail) or cv[i] > trail:
                trail = cv[i] * (1 - tr)
            if cv[i] < trail:
                if held:
                    lx[i] = True
                last, trail, cnt = np.nan, np.nan, 0
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
