"""EMA 10 / 100 / 200 alignment, long only, broker days: while flat, the EMAs stacked upward (10 above 100 above 200) go long; once the stack breaks the long is closed.
Port of FMZ strategy #436788 "多周期EMA交叉量化交易策略Multi-Period-EMA-Crossover-Quantitative-Trading-Strategy" (Tester Emas).

FMZ source id: 436788

Source
    https://www.fmz.com/strategy/436788 (PineScript v5, FMZ last modified 2023-12-27 17:09:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 90-135), EMA 10 / 100 / 200; date window 2000-2030 (FechaValida() = true)
    alcista = ema1 > ema2 and ema2 > ema3;  comprado = strategy.position_size > 0
    not comprado and alcista -> entry Compra (qty = round(equity / close));  comprado and not alcista -> close Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * FechaValida() is true (the date inputs are the author's window): dropped, so its period-end close
      never fires. The crossover lines are plotted only. Long only. The equity / close quantity is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA alignment.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity / close quantity stored.
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

NAME = "fmz_436788_ema_stack_long_only"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p1": [10, 20],
    "p2": [100, 50],
}
DEFAULT_PARAMS = {"p1": 10, "p2": 100, "p3": 200}


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
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("p1", "p2", "p3"))
    alc = ((e1 > e2) & (e2 > e3)).to_numpy()
    m = len(alc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and alc[i]:
            le[i] = True
            pos = 1
        elif pos == 1 and not alc[i]:
            lx[i] = True
            pos = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
