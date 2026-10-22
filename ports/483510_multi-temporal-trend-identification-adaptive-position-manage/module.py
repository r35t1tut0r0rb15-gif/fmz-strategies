"""Close crossings of the SuperTrend 3 / 10 line with a DEMA 100 side, 5-minute bars: crossing up above the DEMA goes long (reversing a short), crossing down below it goes short; a crossing that fails the DEMA test only closes the other side; reversing.
Port of FMZ strategy #483510 "Multi Temporal Trend Identification Adaptive Position Management Strategy" (Supertrend with DEMA Strategy (Reversal Enabled)).

FMZ source id: 483510

Source
    https://www.fmz.com/strategy/483510 (PineScript v6, FMZ last modified 2025-02-27 16:49:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-183), SuperTrend factor 3, ATR 10 (line na on the first bar); DEMA 100; long and short allowed
    longSignal = crossover(close, supertrend) and close > dema;  shortSignal = crossunder(close, supertrend) and close < dema
    longSignal: short -> close Short + entry Long;  flat -> entry Long;  shortSignal mirror
    crossover(close, supertrend) and not longSignal and short -> close Short;  crossunder and not shortSignal and long -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both directions are allowed by default. A long signal while long adds nothing. Each signal closes the
      other side and enters (REVERSAL INTENDED); a crossing failing the DEMA test closes the other side
      only. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend line crossings with a DEMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483510_close_supertrend3_10_cross_dema100_side_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "dema_length": [100, 50],
}
DEFAULT_PARAMS = {"factor": 3.0, "dema_length": 100, "atr_period": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[0]
    st.iloc[0] = np.nan                       # barstate.isfirst -> na
    n = int(p["dema_length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    up = (c > st) & (c.shift(1) <= st.shift(1))
    dn = (c < st) & (c.shift(1) >= st.shift(1))
    le, se = up & (c > dema), dn & (c < dema)
    return le, dn & ~se & ~le, se, up & ~le & ~se


def portfolio_kwargs(**params):
    return {}
