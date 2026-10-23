"""A Wilder RSI 30 with a VWMA 30 / 200 trend filter, hourly bars: the VWMA 30 above the VWMA 200 with RSI at or under 53 goes long, below with RSI at or over 60 goes short; reversing.
Port of FMZ strategy #429562 "双移动均线与RSI反转交易策略Dual-Moving-Average-and-RSI-Reversal-Trading-Strategy" (_CM_RSI_2_Strat_Low).

FMZ source id: 429562

Source
    https://www.fmz.com/strategy/429562 (PineScript v4, FMZ last modified 2023-10-18 11:08:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-175), RSI 30 (down == 0 -> 100); VWMA 30 / 200 (named ma50 / ma200); levels 53 / 60
    long = vwma(close, 30) > vwma(close, 200) and rsi <= 53 -> entry buy;  short = vwma(30) < vwma(200) and rsi >= 60 -> entry sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are volume weighted (VWMA) though named ma50 / ma200, as written. The entries are sent
      every bar the conditions hold (repeats ignored). REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI pullbacks in a VWMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(close, 30) and vwma(close, 200); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429562_rsi30_vwma30_200_trend_pullback_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_long": [53.0, 40.0],
    "rsi_short": [60.0, 70.0],
}
DEFAULT_PARAMS = {"rsi_long": 53.0, "rsi_short": 60.0, "rsi_len": 30, "fast": 30, "slow": 200}


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
    c, v = bars_df["close"], bars_df["volume"]
    d = c.diff()
    n = int(p["rsi_len"])
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    vw = lambda k: (c * v).rolling(k).sum() / v.rolling(k).sum()
    f, s = vw(int(p["fast"])), vw(int(p["slow"]))
    le = (f > s) & (rsi <= float(p["rsi_long"]))
    se = (f < s) & (rsi >= float(p["rsi_short"]))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
