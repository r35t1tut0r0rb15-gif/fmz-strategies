"""Hourly bars: a rising 3-bar Hull-style line with the close above the 3-bar VWMA, the script's ADX 14 above 20, RSI 14 between 30 and 70 and volume above its 10-bar average goes long; the mirror goes short; the opposite signal reverses.
Port of FMZ strategy #474836 "Multi Moving Average Trading System with Momentum and Volume Confirmation Quantitative Trend Strategy" (Optimized Multi-MA Strategy with Volume, ADX and RSI).

FMZ source id: 474836

Source
    https://www.fmz.com/strategy/474836 (PineScript v5, FMZ last modified 2024-12-12 14:27:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 118-178), Hull-style 3 (WMA 2 / 3, smoothing WMA 2); VWMA 3; manual ADX 14 > 20; RSI 14 30 .. 70; volume SMA 10
    n1 = wma(2 x wma(close, 2) - wma(close, 3), 2);  n2 = the same of diff[1];  longCondition = n1 > n2 and close > vwma(close, 3) and adx > 20 and 30 < rsi < 70 and volume > sma(volume, 10) -> entry Long;  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * math.round(3 / 2) is 2 (Pine v5 divides to 1.5) and round(sqrt 3) is 2. The ADX is the script's
      own: RMA of max(high - high[1], 0) and of max(low[1] - low, 0) (both kept, not compared) over the
      RMA of the true range, then the RMA of the DX. The WMA 75 only plots. Entries only, as states; an
      opposite entry reverses. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fast Hull-style slope with VWMA, ADX, RSI and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMA 3 and against its SMA 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_474836_hull3_vwma3_adx_rsi_volume_state_1h_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [3, 9],
    "adx_min": [20.0, 25.0],
}
DEFAULT_PARAMS = {"keh": 3, "teh": 3, "adx_len": 14, "adx_min": 20.0, "vol_len": 10}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k = int(p["keh"])
    half, root = int(np.floor(k / 2 + 0.5)), int(np.floor(np.sqrt(k) + 0.5))   # Pine math.round
    diff = 2 * _wma(c, half) - _wma(c, k)
    n1, n2 = _wma(diff, root), _wma(diff.shift(1), root)
    t = int(p["teh"])
    vw = (c * v).rolling(t).mean() / v.rolling(t).mean()
    n = int(p["adx_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    pdi = _rma((h - h.shift(1)).clip(lower=0), n) / trr * 100
    mdi = _rma((lo.shift(1) - lo).clip(lower=0), n) / trr * 100
    adx = _rma((pdi - mdi).abs() / (pdi + mdi) * 100, n)
    r = _rsi(c, 14)
    common = (adx > float(p["adx_min"])) & (r > 30) & (r < 70) & (v > v.rolling(int(p["vol_len"])).mean())
    buy = (n1 > n2) & (c > vw) & common
    sell = (n1 < n2) & (c < vw) & common
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
