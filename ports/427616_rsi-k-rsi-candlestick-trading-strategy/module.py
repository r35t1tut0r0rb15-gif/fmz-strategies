"""RSI with candlestick patterns, broker days: an RSI(hlc3) cross back above 30 goes long when a bullish
pattern (white marubozu, hammer, tweezer bottom, three white soldiers, morning star, three inside up)
printed on this or the previous bar in a weak market; a cross back below 70 goes short on the bearish
mirror patterns. An RSI cross above 70 closes a long, a cross below 30 closes a short.
Port of FMZ strategy #427616 "RSI Candlestick Trading Strategy".

FMZ source id: 427616

Source
    https://www.fmz.com/strategy/427616 (PineScript v2, FMZ last modified 2023-09-22 17:10:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 166-348), RSI 14 on hlc3, bullish 55, bearish 45
    rsi = Wilder RSI of hlc3; trend up / down = rsi(close, 14) >= 55 / <= 45
    crossover(rsi, 30) and (pattern or pattern[1]) for wm, h, twb, tws, ms, tiu -> entry long
    crossunder(rsi, 70) and (pattern or pattern[1]) for bm, hm, ss, twt, tbc, tid -> entry short
    crossover(rsi, 70) -> entry short qty 0; crossunder(rsi, 30) -> entry long qty 0
    (inverted hammer, engulfings and evening star are drawn but do not trade)

Interpretation choices (Pine rules in SURVEY_README.md)
    * An entry with qty 0 only closes the opposite position (Noro's idiom, as earlier ports).
    * Pattern formulas as written, including the divisions by a bar range (na on a zero range).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and candle ratios only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427616_rsi_candlestick_patterns"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "bull": [55, 60],
    "bear": [45, 40],
}
DEFAULT_PARAMS = {"length": 14, "bull": 55, "bear": 45, "trend_len": 14}


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


def _rsi(src, n):
    d = src.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)
    return r.where(up.notna() & dn.notna())


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
    rsi = _rsi((h + lo + c) / 3, int(p["length"]))
    rc = _rsi(c, int(p["trend_len"]))
    t_up, t_dn = rc >= p["bull"], rc <= p["bear"]
    rng = h - lo
    body = (c - o).abs()
    oc2 = np.minimum(c, o) + body / 2
    uw = h - np.maximum(o, c)
    lw = np.minimum(o, c) - lo
    is_up = c > o
    S = lambda x, k=1: x.shift(k)
    B = lambda x, k=1: x.shift(k, fill_value=False).astype(bool)
    is_doji = (body / rng) < 0.05
    wm = is_up & (uw <= 0.05 * body) & (lw <= 0.05 * body) & t_dn
    bm = ~is_up & (uw <= 0.05 * body) & (lw <= 0.05 * body) & t_up
    ham = is_up & (lw >= 2 * body) & (uw <= 0.1 * body) & t_dn
    hm = ~is_up & (lw >= 2 * body) & (uw <= 0.1 * body) & t_up
    ss = ~is_up & (uw >= 2 * body) & (lw <= 0.1 * body) & t_up
    twb = ~B(is_up) & is_up & (np.minimum(lw, S(lw)) / np.maximum(lw, S(lw)) >= 0.99) \
        & (np.minimum(lo, S(lo)) / np.maximum(lo, S(lo)) >= 0.99) & t_dn
    twt = B(is_up) & ~is_up & (np.minimum(uw, S(uw)) / np.maximum(uw, S(uw)) >= 0.99) \
        & (np.minimum(h, S(h)) / np.maximum(h, S(h)) >= 0.99) & t_up
    tws = ~B(is_up, 3) & B(is_up, 2) & B(is_up) & is_up & (S(body) > S(body, 2)) \
        & (uw < 0.1 * body) & (lw < 0.1 * body) & t_dn
    tbc = B(is_up, 3) & ~B(is_up, 2) & ~B(is_up) & ~is_up & (S(body) > S(body, 2)) \
        & (uw < 0.1 * body) & (lw < 0.1 * body) & t_up
    small1 = (S(body) / S(rng)) < 0.1
    ms = ~B(is_up) & small1 & (c > S(oc2, 2)) & (c < S(o, 2)) & t_dn
    tiu = ~B(is_up, 2) & (S(c) > S(oc2, 2)) & (S(c) < S(o, 2)) & (c > S(h, 2)) & t_dn
    tid = B(is_up, 2) & (S(c) < S(oc2, 2)) & (S(c) > S(o, 2)) & (c < S(lo, 2)) & t_up
    _ = is_doji  # engulfings use it; they do not trade
    bull = pd.Series(False, index=c.index)
    for x in (wm, ham, twb, tws, ms, tiu):
        x = x.fillna(False).astype(bool)
        bull = bull | x | B(x)
    bear = pd.Series(False, index=c.index)
    for x in (bm, hm, ss, twt, tbc, tid):
        x = x.fillna(False).astype(bool)
        bear = bear | x | B(x)
    xo30 = (rsi > 30) & (rsi.shift(1) <= 30)
    xu70 = (rsi < 70) & (rsi.shift(1) >= 70)
    xo70 = (rsi > 70) & (rsi.shift(1) <= 70)
    xu30 = (rsi < 30) & (rsi.shift(1) >= 30)
    le = (xo30 & bull).to_numpy()
    se = (xu70 & bear).to_numpy()
    close_long, close_short = xo70.to_numpy(), xu30.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        elif close_long[i] and pos == 1:
            pos = 0
        elif close_short[i] and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
