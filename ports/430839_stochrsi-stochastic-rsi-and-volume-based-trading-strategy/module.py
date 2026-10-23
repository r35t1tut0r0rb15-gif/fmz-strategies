"""The stochastic RSI 14 / 14 (K 3, D 3) K-minus-D sign flipping with volume above its 7-bar SMA, 2-hour bars: a flip to K >= D on an up bar goes long, a flip to K < D on a down bar goes short; reversing.
Port of FMZ strategy #430839 "基于StochRSI和交易量的多空策略Stochastic-RSI-and-Volume-Based-Trading-Strategy" (StochRSI Volume Strategy).

FMZ source id: 430839

Source
    https://www.fmz.com/strategy/430839 (PineScript v5, FMZ last modified 2023-11-02 14:12:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-180), RSI 14, stochastic 14, K 3, D 3; volume SMA 7
    level = k - d >= 0 ? 1 : -1;  level > -1 and level[1] <= -1 and close > open and volume > sma(volume, 7) -> entry Buy;  level < 1 and level[1] >= 1 and close < open and volume > sma -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * An undefined K - D (early bars) counts as level -1 (the na comparison is false), as written.
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic-RSI cross with volume confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > sma(volume, 7); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430839_stoch_rsi_kd_flip_volume_candle_reversal"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_rsi": [14, 21],
    "vol_len": [7, 20],
}
DEFAULT_PARAMS = {"length_rsi": 14, "vol_len": 7, "length_stoch": 14, "smooth_k": 3, "smooth_d": 3}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    d_ = c.diff()
    n = int(p["length_rsi"])
    r = 100 - 100 / (1 + _rma(d_.clip(lower=0), n) / _rma((-d_).clip(lower=0), n))
    ns = int(p["length_stoch"])
    st = 100 * (r - r.rolling(ns).min()) / (r.rolling(ns).max() - r.rolling(ns).min()).replace(0.0, np.nan)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    level = pd.Series(np.where(k - d >= 0, 1, -1), index=c.index)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    le = (level > -1) & (level.shift(1) <= -1) & (c > o) & vol_ok
    se = (level < 1) & (level.shift(1) >= 1) & (c < o) & vol_ok
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
