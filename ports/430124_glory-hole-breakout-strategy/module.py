"""Glory hole, broker days: with ADX 14 above 30, a bar whose low pierces the SMA 20 while its open and close stay above it
goes long; a bar whose high pierces it from below with open and close under it goes short.
Port of FMZ strategy #430124 "Glory Hole Breakout Strategy" (Glory Hole with SMA + ADX).

FMZ source id: 430124

Source
    https://www.fmz.com/strategy/430124 (PineScript v2, FMZ last modified 2023-10-25 11:35:36).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 179-214), SMA 20 of close, ADX 14 / 14 above 30
    bullish = sma < close and sma < open and sma > low and adx > 30 -> entry long
    bearish = sma > close and sma > open and sma < high and adx > 30 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ADX as the source's dirmov (Wilder averages); fixnan carries the last DI value over a zero true
      range.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average against the bar and an ADX level.
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

NAME = "fmz_430124_glory_hole_sma_adx"
FAMILY = "directional_movement"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "adx_level": [30, 20],
}
DEFAULT_PARAMS = {"length": 20, "adx_level": 30, "adx_len": 14, "di_len": 14}


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
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(h, lo, c, di_len, adx_len):
    up, down = h.diff(), -lo.diff()
    plus_dm = ((up > down) & (up > 0)).astype(float) * up.fillna(0.0)
    minus_dm = ((down > up) & (down > 0)).astype(float) * down.fillna(0.0)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, di_len).replace(0.0, np.nan)
    plus = _fixnan(100 * _rma(plus_dm, di_len) / atr)
    minus = _fixnan(100 * _rma(minus_dm, di_len) / atr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


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
    sma = c.rolling(int(p["length"])).mean()
    strong = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"])) > p["adx_level"]
    bull = ((sma < c) & (sma < o) & (sma > lo) & strong).to_numpy()
    bear = ((sma > c) & (sma > o) & (sma < h) & strong).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bull[i]:
            pos = 1
        elif bear[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
