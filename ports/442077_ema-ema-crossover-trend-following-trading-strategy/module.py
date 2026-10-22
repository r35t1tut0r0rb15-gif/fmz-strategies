"""EMA 3 / 30 crossings with a doubling target, broker days, long only: the EMA 3 crossing over the EMA 30 goes long; crossing under, or the close at twice the fill price, closes.
Port of FMZ strategy #442077 "基于EMA指标的趋势跟踪交易策略EMA-Crossover-Trend-Following-Trading-Strategy" (EMACross).

FMZ source id: 442077

Source
    https://www.fmz.com/strategy/442077 (PineScript v5, FMZ last modified 2024-02-19 10:39:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-145), EMA 3 / 30; profit percentage 100
    crossover(ema3, ema30) -> entry Buy;  crossunder(ema3, ema30) or close >= position_avg_price (1 + 100 %) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a bar-close test of the close against the fill price (the average price is na
      while flat), sent at the next open. The short side is commented out. Long only. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and close-vs-fill target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442077 (2 members, best partner #442821, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442077_ema3_30_cross_double_target_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 9],
    "profit_pct": [100.0, 50.0],
}
DEFAULT_PARAMS = {"fast": 3, "profit_pct": 100.0, "slow": 30}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    ov = bars_df["open"].to_numpy(dtype=float)
    mult = 1 + float(p["profit_pct"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, entry_i = 0, -1
    for i in range(m):
        if held == 1 and i >= entry_i and (dn[i] or cv[i] >= ov[entry_i] * mult):
            lx[i], held = True, 0
        elif held == 0 and up[i] and i + 1 < m:
            le[i], held, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
