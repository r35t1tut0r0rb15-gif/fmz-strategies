"""ATR trailing line, broker days: the classic close-based ATR trailing stop (3.5 x ATR 5); a close
above the line is long, below it is short (always in the market after the first bar).
Port of FMZ strategy #427470 "ATR Trend Following Strategy".

FMZ source id: 427470

Source
    https://www.fmz.com/strategy/427470 (PineScript, no @version line, v5 syntax; FMZ last modified 2023-09-21 15:13:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 121-139), ATR 5 x 3.5
    stop = close > s[1] and close[1] > s[1] ? max(s[1], close - loss)
         : close < s[1] and close[1] < s[1] ? min(s[1], close + loss)
         : close > s[1] ? close - loss : close + loss            (s[1] = nz(stop[1], 0))
    close > stop -> entry long; close < stop -> entry short (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing stop" is a line compared with the close: the entries are close-based signals
      (no stop order, no mark). `pos` and its colours only plot.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission setting stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427470_atr_trailing_line_state"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [5, 10, 14],
    "atr_mult": [3.5, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 5, "atr_mult": 3.5}


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
    loss = (p["atr_mult"] * _rma(tr, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st = np.full(m, np.nan)
    for i in range(m):
        s1 = st[i - 1] if i and not np.isnan(st[i - 1]) else 0.0
        c1 = cv[i - 1] if i else np.nan
        if cv[i] > s1 and c1 > s1:
            st[i] = max(s1, cv[i] - loss[i])
        elif cv[i] < s1 and c1 < s1:
            st[i] = min(s1, cv[i] + loss[i])
        elif cv[i] > s1:
            st[i] = cv[i] - loss[i]
        else:
            st[i] = cv[i] + loss[i]
    up, dn = cv > st, cv < st
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
