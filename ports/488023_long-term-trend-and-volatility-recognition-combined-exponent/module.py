"""A hand-built SuperTrend (factor 3, ATR 14) on the side of the SMA 200, 3-hour bars: an up-trend above the SMA goes long, a down-trend below it goes short; a turn of the trend closes; reversing.
Port of FMZ strategy #488023 "Long term Trend and Volatility Recognition Combined Exponential Moving Average SuperTrend Quantitative Trading Strategy" (Moving Average + SuperTrend Strategy).

FMZ source id: 488023

Source
    https://www.fmz.com/strategy/488023 (PineScript v6, FMZ last modified 2025-03-24 14:42:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 198-248), SMA 200; SuperTrend factor 3, ATR 14 (hand-built)
    trendUp := close[1] > trendUp[1] ? max(hl - 3 atr, trendUp[1]) : hl - 3 atr;  trendDown mirror with min
    trend := close > trendDown[1] ? 1 : close < trendUp[1] ? -1 : nz(trend[1], 1)
    close > sma200 and trend == 1 -> entry Buy;  close < sma200 and trend == -1 -> entry Sell;  long and trend == -1 -> close;  short and trend == 1 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trend rule is as written: any close over the previous down-line turns it up, whatever the
      previous trend. The entry conditions are states; a turn of the trend closes, and a turn that also
      meets the other side's entry reverses (REVERSAL INTENDED). No sizing code. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend states with an SMA side filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_488023_handbuilt_supertrend3_14_sma200_side_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"factor": 3.0, "ma_length": 200, "period": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["period"])).to_numpy()
    hl = ((h + lo) / 2).to_numpy()
    k = float(p["factor"])
    up, dn = hl - k * atr, hl + k * atr
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tu, td, tr_ = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    for i in range(m):
        pu = tu[i - 1] if i >= 1 else np.nan
        pd_ = td[i - 1] if i >= 1 else np.nan
        c1 = cv[i - 1] if i >= 1 else np.nan
        tu[i] = (np.nan if np.isnan(up[i]) or np.isnan(pu) else max(up[i], pu)) if c1 > pu else up[i]
        td[i] = (np.nan if np.isnan(dn[i]) or np.isnan(pd_) else min(dn[i], pd_)) if c1 < pd_ else dn[i]
        if cv[i] > pd_:
            tr_[i] = 1
        elif cv[i] < pu:
            tr_[i] = -1
        else:
            tr_[i] = tr_[i - 1] if i >= 1 else 1
    trend = pd.Series(tr_, index=c.index)
    ma = c.rolling(int(p["ma_length"])).mean()
    le = (c > ma) & (trend == 1)
    se = (c < ma) & (trend == -1)
    lx = (trend == -1) & ~se
    sx = (trend == 1) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
