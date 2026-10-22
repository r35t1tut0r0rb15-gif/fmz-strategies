"""RSI 14 re-entries after a divergence has ever been seen, 3-hour bars: the RSI crossing back over 30 goes long and back under 70 goes short, each only once its divergence flag has been set; reversing.
Port of FMZ strategy #452701 "基于RSI背离的趋势反转交易策略-Trend-Reversal-Trading-Strategy-Based-on-RSI-Divergence" (RSI Divergence Strategy).

FMZ source id: 452701

Source
    https://www.fmz.com/strategy/452701 (PineScript v5, FMZ last modified 2024-05-28 11:51:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-140), RSI 14, levels 30 / 70; divergence lookback 5
    bullDiv: var flag set when any of the last 5 bars has a lower low with a higher RSI (never reset);  bullDiv and crossover(rsi, 30) -> entry Buy
    bearDiv: var flag set when any of the last 5 bars has a higher high with a lower RSI;  bearDiv and crossunder(rsi, 70) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each divergence flag is a var inside its function, set to true and never set back to false, so
      after the first bullish (bearish) divergence of the data every RSI re-entry over 30 (under 70)
      enters; the port keeps the latch as written. The two entries cannot meet on one bar. There is no
      exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h" from
      the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI re-entries behind a latched divergence flag.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
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

NAME = "fmz_452701_rsi_reentry_latched_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "lookback": [5, 10],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lookback": 5, "os": 30.0, "ob": 70.0}


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
    r = _rsi(c, int(p["rsi_len"]))
    k = int(p["lookback"])
    bull_now = pd.Series(False, index=c.index)
    bear_now = pd.Series(False, index=c.index)
    for i in range(1, k + 1):
        bull_now |= (lo.shift(i) < lo) & (r.shift(i) > r)
        bear_now |= (h.shift(i) > h) & (r.shift(i) < r)
    bull = bull_now.cummax()                  # var flag: set once, never reset
    bear = bear_now.cummax()
    os_, ob = float(p["os"]), float(p["ob"])
    le = bull & (r > os_) & (r.shift(1) <= os_)
    se = bear & (r < ob) & (r.shift(1) >= ob)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
