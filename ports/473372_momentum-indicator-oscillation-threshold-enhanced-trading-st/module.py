"""CCI 12 dips under -90, daily bars, long only: a CCI under -90 buys; the first close over the previous close sells. The point stop and target are switched off by default.
Port of FMZ strategy #473372 "Momentum Indicator Oscillation Threshold Enhanced Trading Strategy" (CCI Threshold Strategy).

FMZ source id: 473372

Source
    https://www.fmz.com/strategy/473372 (PineScript v5, FMZ last modified 2024-11-29 15:40:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-134), CCI 12, buy under -90; stop 100 / target 150 points off; commission 0.05 per contract, slippage 1
    cci < -90 -> entry Buy;  close > highest(close[1], 1) -> close Buy;  cci < -90 -> exit(loss = na, profit = na) (switched off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(close[1], 1) is the previous close. The close acts only on a long held into the bar
      (#437773): on a flat bar with both tests the entry is sent and the close does nothing; on a long
      bar a new entry is ignored (pyramiding 0) and the close acts. A loop follows the position for
      that. The stop and target are off (na). Long only. The costs are not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI dips with an up-close exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission and slippage stored, not ported.
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

NAME = "fmz_473372_cci12_below_m90_up_close_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 20],
    "threshold": [-90, -150],
}
DEFAULT_PARAMS = {"length": 12, "threshold": -90}


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


def _cci(src, n):
    ma = src.rolling(n).mean()
    md = src.rolling(n).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True)
    return (src - ma) / (0.015 * md)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    buy = (_cci(c, int(p["length"])) < float(p["threshold"])).to_numpy()
    up = (c > c.shift(1)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if pos == 0 and buy[i]:
            le[i], nxt = True, 1
        elif pos == 1 and up[i]:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
