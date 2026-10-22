"""Dips from the running all-time high, daily bars, long only: a close 10 %, 15 % or 20 % under the all-time high of previous bars buys (each level once per new high; one position at a time), and a close back within 5 % of that high sells.
Port of FMZ strategy #475604 "多层级跌幅ATH动态追踪三段买入策略-Multi-level-ATH-Dynamic-Tracking-Triple-Entry-Strategy" (Long-term Bean Dip (v.1)).

FMZ source id: 475604

Source
    https://www.fmz.com/strategy/475604 (PineScript v6, FMZ last modified 2024-12-20 14:53:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-181), dips 10 / 15 / 20 %; recovery 5 %; buy amount $50000 per dip
    ath := na ? high : max(ath[1], high[1]); new high -> dip flags reset;  drop >= 10 % and not dip1 -> entry Dip1 Buy, dip1 := true;  15 % / 20 % mirror for Dip2 / Dip3;  close >= ath x 0.95 and long -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The all-time high runs from the first loaded bar over previous highs (a loop), so it counts from
      where the data starts, as written. With pyramiding 1 the three dip ids never add up: the first
      dip entry sent while flat fills and later ones are ignored while long, but each still sets its
      flag, as written; the flags reset on a new high. The recovery close and the dip entries cannot hold
      on one bar. Long only. The dollar amounts are not ported. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, all-time-high dip entries with a recovery exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: dollar amounts per dip stored, not ported.
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

NAME = "fmz_475604_ath_dip_10_15_20_recovery_5pct_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dip1": [10.0, 20.0],
    "recovery": [5.0, 2.0],
}
DEFAULT_PARAMS = {"dip1": 10.0, "recovery": 5.0}


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
    hv, cv = bars_df["high"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    d1 = float(p["dip1"])
    dips = (d1, d1 + 5.0, d1 + 10.0)
    rec = 1 - float(p["recovery"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ath = np.nan
    flags = [False, False, False]
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if np.isnan(ath):
            ath = hv[i]
        else:
            prev = ath
            ath = max(prev, hv[i - 1])
            if hv[i - 1] > prev:
                flags = [False, False, False]
        drop = (ath - cv[i]) / ath * 100.0
        for j in range(3):
            if drop >= dips[j] and not flags[j]:
                if pos == 0 and nxt == 0:
                    le[i], nxt = True, 1
                flags[j] = True
        if cv[i] >= ath * rec and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
