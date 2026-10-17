"""RSI 14 crossings into the extremes with a 1 % stop and a 2 % target, 1-hour bars: RSI falling to 30 or below goes long;
RSI rising to 70 or above goes short; each trade has a 1 % stop and a 2 % target.
Port of FMZ strategy #485283 "RSI反转斐波那契布林带量化策略-RSI-Reversal-Fibonacci-Bollinger-Bands-Quantitative-Strategy" (BRAHIM KHATTARA ).

FMZ source id: 485283

Source
    https://www.fmz.com/strategy/485283 (PineScript v6, FMZ last modified 2025-03-20 11:42:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 184-212), RSI 14 (30 / 70), SL 1 %, TP 2 %
    oversold = rsi <= 30 and rsi[1] > 30 -> entry long;  overbought = rsi >= 70 and rsi[1] < 70 -> entry short
    in a position, every bar: exit(limit = close x (1 +- 2 %), stop = close x (1 -+ 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-issued every bar from the current close (moving): fixed at entry, mark trailing_stop_pending
      (sl_stop 1 %, tp_stop 2 % of the fill, scalars).
    * The Fibonacci VWMA bands (lines 224-257) are drawn only and take no part in the orders.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-issue marked).
    2 generic: PASS, an oscillator and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA bands are plots only.
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_485283_rsi_extreme_cross_pct_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_os": 30, "rsi_ob": 70, "sl_pct": 1.0, "tp_pct": 2.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["rsi_len"]))
    r1 = rsi.shift(1)
    long_e = ((rsi <= p["rsi_os"]) & (r1 > p["rsi_os"])).astype(bool)
    short_e = ((rsi >= p["rsi_ob"]) & (r1 < p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
