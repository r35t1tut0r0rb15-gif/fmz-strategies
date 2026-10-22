"""3 % drops against any of the last 5 closes buy, daily bars, long only, at most once per 6 bars by the script's counter: the trade closes at a 5 % target above its signal close (the add-on buys never fill).
Port of FMZ strategy #449949 "Price-Action-Pyramiding-5-Profit-Target-3-Stop-Loss-价格行为-金字塔加仓-5止盈-3止损" (G Strategija su piramidavimu).

FMZ source id: 449949

Source
    https://www.fmz.com/strategy/449949 (PineScript v5, FMZ last modified 2024-04-30 16:20:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-139), drop 3 % vs close[1..5]; counter >= 5 bars; target 5 % of the signal close; qty 1000 / close
    should_buy = close < close[i] x 0.97 for any i in 1..5;  should_buy and count >= 5 -> entry Pirkti_n, count = 0, n + 1;  else count + 1
    exit(TakeProfit_i, Pirkti_i, limit = entryPrice_i x 1.05)  (every bar for every recorded entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() sets no pyramiding, so a buy while long never fills (its id gets no position), but
      the counter and the entry list still move, as written; the counter resets on every buy call.
      The target of the trade that filled is 5 % above its signal close: tp_stop 0.05 of the fill (as
      #437751). There is no stop (the 3 % input is the entry drop). Daily stop module: mark
      coarse_bar_stop. Long only. Stop module: portfolio_kwargs {} (driver D4). The 1000 / close
      quantity is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed from the signal close.
    2 generic: PASS, dip buying with a percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1000 / close quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 0-23 hour test is always true).
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_449949_three_pct_dip_counter_buy_five_pct_target_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "drop": [0.03, 0.05],
    "target": [0.05, 0.1],
}
DEFAULT_PARAMS = {"drop": 0.03, "target": 0.05, "lookback": 5, "min_count": 5}


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
    k = 1.0 - float(p["drop"])
    dip = pd.Series(False, index=c.index)
    for i in range(1, int(p["lookback"]) + 1):
        dip |= c < c.shift(i) * k
    d = dip.to_numpy()
    m = len(d)
    le = np.zeros(m, dtype=bool)
    count = 0
    mc = int(p["min_count"])
    for i in range(m):
        if d[i] and count >= mc:
            le[i] = True                     # the engine ignores it while a long is open (no pyramiding)
            count = 0
        else:
            count += 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["target"])}


def portfolio_kwargs(**params):
    return {}
