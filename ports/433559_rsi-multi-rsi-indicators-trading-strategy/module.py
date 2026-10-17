"""Noro's RSI symphony, broker days, long only: when any of RSI 4 < 20, RSI 7 < 25 or RSI 14 < 30 holds, a long opens (the
slowest RSI that fired is remembered); the long is closed when that remembered RSI rises back above its limit.
Port of FMZ strategy #433559 "多重RSI指标交易策略Multi-RSI-Indicators-Trading-Strategy" (Noro's Symphony Strategy v1.1).

FMZ source id: 433559

Source
    https://www.fmz.com/strategy/433559 (PineScript v2, FMZ last modified 2023-11-28 15:03:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-171), RSI 4 / 20, 7 / 25, 14 / 30 on; 21 / 35 and 28 / 40 off; colour filter off; pyramiding 20
    up_k = rsi_k < limit_k (enabled);  str = the highest k that fired, else str[1];  up = any up_k
    up and (close < open or cf == false) -> entry long (adds);  exit = rsi_str > limit_str -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour filter is off by default (cf false), so the candle colour is not required.
    * pyramiding 20 adds units on repeated signals; stacking is sizing (SURVEY_README, as #426588), so
      the net position is ported. The lot formula is sizing.
    * An entry and the exit on one bar: the entry is placed first and close_all then closes the
      position held, so a long already open is closed; from flat the entry stands. Long only;
      Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot formula and pyramiding 20 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433559_noro_rsi_symphony"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit_shift": [0, -5],
    "use_rsi4": [False, True],
}
DEFAULT_PARAMS = {"limit_shift": 0, "use_rsi4": False}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sh = float(p["limit_shift"])
    cfg = [(4, 20 + sh, True), (7, 25 + sh, True), (14, 30 + sh, True), (21, 35 + sh, bool(p["use_rsi4"]))]
    rs = [_rsi(c, n).to_numpy() for n, _, _ in cfg]
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, strk = 0, -1
    with np.errstate(invalid="ignore"):
        ups = [(rs[j] < cfg[j][1]) & cfg[j][2] for j in range(len(cfg))]
        abv = [rs[j] > cfg[j][1] for j in range(len(cfg))]
    for i in range(m):
        for j in range(len(cfg) - 1, -1, -1):
            if ups[j][i]:
                strk = j
                break
        up = any(u[i] for u in ups)
        ex = strk >= 0 and abv[strk][i]
        start = pos
        if up:
            pos = 1
        if ex and start == 1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
