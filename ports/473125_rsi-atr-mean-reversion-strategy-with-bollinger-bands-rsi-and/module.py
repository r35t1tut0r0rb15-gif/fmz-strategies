"""Bollinger 20 / 2 and RSI 14 extremes, 15-minute bars: a close under the lower band with the RSI under 30 goes long, the mirror goes short; a long closes on a close over the middle band or an RSI over 70, a short on the mirror; each trade also has a 2 ATR stop and 3 ATR target from the fill; reversing.
Port of FMZ strategy #473125 "均值回归型布林带RSI策略结合ATR动态止损优化系统-Mean-Reversion-Strategy-with-Bollinger-Bands-RSI-and-ATR-Based-Dynamic-Stop-Loss-System" (SOL/USDT Mean Reversion Strategy).

FMZ source id: 473125

Source
    https://www.fmz.com/strategy/473125 (PineScript v5, FMZ last modified 2024-11-27 14:28:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-137), BB 20, 2; RSI 14, 30 / 70; ATR 14: stop 2 x, target 3 x from the average price (re-sent every bar with that bar's ATR)
    close < lower and rsi < 30 -> entry Long;  close > upper and rsi > 70 -> entry Short;  close > middle or rsi > 70 -> close Long;  close < middle or rsi < 30 -> close Short
    every bar: exit(Long, stop = avg - 2 atr, limit = avg + 3 atr);  exit(Short, mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are bar-close tests filled at the next open; they give way to an entry on the same
      bar. The bracket comes from the average (fill) price but moves with each bar's ATR: ported with the
      ATR of the bar before the fill as fractions of the fill (active from the fill bar, #440797); the
      bar-by-bar ATR movement cannot be expressed (mark trailing_stop_pending). The title names SOL; the
      rules are generic. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR levels from the fill.
    2 generic: PASS, band and RSI extremes with mean exits and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only (SOL named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473125_bb20_rsi_extreme_mean_exit_atr_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "std_dev": [2.0, 2.5],
    "sl_atr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "std_dev": 2.0, "sl_atr": 2.0, "tp_atr": 3.0, "rsi_len": 14, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    mid = c.rolling(n).mean()
    dev = float(p["std_dev"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < mid - dev) & (r < 30)
    se = (c > mid + dev) & (r > 70)
    lx = ((c > mid) | (r > 70)) & ~le & ~se
    sx = ((c < mid) | (r < 30)) & ~le & ~se
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
