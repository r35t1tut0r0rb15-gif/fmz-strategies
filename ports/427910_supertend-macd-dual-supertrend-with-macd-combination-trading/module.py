"""Dual SuperTrend with MACD, 30-minute bars: both SuperTrends (3 x ATR 10 and 5 x ATR 20) up with a
positive MACD histogram goes long, both down with a negative histogram goes short; a long closes as
soon as either SuperTrend turns down or the histogram turns negative (shorts mirror).
Port of FMZ strategy #427910 "Dual SuperTrend with MACD Combination Trading Strategy".

FMZ source id: 427910

Source
    https://www.fmz.com/strategy/427910 (PineScript v5, FMZ last modified 2023-09-26 17:45:03).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 298-349), MACD 12/26/9 EMA, SuperTrend 3 x 10 and 5 x 20
    isBullish = direction1 < 0 and direction2 < 0 and hist > 0 -> entry long
    isBearish = direction1 > 0 and direction2 > 0 and hist < 0 -> entry short
    exitLong = direction1 > 0 or direction2 > 0 or hist < 0 -> close long; exitShort mirrors

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as in Pine v5 (worker A's helper from #359806); direction < 0 is an up trend.
    * The strategy() line is commented out: Pine defaults (one position). Trading direction "both" (default).
    * An opposite entry reverses (the close on that bar is redundant): REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples and MACD lengths.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427910_dual_supertrend_macd"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor1": [3.0, 2.0],
    "factor2": [5.0, 3.0],
    "atr1": [10, 14],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "atr1": 10, "factor1": 3.0, "atr2": 20, "factor2": 5.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _atr_pine(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = bars["high"].iloc[0] - bars["low"].iloc[0]   # ta.tr(true) on the first bar
    return _rma(tr, n)


def _supertrend(bars, factor, atr_period):
    """ta.supertrend(factor, atrPeriod) as in Pine v5: returns (supertrend, direction);
    direction < 0 is an up-trend."""
    atr = _atr_pine(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    st, dirn = np.full(m, np.nan), np.full(m, np.nan)
    lower_prev = upper_prev = 0.0      # nz(...[1])
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st[i] = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
        st_prev = st[i]
    return pd.Series(st, index=bars.index), pd.Series(dirn, index=bars.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = (macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()).to_numpy()
    _, d1 = _supertrend(bars_df, float(p["factor1"]), int(p["atr1"]))
    _, d2 = _supertrend(bars_df, float(p["factor2"]), int(p["atr2"]))
    d1, d2 = d1.to_numpy(), d2.to_numpy()
    bull = (d1 < 0) & (d2 < 0) & (hist > 0)
    bear = (d1 > 0) & (d2 > 0) & (hist < 0)
    x_long = (d1 > 0) | (d2 > 0) | (hist < 0)
    x_short = (d1 < 0) | (d2 < 0) | (hist > 0)
    m = len(hist)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bull[i]:
            pos = 1
        elif bear[i]:
            pos = -1
        elif pos == 1 and x_long[i]:
            pos = 0
        elif pos == -1 and x_short[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
