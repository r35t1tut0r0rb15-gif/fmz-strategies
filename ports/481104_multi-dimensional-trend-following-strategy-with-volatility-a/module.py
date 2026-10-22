"""SuperTrend (ATR 14 x 3) up-trend with RSI 14 under 65 and the close above the SMA 50, 3-hour bars, long only: such a bar buys; the SuperTrend turning down closes. The 1.5 ATR close-based ratchet stop is re-sent every bar and is not ported (pending).
Port of FMZ strategy #481104 "Multi Dimensional Trend Following Strategy with Volatility Adaptive Stop Loss" (Trend Strategy with Stop Loss).

FMZ source id: 481104

Source
    https://www.fmz.com/strategy/481104 (PineScript v5, FMZ last modified 2025-02-08 15:12:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-157), SuperTrend ATR 14 x 3; RSI 14 under 65; SMA 50; trail 1.5 x ATR 14 under the close (ratchet)
    dir < 0 and rsi < 65 and close > sma50 -> entry Long;  dir > 0 -> close Long;  trail := buy and flat ? close - 1.5 atr : max(close - 1.5 atr, trail[1]);  exit(Long, stop = trail)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend is Pine's reference ta.supertrend (direction -1 = up-trend). The stop is a ratchet
      of close - 1.5 ATR that is re-sent every bar and keeps rising even while flat until a new entry
      from flat resets it; the house trail settings cannot express a close-minus-ATR ratchet, so it is
      described here and kept pending (mark trailing_stop_pending). Long only. No sizing code. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet stop described (pending).
    2 generic: PASS, SuperTrend with RSI and SMA filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481104_supertrend14x3_rsi65_sma50_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "ma_length": [50, 100],
}
DEFAULT_PARAMS = {"factor": 3.0, "ma_length": 50, "atr_length": 14, "rsi_length": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


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
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_length"]))[1]
    r = _rsi(c, int(p["rsi_length"]))
    ma = c.rolling(int(p["ma_length"])).mean()
    le = (d < 0) & (r < 65) & (c > ma)
    lx = d > 0
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
