"""OneTrend Lite v1.0: the EMA 30 / 60 gap crossing an ATR margin, long only, 5-minute bars: the gap crossing above
0.3 x ATR(60) goes long; crossing below -0.3 x ATR(60) closes the long.
Port of FMZ strategy #489017 "双均线趋势追踪量化策略-Dual-EMA-Trend-Following-Quantitative-Strategy" (onetrend Lite v1.0).

FMZ source id: 489017

Source
    https://www.fmz.com/strategy/489017 (PineScript v6, FMZ last modified 2025-04-01 10:59:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 143-180), EMA 30 / 60, margin 0.3 x ATR(60)
    diff = ema30 - ema60;  long = crossover(diff, 0.3 ATR) -> entry long;  sell = crossunder(diff, -0.3 ATR) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crosses compare with the margin's own previous value (Pine's crossover of two series).
    * Long only. FREQ = "5min" from the backtest header. (A later version with an ADX-scaled margin is #489311.)

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA gap in ATR units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489017_onetrend_lite_v1_ema_gap_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "margin_mult": [0.3, 0.6],
    "ema_fast": [30, 20],
}
DEFAULT_PARAMS = {"ema_fast": 30, "ema_slow": 60, "atr_len": 60, "margin_mult": 0.3}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    diff = c.ewm(span=int(p["ema_fast"]), adjust=False).mean() - c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    thr = p["margin_mult"] * _atr(bars_df, int(p["atr_len"]))
    long_e = ((diff > thr) & (diff.shift(1) <= thr.shift(1))).astype(bool)
    long_x = ((diff < -thr) & (diff.shift(1) >= -thr.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
