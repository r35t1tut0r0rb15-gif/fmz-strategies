"""Hourly bars: a close under the bar's own hlc3 with RSI 8 under 30 goes long; a close over hlc3 with RSI 8 over 70 goes short; reversing.
Port of FMZ strategy #442832 "Trend Following Quant Trading Strategy Based on Moving Average" (Verbesserte VWAP Strategie mit RSI Filter).

FMZ source id: 442832

Source
    https://www.fmz.com/strategy/442832 (PineScript v5, FMZ last modified 2024-02-26 13:45:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 155-179), VWAP length 5 (passed as the anchor); RSI 8, 70 / 30; SMA 25 and the deviation multiplier unused
    vwapValue = ta.vwap(hlc3, length = 5);  buySignal = close < vwapValue and rsi(close, 8) < 30 -> entry Buy;  sellSignal = close > vwapValue and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap(hlc3, 5) passes 5 as the reset anchor (true on every bar), so the "VWAP" restarts each bar
      and equals that bar's hlc3; volume cancels out (weird case; held for volume, not used). The SMA
      trend filter and the deviation multiplier feed nothing. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against its own hlc3 at RSI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h; the VWAP resets every bar).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442832_close_vs_hlc3_rsi8_extremes_1h_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [8, 14],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"rsi_period": 8, "oversold": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hlc3 = (h + lo + c) / 3
    r = _rsi(c, int(p["rsi_period"]))
    os_ = float(p["oversold"])
    buy = (c < hlc3) & (r < os_)
    sell = (c > hlc3) & (r > 100 - os_)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
