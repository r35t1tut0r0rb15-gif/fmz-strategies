"""PlanB's RSI regime switch, broker days: after the RSI 14 has been under 50 within the previous 6 days, a bounce of more
than 2 points above that low goes long; after it has been above 90 within the previous 6 days, a fall under 65 goes
short. Always in after the first signal.
Port of FMZ strategy #433434 "基于RSI指标的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator" (PlanB Quant Investing 101 (PlanB RSI Strategy)).

FMZ source id: 433434

Source
    https://www.fmz.com/strategy/433434 (PineScript v4, FMZ last modified 2023-11-27 16:02:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 216-262), RSI 14; sell level 90, drop 65; buy level 50, bounce 2; window 6
    maxrsi = highest(rsi, 6)[1];  sell = maxrsi > 90 and rsi < 65 -> entry short
    minrsi = lowest(rsi, 6)[1];  buy = minrsi < 50 and rsi > minrsi + 2 -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both signals can hold on one bar; the short entry is issued after the long one, so the bar ends
      short, as written. The entries are levels (re-fired while they hold, ignored when already in
      that position). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 1000 cash quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433434_planb_rsi_regime"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sell_level": [90, 80],
    "window": [6, 12],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sell_level": 90, "drop": 65, "buy_level": 50, "bounce": 2, "window": 6}


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
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    w = int(p["window"])
    mx = r.rolling(w).max().shift(1)
    mn = r.rolling(w).min().shift(1)
    sell = ((mx > p["sell_level"]) & (r < p["drop"])).to_numpy()
    buy = ((mn < p["buy_level"]) & (r > mn + p["bounce"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
