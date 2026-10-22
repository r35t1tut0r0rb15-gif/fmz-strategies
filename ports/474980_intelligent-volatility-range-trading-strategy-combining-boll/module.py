"""Bollinger 20 / 2 band re-tests with the supertrend (3, 10), 5-minute bars: a low crossing back over the lower band while Pine's supertrend direction is over 0 (a down-trend, as written) goes long, a high crossing under the upper band while it is under 0 goes short; a close crossing the supertrend line the other way closes; reversing.
Port of FMZ strategy #474980 "Intelligent Volatility Range Trading Strategy Combining Bollinger Bands and SuperTrend" (Bollinger Band & SuperTrend Strategy (Standard Chart)).

FMZ source id: 474980

Source
    https://www.fmz.com/strategy/474980 (PineScript v5, FMZ last modified 2024-12-13 11:47:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-181), BB 20, 2 sd; supertrend 3.0 / 10; 100 % of equity
    crossover(low, lower) and direction > 0 -> entry Buy;  crossunder(high, upper) and direction < 0 -> entry Sell;  crossunder(close, supertrend) and direction < 0 -> close Buy;  crossover(close, supertrend) and direction > 0 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's supertrend direction is 1 in a down-trend and -1 in an up-trend; the tests are kept as
      written. A close coinciding with the opposite entry only repeats the reversal (#437773), so it is
      masked on entry bars. REVERSAL INTENDED. The equity share is not ported. FREQ = "5min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-tests with supertrend filters and line-cross closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_474980_bb20_retest_supertrend_dir_line_cross_exit_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_bb": [20, 50],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length_bb": 20, "factor": 3.0, "atr_length": 10}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_bb"])
    basis = c.rolling(n).mean()
    dev = 2.0 * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    st, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_length"]))
    le = (lo > dn) & (lo.shift(1) <= dn.shift(1)) & (d > 0)
    se = (h < up) & (h.shift(1) >= up.shift(1)) & (d < 0)
    xb = (c < st) & (c.shift(1) >= st.shift(1)) & (d < 0)
    xs = (c > st) & (c.shift(1) <= st.shift(1)) & (d > 0)
    return le, xb & ~se, se, xs & ~le


def portfolio_kwargs(**params):
    return {}
