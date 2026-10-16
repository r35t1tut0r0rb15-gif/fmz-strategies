"""RSI(2) momentum with a volatility-stop filter, broker days: RSI 2 above 70 goes long; RSI 2 below 30 with
the close under the volatility stop goes short.
Port of FMZ strategy #428802 "基于VSTOP和RSI的交易策略VSTOP-and-RSI-Trading-Strategy" (Vstop and RSI).

FMZ source id: 428802

Source
    https://www.fmz.com/strategy/428802 (PineScript v3, FMZ last modified 2023-10-09 15:48:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 156-199), RSI 2, 30 / 70, Vstop ATR 2 x 2
    max1 = max(max_[1] (nz 0), close); min1 = min(min_[1] (nz 0), close); up_prev = is_uptrend[1] (nz true)
    stop = up_prev ? max1 - 2 atr(2) : min1 + 2 atr(2); vstop1 = up_prev ? max(vstop[1] (nz 0), stop) : min(vstop[1], stop)
    is_uptrend = close >= vstop1; on a change max_ / min_ := close and vstop := the new side's stop, else vstop1
    rsi(close,2) > 70 -> entry long; rsi(close,2) < 30 and vstop > close -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volatility stop is a filter line, not a stop order. Its nz() seeds are kept as written
      (min_ starts from 0, so the down-side running minimum starts at 0 until the first trend change).
    * strategy.entry reverses: REVERSAL INTENDED; same-direction entries while in a position are
      ignored (pyramiding 0).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_428802_rsi2_momentum_vstop"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [2, 3],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"rsi_length": 2, "oversold": 30, "overbought": 70, "vlength": 2, "mult": 2.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _nmax(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else max(a, b)


def _nmin(a, b):
    return np.nan if np.isnan(a) or np.isnan(b) else min(a, b)


def _vstop(bars_df, n, mult):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    vstop = np.full(m, np.nan)
    mx_prev = mn_prev = 0.0
    up_prev = True
    for i in range(m):
        mx1 = _nmax(mx_prev, cv[i])
        mn1 = _nmin(mn_prev, cv[i])
        stop = mx1 - mult * atr[i] if up_prev else mn1 + mult * atr[i]
        vp = vstop[i - 1] if i >= 1 and not np.isnan(vstop[i - 1]) else 0.0
        v1 = _nmax(vp, stop) if up_prev else _nmin(vp, stop)
        is_up = bool(cv[i] - v1 >= 0) if not np.isnan(v1) else False
        changed = is_up != up_prev
        mx = cv[i] if changed else mx1
        mn = cv[i] if changed else mn1
        vstop[i] = ((mx - mult * atr[i]) if is_up else (mn + mult * atr[i])) if changed else v1
        mx_prev = 0.0 if np.isnan(mx) else mx
        mn_prev = 0.0 if np.isnan(mn) else mn
        up_prev = is_up
    return pd.Series(vstop, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    vs = _vstop(bars_df, int(p["vlength"]), float(p["mult"]))
    long_e = (r > p["overbought"]).astype(bool)
    short_e = ((r < p["oversold"]) & (vs > c)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
