"""Faytterro estimator, broker days: a triangular-weighted average of hlc3 (19 bars) is extrapolated as a
parabola; when the extrapolation turns up below the average 10 bars back and the close sits well below
the last signal's close and the recent sell levels, go long; the mirror goes short.
Port of FMZ strategy #427588 "Trading Strategy Based on Faytterro Estimator".

FMZ source id: 427588

Source
    https://www.fmz.com/strategy/427588 (PineScript v5, FMZ last modified 2023-09-22 14:12:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 207-248), length 10, gaps 500 / 500, look-back 100
    cr = sum_{i=0..18} hlc3[i] x (10 - |i - 9|) / 100
    dizi(k) = k (k - 1) / 2 x (cr - 2 cr[1] + cr[2]) + k (cr[1] - cr[2]) + cr[2]
    buy0 = dizi(16) > dizi(15) and dizi(16) < cr[10]; sell0 mirrors
    X = close at the last buy0 / sell0 bar before this one
    buy = buy0 and close < X - 500 and close < highest(fixnan(sell0 ? hlc3 : na), 100) - 500 (sell mirrors)
    ("strong" versions need 3 x 500 and add width units)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the two 500 gaps are price units; they become `gap_atr` x Wilder ATR(14) of the
      bar (on the source's daily BTC bars 500 USD is about half an ATR; judgement before any
      backtest). The strong entries are a subset of the plain ones with extra units: sizing.
    * The strategy() line (pyramiding 100) is commented out: Pine defaults, one position.
    * fixnan carries the last sell level forward in time (causal).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the estimator uses past bars only.
    2 generic: ADAPT, price-unit gaps -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strong-entry width (units) stored in original_sizing.txt.
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

NAME = "fmz_427588_faytterro_estimator"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "gap_atr": [0.5, 0.25, 1.0],
}
DEFAULT_PARAMS = {"length": 10, "gap_atr": 0.5, "lookback": 100, "atr_length": 14}


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
    hlc3 = (h + lo + c) / 3
    n = int(p["length"])
    y = 2 * n - 1
    mid = (y - 1) / 2
    w = np.array([mid + 1 - abs(i - mid) for i in range(y)], dtype=float)   # weight of x[i], i bars back
    den = ((y + 1) / 2) * (y + 1) / 2
    cr = hlc3.rolling(y).apply(lambda v: np.dot(v[::-1], w) / den, raw=True)
    a = cr - 2 * cr.shift(1) + cr.shift(2)
    b = cr.shift(1) - cr.shift(2)
    k1, k0 = n + 6, n + 5

    def dizi(k):
        return k * (k - 1) / 2 * a + k * b + cr.shift(2)

    d1, d0 = dizi(k1), dizi(k0)
    buy0 = ((d1 > d0) & (d1 < cr.shift(n))).to_numpy()
    sell0 = ((d1 < d0) & (d1 > cr.shift(n))).to_numpy()
    cv, hv = c.to_numpy(dtype=float), hlc3.to_numpy(dtype=float)
    m = len(cv)
    x_prev = np.full(m, np.nan)            # close at the last raw signal BEFORE this bar
    last = np.nan
    ss_fix, bb_fix = np.full(m, np.nan), np.full(m, np.nan)
    ls_lvl = lb_lvl = np.nan
    for i in range(m):
        x_prev[i] = last
        if buy0[i] or sell0[i]:
            last = cv[i]
        if sell0[i]:
            ls_lvl = hv[i]
        if buy0[i]:
            lb_lvl = hv[i]
        ss_fix[i], bb_fix[i] = ls_lvl, lb_lvl
    lb = int(p["lookback"])
    hi_ss = pd.Series(ss_fix).rolling(lb).max().to_numpy()
    lo_bb = pd.Series(bb_fix).rolling(lb).min().to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    gap = (p["gap_atr"] * _rma(tr, int(p["atr_length"]))).to_numpy()
    with np.errstate(invalid="ignore"):
        buy = buy0 & (cv < x_prev - gap) & (cv < hi_ss - gap)
        sell = sell0 & (cv > x_prev + gap) & (cv > lo_bb + gap)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i] and pos != 1:
            pos = 1
        elif sell[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
