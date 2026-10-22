"""RSI 14 extremes beyond two EMAs, 1-hour bars: a close under the EMA 100 and the EMA 20 of lows with the RSI at 30 or less goes long, a close above both with the RSI at 70 or more goes short; reversing.
Port of FMZ strategy #449553 "RSI与双EMA交叉信号量化策略-RSI-and-Dual-EMA-Crossover-Signal-Quantitative-Strategy" (RSI-EMA100&20 Buy/Sell Signal).

FMZ source id: 449553

Source
    https://www.fmz.com/strategy/449553 (PineScript v5, FMZ last modified 2024-04-26 17:36:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-161), RSI 14, levels 30 / 70; EMA 100 of close; EMA 20 of low
    close < ema100 and close < ema20(low) and rsi <= 30 -> entry Buy;  close > both and rsi >= 70 -> entry Sell (sent twice)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry is written twice; the second call repeats the first. Both conditions are
      levels, so a repeated entry on the held side is ignored. No exit: positions end at the opposite
      entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes beyond two EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_449553_rsi_extreme_beyond_ema100_ema20low_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "ema_close": [100, 200],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ema_close": 100, "ema_low": 20, "os": 30.0, "ob": 70.0}


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
    lo, c = bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ec = c.ewm(span=int(p["ema_close"]), adjust=False).mean()
    el = lo.ewm(span=int(p["ema_low"]), adjust=False).mean()
    le = (c < ec) & (c < el) & (r <= float(p["os"]))
    se = (c > ec) & (c > el) & (r >= float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
