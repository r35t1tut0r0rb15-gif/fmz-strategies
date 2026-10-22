"""Three SuperTrends (ATR 10 x 3 / 2 / 1) agreeing with the close on one side of the EMA 50, 45-minute bars: all up with the close above goes long, all down below goes short; the fastest SuperTrend turning against the position closes it; reversing.
Port of FMZ strategy #476281 "Triple Supertrend and Exponential Moving Average Trend Following Quantitative Trading Strategy" (Supertrend EMA Strategy).

FMZ source id: 476281

Source
    https://www.fmz.com/strategy/476281 (PineScript v5, FMZ last modified 2024-12-27 15:56:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-144), EMA 50; SuperTrend ATR 10, factors 3 / 2 / 1
    dir1 == dir2 == dir3 == -1 and close > ema50 -> entry Long;  all == 1 and close < ema50 -> entry Short;  dir3 == 1 -> close Long;  dir3 == -1 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrends are Pine's reference ta.supertrend (direction -1 = up-trend). A close acts only on
      the held position and leaves a same-bar reversal standing (as #441963). REVERSAL INTENDED. No
      sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, triple SuperTrend agreement with an EMA filter.
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

NAME = "fmz_476281_triple_supertrend_ema50_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [50, 200],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"ema_length": 50, "atr_period": 10}


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
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    k = int(p["atr_period"])
    d1, d2, d3 = (_supertrend(bars_df, f, k)[1] for f in (3.0, 2.0, 1.0))
    le = (d1 == -1) & (d2 == -1) & (d3 == -1) & (c > e)
    se = (d1 == 1) & (d2 == 1) & (d3 == 1) & (c < e)
    return le, (d3 == 1) & ~se, se, (d3 == -1) & ~le


def portfolio_kwargs(**params):
    return {}
