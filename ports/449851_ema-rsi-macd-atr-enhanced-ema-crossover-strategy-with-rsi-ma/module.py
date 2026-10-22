"""EMA 8 / 14 crossings with RSI, MACD and rising-ATR filters, 1-hour bars, with a fixed-point bracket: a cross up with the RSI under 70, the MACD over its signal and the ATR 10 % above its previous value
goes long, the mirror goes short; stop 100 and target 200 price units from the signal close; reversing.
Port of FMZ strategy #449851 "EMA与RSI-MACD-ATR结合的双均线交叉策略-Enhanced-EMA-Crossover-Strategy-with-RSI-MACD-ATR" (Enhanced EMA Crossover Strategy).

FMZ source id: 449851

Source
    https://www.fmz.com/strategy/449851 (PineScript v4, FMZ last modified 2024-04-29 17:33:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-133), EMA 8 / 14; RSI 14; MACD 12 / 26 / 9; ATR 14 > 1.1 x previous; stop 100, target 200 points
    crossover(ema8, ema14) and rsi < 70 and macd > signal and atr > 1.1 atr[1] -> entry Long, exit(stop = close - 100, limit = close + 200);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 100 / 200 price-unit distances are fractions of the price, 0.00238 / 0.00476
      against BTC near 42000, ported as sl_stop / tp_stop of the fill (re-based). A repeated signal
      inside the trade re-issues the levels from that bar's close: not expressible (mark
      trailing_stop_pending). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-sent levels marked).
    2 generic: PASS, EMA crossings with RSI, MACD and volatility filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_449851_ema8_14_cross_rsi_macd_atr_rise_point_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.00238, 0.01],
    "atr_rise": [1.1, 1.0],
}
DEFAULT_PARAMS = {"sl_frac": 0.00238, "atr_rise": 1.1, "rr": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=8, adjust=False).mean()
    s = c.ewm(span=14, adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, 14)
    vol = atr > atr.shift(1) * float(p["atr_rise"])
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70) & (macd > sig) & vol
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30) & (macd < sig) & vol
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = float(p["sl_frac"])
    return {"sl_stop": sl, "tp_stop": sl * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
