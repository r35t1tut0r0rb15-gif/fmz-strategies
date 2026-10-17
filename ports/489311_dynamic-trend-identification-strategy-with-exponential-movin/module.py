"""EMA 30 / 60 gap beyond an ADX-scaled ATR threshold, long only, hourly bars: when EMA 30 is above EMA 60 by more than
0.3 ATR(60) (0.1 ATR when ADX 14 is 20 or below) the strategy goes long; when it is below by as much the long closes.
Port of FMZ strategy #489311 "动态趋势识别策略与指数移动平均线和自适应波动阈值-Dynamic-Trend-Identification-Strategy-with-Exponential-Moving-Average-and-Adaptive-Volatility-Threshold" (OneTrend Lite EMA).

FMZ source id: 489311

Source
    https://www.fmz.com/strategy/489311 (PineScript v6, FMZ last modified 2025-04-03 13:08:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 155-205), EMA 30 / 60, ATR 60, ADX 14 > 20 -> 0.3 else 0.1
    diff = ema30 - ema60;  mult = adx > 20 ? 0.3 : 0.1
    bull = diff > mult x ATR(60) -> entry long;  bear = diff < -mult x ATR(60) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI is the source's own: plusDM / minusDM are 0 where the change is na, ta.tr is na on the first bar, Wilder
      rma smoothing; dx is na where plusDI + minusDI is 0.
    * The performance tables in the source's comments are FMZ / author claims: ignored (criterion 7).
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA gap in ATR units and ADX.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG489311 (2 members, best partner #490075, Jaccard 1.000, not an exact duplicate); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489311_onetrend_lite_ema_gap_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [30, 20],
    "atr_mult_strong": [0.3, 0.6],
}
DEFAULT_PARAMS = {"ema_fast": 30, "ema_slow": 60, "atr_len": 60, "adx_len": 14, "adx_threshold": 20,
                  "atr_mult_strong": 0.3, "atr_mult_weak": 0.1}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    diff = c.ewm(span=int(p["ema_fast"]), adjust=False).mean() - c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    up, down = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=c.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=c.index)
    n = int(p["adx_len"])
    tr = _tr(bars_df)
    trur = _rma(tr, n)
    pdi, mdi = 100 * _rma(plus_dm, n) / trur, 100 * _rma(minus_dm, n) / trur
    s = pdi + mdi
    dx = (100 * (pdi - mdi).abs() / s).where(s != 0)
    adx = _rma(dx, n)
    atr_full = tr.copy()
    atr_full.iloc[0] = h.iloc[0] - lo.iloc[0]          # ta.atr's first true range is high - low
    atr = _rma(atr_full, int(p["atr_len"]))
    mult = pd.Series(np.where(adx > p["adx_threshold"], p["atr_mult_strong"], p["atr_mult_weak"]), index=c.index)
    bull = (diff > mult * atr).astype(bool)
    bear = (diff < -mult * atr).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return bull, bear, false, false.copy()


def portfolio_kwargs(**params):
    return {}
