"""Chande momentum dips, daily bars, long only: a CMO 9 under -50 buys (when the trade flag is clear); a CMO over 50, or 5 bars since the last reading under -50, sells.
Port of FMZ strategy #473134 "Adaptive Trend Following Strategy Based on Momentum Oscillator" (Chande Momentum Oscillator Strategy).

FMZ source id: 473134

Source
    https://www.fmz.com/strategy/473134 (PineScript v5, FMZ last modified 2024-11-27 15:03:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-127), CMO 9 = 100 x (sum of ups - sum of downs) / (sum of ups + downs); levels -50 / 50; exit 5 bars after the last buy reading
    cmo < -50 and not inTrade -> entry Long, inTrade;  cmo > 50 or barssince(cmo < -50) >= 5 -> close Long, inTrade = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag is cleared by every exit test, held or not, as written. barssince counts from the last
      bar with the CMO under -50 (a new low reading restarts it). The entry is called before the close;
      the close acts only on a long held into the bar. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CMO dips with a timed exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG473134 (2 members, best partner #474705, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473134_cmo9_dip_timed_or_overbought_exit_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cmo_period": [9, 14],
    "hold": [5, 10],
}
DEFAULT_PARAMS = {"cmo_period": 9, "hold": 5}


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
    n = int(p["cmo_period"])
    ch = c.diff()
    up = ch.where(ch > 0, 0.0)
    dn = (-ch).where(ch < 0, 0.0)
    su, sd = up.rolling(n).mean() * n, dn.rolling(n).mean() * n
    cmo = (100 * (su - sd) / (su + sd)).to_numpy()
    hold = int(p["hold"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, in_trade, last_buy = 0, False, None
    for i in range(m):
        with np.errstate(invalid="ignore"):
            buy, sell1 = cmo[i] < -50, cmo[i] > 50
        if buy:
            last_buy = i
        sell2 = last_buy is not None and i - last_buy >= hold
        cur = pos
        if buy and not in_trade:
            in_trade = True
            if pos == 0:
                cur = 1
        if sell1 or sell2:
            in_trade = False
            if pos == 1:
                cur = 0                          # the close acts only on a long held into the bar
        if cur == 1 and pos == 0:
            le[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        pos = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
