"""PPO bull / bear divergence, broker days: price bottoms and tops (confirmed one bar later) are matched
against bottoms and tops of a smoothed PPO of the open; a bullish divergence (or a long-term one over
55 bars) goes long, a bearish one goes short; a new PPO top closes a long, a new PPO bottom closes a short.
Port of FMZ strategy #427471 "PPO Bull Bear Divergence Trading Strategy".

FMZ source id: 427471

Source
    https://www.fmz.com/strategy/427471 (PineScript v2, FMZ last modified 2023-09-21 15:16:50).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 129-250), PPO 12 / 26 of open, smoother 2, look-back 55, long-term on
    d = sma(100 (ema12 - ema26) / ema26, 2) of open
    priceMins / priceMax: bottoms / tops (and plateaus) of low / high at bar [1]; oscMins / oscMax: of d at [1]
    the divergence tests bullishdiv1..4 / bearishdiv1..4 on valuewhen() chains (lines 156-222)
    bullish -> entry long; bearish -> entry short; oscMax (d[1]) -> close long; oscMins -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every quantity is written exactly as in the source (valuewhen occurrence 0 = the latest event,
      1 = the one before; barssince counts from the latest event; comparisons with na are false).
      `low[1] and ...` reads low[1] as a boolean (true unless 0).
    * `if (beardiv)` is true on a PPO top whose d[1] is not 0 (a float used as a condition).
    * Entries come before the closes in the script; an opposite entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; extremes are used only once confirmed.
    2 generic: PASS, a percentage oscillator and comparisons of the instrument's own prices.
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

NAME = "fmz_427471_ppo_divergence"
FAMILY = "macd_divergence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [55, 30],
    "fast": [12, 8],
    "long_term_div": [True, False],
}
DEFAULT_PARAMS = {"lookback": 55, "fast": 12, "slow": 26, "smoother": 2, "long_term_div": True}


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


def _sh(a, k):
    a = np.asarray(a, dtype=float)
    return np.concatenate((np.full(k, np.nan), a[:-k])) if k else a


def _shb(a, k):
    a = np.asarray(a, dtype=bool)
    return np.concatenate((np.zeros(k, dtype=bool), a[:-k])) if k else a


def _valuewhen(cond, src, occ):
    cond = np.asarray(cond, dtype=bool)
    src = np.asarray(src, dtype=float)
    out = np.full(len(src), np.nan)
    hits = []
    for i in range(len(src)):
        if cond[i]:
            hits.append(src[i])
        if len(hits) > occ:
            out[i] = hits[-1 - occ]
    return out


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, f in enumerate(cond):
        if f:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _roll(a, n, fn):
    return getattr(pd.Series(a).rolling(n), fn)().to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o = bars_df["open"]
    lo = bars_df["low"].to_numpy(dtype=float)
    hi = bars_df["high"].to_numpy(dtype=float)
    fast_ma = o.ewm(span=int(p["fast"]), adjust=False).mean()
    slow_ma = o.ewm(span=int(p["slow"]), adjust=False).mean()
    d = ((fast_ma - slow_ma) / slow_ma * 100).rolling(int(p["smoother"])).mean().to_numpy()
    L = int(p["lookback"])
    l1, l2, l3, l4, l5 = (_sh(lo, k) for k in range(1, 6))
    h1, h2, h3, h4, h5 = (_sh(hi, k) for k in range(1, 6))
    with np.errstate(invalid="ignore"):
        pmin = ((lo > l1) & (l1 < l2)) | ((l1 == l2) & (l1 < lo) & (l1 < l3)) \
            | ((l1 == l2) & (l1 == l3) & (l1 < lo) & (l1 < l4)) \
            | ((l1 == l2) & (l1 == l3) & (l1 != 0) & (l1 == l4) & (l1 < lo) & (l1 < l5))
        pmax = ((hi < h1) & (h1 > h2)) | ((h1 == h2) & (h1 > hi) & (h1 > h3)) \
            | ((h1 == h2) & (h1 == h3) & (h1 > hi) & (h1 > h4)) \
            | ((h1 == h2) & (h1 == h3) & (h1 != 0) & (h1 == h4) & (h1 > hi) & (h1 > h5))
        d1, d2 = _sh(d, 1), _sh(d, 2)
        omin = (d > d1) & (d1 < d2)
        omax = (d < d1) & (d1 > d2)
    ct4, ct5 = _valuewhen(omin, d1, 0), _valuewhen(omax, d1, 0)
    ct6, ct7 = _valuewhen(pmin, l1, 0), _valuewhen(pmax, h1, 0)
    bs_omin, bs_omax = _barssince(omin), _barssince(omax)
    bs_pmin, bs_pmax = _barssince(pmin), _barssince(pmax)
    with np.errstate(invalid="ignore"):
        dlow = np.where(pmin & (bs_omin < 3), l1, np.nan)
        dhigh = np.where(pmax & (bs_omax < 3), h1, np.nan)
        filt = np.where(bs_pmin < 5, _roll(ct6, 4, "min"), np.nan)
        filt2 = np.where(bs_pmax < 5, _roll(ct7, 4, "max"), np.nan)
    y2, y6 = _valuewhen(omax, filt2, 1), _valuewhen(omin, filt, 1)
    ltbull = _valuewhen(pmin, _roll(lo, L, "min"), 1)
    ltbear = _valuewhen(pmax, _roll(hi, L, "max"), 1)
    y3, y4 = _valuewhen(omax, ct5, 0), _valuewhen(omax, ct5, 1)
    y7, y8 = _valuewhen(omin, ct4, 0), _valuewhen(omin, ct4, 1)
    y9, y10 = _valuewhen(omin, ct6, 0), _valuewhen(omax, ct7, 0)
    ltd = bool(p["long_term_div"])
    with np.errstate(invalid="ignore"):
        i1 = ct5 < _roll(d, L, "max")
        i2 = y10 > ltbear
        i3 = dhigh > ltbear
        i4 = ct4 > _roll(d, L, "min")
        i5 = y9 < ltbull
        i6 = dlow < ltbull
        bear = ((y10 > y2) & omax & (y3 < y4)) | ((dhigh > y2) & (y3 < y4)) \
            | (ltd & omax & i1 & i2) | (ltd & i1 & i3)
        bull = ((y9 < y6) & omin & (y7 > y8)) | ((dlow < y6) & (y7 > y8)) \
            | (ltd & omin & i4 & i5) | (ltd & i4 & i6)
    close_long = omax & (d1 != 0) & ~np.isnan(d1)
    close_short = omin & (d1 != 0) & ~np.isnan(d1)
    m = len(d)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bull[i] and pos != 1:
            pos = 1
        elif bear[i] and pos != -1:
            pos = -1
        elif pos == 1 and close_long[i]:
            pos = 0
        elif pos == -1 and close_short[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
