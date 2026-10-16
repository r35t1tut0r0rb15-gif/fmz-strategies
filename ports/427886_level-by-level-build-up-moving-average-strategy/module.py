"""ATR renko bricks, broker days, long only: a close more than one ATR(14) above the last brick lays an
up brick, more than one ATR below lays a down brick; the second up brick in a row goes long and any
down brick closes the position.
Port of FMZ strategy #427886 "Level-by-Level Build-Up Moving Average Strategy" (Renko Level Strategy 2).

FMZ source id: 427886

Source
    https://www.fmz.com/strategy/427886 (PineScript v4, FMZ last modified 2023-09-26 16:00:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 191-237), timeframe "D", ATR 14
    RENKO carries forward (first value: close); ATR = security("D", atr(14))
    close > RENKO[1] + ATR[1] -> up brick (RENKO = close, BUY += 1, SELL = 0)
    close < RENKO[1] - ATR[1] -> down brick (RENKO = close, BUY = 0, SELL += 1)
    BUY[1] == 1 and BUY == 2 -> entry long; down brick -> cancel_all and close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The timeframe input "D" equals the daily chart's: the security calls are the series themselves.
    * pyramiding 2 is sizing: the entry fires once per up run (BUY goes 1 -> 2 once before a down
      brick resets it). Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50 % of equity, pyramiding 2 stored in original_sizing.txt.
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

NAME = "fmz_427886_atr_renko_second_brick_long"
FAMILY = "renko_bricks"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length": [14, 7, 28, 50],
}
DEFAULT_PARAMS = {"atr_length": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_length"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    renko, buy, pos = np.nan, 0, 0
    for i in range(m):
        r1 = renko
        a1 = atr[i - 1] if i else np.nan
        buy1 = buy
        if np.isnan(r1):
            renko = cv[i]
        dn = False
        if cv[i] > r1 + a1:
            renko, buy = cv[i], buy + 1
        if cv[i] < r1 - a1:
            dn = True
            renko, buy = cv[i], 0
        if buy1 == 1 and buy == 2:
            pos = 1
        if dn:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
