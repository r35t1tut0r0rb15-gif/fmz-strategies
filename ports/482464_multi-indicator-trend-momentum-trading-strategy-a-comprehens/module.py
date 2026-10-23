"""Hourly bars, long only: a close above the 20-bar Bollinger basis with RSI 14 over 50 and a rising OBV (its EMA 10 above the EMA 10 of the previous bar's OBV) goes long; a close under the lower band (20, 2) closes it.
Port of FMZ strategy #482464 "Multi Indicator Trend Momentum Trading Strategy A Comprehensive Quantitative Trading System Based on Bollinger Bands RSI and OBV" (Istanbul Stratejisi).

FMZ source id: 482464

Source
    https://www.fmz.com/strategy/482464 (PineScript v5, FMZ last modified 2025-02-18 15:24:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 103-146), BB 20 x 2; RSI 14 vs 50; OBV = cum(volume x sign(change)); EMA 10 trend
    buyCondition = close > basis and rsi > 50 and ema(obv, 10) > ema(obv[1], 10) -> entry Long;  sellCondition = close < lowerBand -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a state and an entry while long adds nothing; a buy (close above the basis) and a sell
      (close under the lower band) never meet on one bar. The first bar's OBV step is 0. Pine's stdev is
      the population deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, basis-side momentum with OBV trend, lower-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482464_bb_basis_rsi_obv_trend_lower_band_exit_1h_long_only"
FAMILY = "bollinger_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 40],
    "rsi_mid": [50.0, 55.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_mid": 50.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["bb_len"])
    basis, dev = c.rolling(n).mean(), float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, 14)
    obv = (v * np.sign(c.diff())).fillna(0.0).cumsum()
    trend = obv.ewm(span=10, adjust=False).mean() > obv.shift(1).ewm(span=10, adjust=False).mean()
    entry = (c > basis) & (r > float(p["rsi_mid"])) & trend
    ex = c < basis - dev
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
