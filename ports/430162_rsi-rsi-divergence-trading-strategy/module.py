"""RSI / price regression divergence (faytterro), 4-hour bars: over the last 14 bars a rising least-squares line of RSI 14
with a falling line of the close (and no such bar in the 7 before) goes long; the mirror goes short; each position has
a 25 % target, a 5 % stop and a trailing stop.
Port of FMZ strategy #430162 "RSI指标背离交易策略RSI-Divergence-Trading-Strategy" (RSI Divergence Strategy).

FMZ source id: 430162

Source
    https://www.fmz.com/strategy/430162 (PineScript v5, FMZ last modified 2023-10-25 16:47:14).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 204-327), RSI 14, divergence length 14, TP 25 %, stop 5 %, trailing offset close x 0.25 ticks
    a = least-squares slope of rsi over the last 14 bars; a2 = slope of close over the last 14 bars
    ttk = a > 0 and a2 < 0 ? 1 : a < 0 and a2 > 0 ? -1 : 0
    long: ttk == 1 and highest(ttk[1], 7) < 1 -> entry long; exit(limit = close x 1.25, stop = close x 0.95,
          trail_price = close, trail_offset = close x 0.25)            (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * dizi[0] < dizi[1] is the sign of the slope a (the line a x i + b), the same for a2; the bug
      b2 = yo2 - a x xo2 changes only the intercept, which the comparison does not use. The
      lines drawn from barssince(cg / cr) only plot.
    * Criterion 2: trail_offset is in ticks: close x 0.25 ticks is 2.5 % of the close at the header
      market's 0.1 tick (BTC_USDT). The trail is ported natively (mark trailing_stop) as
      {"type": "percent", "pct": 0.025, "anchor": "high_low"}; trail_price = close activates it at the
      signal close, which the fill reaches at once (no activate_after; stated approximation). With the
      5 % stop the tighter level applies (house rule).
    * The 25 % target and 5 % stop are fractions of the signal close, used as fractions of the fill.
      The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket and trail fixed at entry.
    2 generic: ADAPT, the tick-based trail offset -> 2.5 % of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430162_rsi_regression_divergence"
FAMILY = "macd_divergence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 28],
    "trail_pct": [0.025, 0.05],
}
DEFAULT_PARAMS = {"rsi_len": 14, "length": 14, "tp_pct": 25.0, "sl_pct": 5.0, "trail_pct": 0.025}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _slope(y, n):
    """Least-squares slope over the last n values, oldest at x = 0."""
    w = np.arange(n, dtype=float) - (n - 1) / 2
    ww = float(np.dot(w, w))
    return y.rolling(n).apply(lambda a: np.dot(a, w) / ww, raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    a = _slope(_rsi(c, int(p["rsi_len"])), n)
    a2 = _slope(c, n)
    ttk = pd.Series(np.where((a > 0) & (a2 < 0), 1, np.where((a < 0) & (a2 > 0), -1, 0)), index=c.index)
    half = max(int(n / 2), 1)
    prev_hi = ttk.shift(1).rolling(half).max()
    prev_lo = ttk.shift(1).rolling(half).min()
    long_e = ((ttk == 1) & (prev_hi < 1)).astype(bool)
    short_e = ((ttk == -1) & (prev_lo > -1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100,
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
