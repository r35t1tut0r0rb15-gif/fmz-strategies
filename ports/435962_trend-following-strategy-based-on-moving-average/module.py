"""Minervini trend template, broker days, long only: a close over the SMA 50 / 150 / 200 stack with the SMA 200 rising over 22 bars, 25 % over
the 260-bar low and within 25 % of the 260-bar high buys; a close 10 % over or 5 % under the entry price closes it.
Port of FMZ strategy #435962 "Trend Following Strategy Based on Moving Average" (Pure Mark Minervini 10%TP 5%CL).

FMZ source id: 435962

Source
    https://www.fmz.com/strategy/435962 (PineScript v4, FMZ last modified 2023-12-20 14:23:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 127-155), SMA 50 / 150 / 200; 260-bar window; take profit 10 %, stop 5 % (on closes)
    buy = close > ma150 and close > ma200 and ma150 > ma200 and ma200 > ma200[22] and ma50 > ma150 and ma50 > ma200 and close > ma50 and (close / lowest(low, 260) - 1) 100 >= 25 and (1 - close / highest(high, 260)) 100 <= 25 and close > 0.3
    sell = close > ep 1.1 or close < ep 0.95 (ep = the average price);  entry long (buy);  close long (sell)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are rules on bar closes against the position's average price (the next open's fill),
      filled at the next open: close-based exit signals, not broker stops (no mark). While long, a still-true
      entry adds nothing; after an exit the entry is taken again on the next flat bar if the template
      holds. The condition close > 0.3 is a price constant (a guard against penny prices), kept as written. Long
      only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, average stack and percent rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commission input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435962_minervini_template_long"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "take": [1.1, 1.2],
    "stop": [0.95, 0.9],
}
DEFAULT_PARAMS = {"take": 1.1, "stop": 0.95, "lookback": 260, "limit_pct": 25.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ma50, ma150, ma200 = (c.rolling(n).mean() for n in (50, 150, 200))
    lb = int(p["lookback"])
    low_n, high_n = lo.rolling(lb).min(), h.rolling(lb).max()
    above52lo = (c / low_n - 1) * 100
    below52hi = (1 - c / high_n) * 100
    lim = float(p["limit_pct"])
    buy = ((c > ma150) & (c > ma200) & (ma150 > ma200) & (ma200 > ma200.shift(22)) & (ma50 > ma150) & (ma50 > ma200)
           & (c > ma50) & (above52lo >= lim) & (below52hi <= lim) & (c > 0.3)).fillna(False).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    take, stop = float(p["take"]), float(p["stop"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, ep, pend = 0, np.nan, None
    for i in range(m):
        if pend == "enter":
            pos, ep = 1, ov[i]
        elif pend == "exit":
            pos, ep = 0, np.nan
        pend = None
        sell = pos == 1 and (cv[i] > ep * take or cv[i] < ep * stop)
        if pos == 0 and buy[i]:
            pend = "enter"
        elif sell:
            pend = "exit"
        tgt[i] = 1 if (pend == "enter" or (pos == 1 and pend != "exit")) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
