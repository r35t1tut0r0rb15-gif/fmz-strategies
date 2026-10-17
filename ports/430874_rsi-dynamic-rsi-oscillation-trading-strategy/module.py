"""Noro's weekly level + RSI dips, broker days, long only: a red bar whose low is above the last completed broker week's
ohlc4 (from flat), or a red bar with RSI 7 under 30, goes long; RSI over 30 with the low no longer above the level
closes. Adds are not ported.
Port of FMZ strategy #430874 "动态RSI震荡操作策略Dynamic-RSI-Oscillation-Trading-Strategy" (Noro's Levels+RSI Strategy v1.0).

FMZ source id: 430874

Source
    https://www.fmz.com/strategy/430874 (PineScript v2, FMZ last modified 2023-11-02 16:04:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 174-220), level = weekly ohlc4[1], RSI 7 / 30, antipila and colour filter on, pyramiding 3
    level = security(tickerid, 'W', ohlc4[1]); ls = low > level (antipila on)
    up1 = flat and ls and close < open;  up2 = rsi < 30 and close < open -> entry long (adds up to pyramiding 3)
    exit1 = high < level;  exit2 = rsi > 30 and not ls;  (exit1 and rsi > 30) or exit2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine v2 security with [1] inside: the previous week's ohlc4, i.e. the last COMPLETED week.
      Weeks are broker weeks (ISO week of the broker-day date), the weekly ohlc4 from that week's
      daily bars, used from the next week's first bar.
    * pyramiding 3: further signals add in the source; adds are not ported (one net position). The
      exit is exit2 alone (exit1 implies not ls). Entries and the exit cannot meet on one bar (RSI
      under / over 30, ls / not ls). needshort is unused: long only; Opposite entries cannot occur.
    * RSI as written: Wilder rma of the up / down changes. The date window (1900-2100) is dropped.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, a weekly level and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the capital % lot formula stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430874_weekly_level_rsi_dips_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14],
    "rsi_limit": [30, 20],
}
DEFAULT_PARAMS = {"rsi_len": 7, "rsi_limit": 30}


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
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    wk = pd.DataFrame({"o": o.to_numpy(), "h": h.to_numpy(), "l": lo.to_numpy(), "c": c.to_numpy()}, index=week)
    agg = wk.groupby(level=0).agg({"o": "first", "h": "max", "l": "min", "c": "last"})
    level = ((agg["o"] + agg["h"] + agg["l"] + agg["c"]) / 4).shift(1)   # the last completed week
    lvl = level.reindex(week).to_numpy()
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    lim = float(p["rsi_limit"])
    lv, red = lo.to_numpy(dtype=float), (c < o).to_numpy()
    m = len(lv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        ls = lv[i] > lvl[i]
        up1 = pos == 0 and ls and red[i]
        up2 = r[i] < lim and red[i]
        if up1 or up2:
            pos = 1
        elif pos == 1 and r[i] > lim and not ls:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
