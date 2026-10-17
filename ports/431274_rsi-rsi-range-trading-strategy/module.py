"""Alternating RSI 2 extremes, broker days: after an RSI at or over 91 has been seen, an RSI at or under 11 closes any short
and goes long; after an RSI at or under 11, an RSI at or over 91 closes any long and goes short; a close 0.5 % beyond the
entry close against the position closes it.
Port of FMZ strategy #431274 "RSI区间震荡交易策略RSI-Range-Trading-Strategy" (Simple RSI Strategy).

FMZ source id: 431274

Source
    https://www.fmz.com/strategy/431274 (PineScript v5, FMZ last modified 2023-11-06 16:12:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-195), RSI 2, levels 11 / 91, stop 0.5 %
    close <= longEntryPrice x 0.995 -> close Long;  close >= shortEntryPrice x 1.005 -> close Short
    rsi <= 11 and maxRsi == 91 -> maxRsi = 11, close Short, entry Long, longEntryPrice = close
    else rsi >= 91 and maxRsi == 11 -> maxRsi = 91, close Long, entry Short, shortEntryPrice = close
    else rsi >= 91 -> maxRsi = 91, close Long;  else rsi <= 11 -> maxRsi = 11, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state (maxRsi starting at 0, the last entry closes) is ported line for line; the stops are
      close-checked exits from the signal close, not stop orders. The closes act on the position
      held at the bar's start; an entry on the same bar sets the final position.
    * An entry closes the opposite side first: REVERSAL INTENDED. RSI as Pine's (Wilder). Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked stops.
    2 generic: PASS, RSI levels and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-risk value (unused by the orders) stored in original_sizing.txt.
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

NAME = "fmz_431274_rsi2_alternating_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_level": [11, 20],
    "stop_pct": [0.5, 2.0],
}
DEFAULT_PARAMS = {"rsi_len": 2, "buy_level": 11, "stop_pct": 0.5}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    bl = float(p["buy_level"])
    sl_ = 102 - bl
    st = float(p["stop_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, max_rsi, le_p, se_p = 0, 0.0, np.nan, np.nan
    for i in range(m):
        start = pos
        if start == 1 and cv[i] <= le_p * (1 - st):
            pos = 0
        if start == -1 and cv[i] >= se_p * (1 + st):
            pos = 0
        if r[i] <= bl and max_rsi == sl_:
            max_rsi, pos, le_p = bl, 1, cv[i]
        elif r[i] >= sl_ and max_rsi == bl:
            max_rsi, pos, se_p = sl_, -1, cv[i]
        elif r[i] >= sl_:
            max_rsi = sl_
            if start == 1:
                pos = 0
        elif r[i] <= bl:
            max_rsi = bl
            if start == -1:
                pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
