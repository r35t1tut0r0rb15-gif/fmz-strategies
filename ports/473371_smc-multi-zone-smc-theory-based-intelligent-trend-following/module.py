"""Swing-range halves with the SMA 50 trend, 5-minute bars: the last 8-bar swing high and low set an equilibrium; a close between the swing low and the equilibrium over the SMA goes long, between the equilibrium and the swing high under the SMA goes short; reversing.
Port of FMZ strategy #473371 "基于多区域SMC理论的智能趋势跟踪策略Multi-Zone-SMC-Theory-Based-Intelligent-Trend-Following-Strategy" (SMC Strategy with Premium, Equilibrium, and Discount Zones).

FMZ source id: 473371

Source
    https://www.fmz.com/strategy/473371 (PineScript v5, FMZ last modified 2024-11-29 15:38:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-193), swing length 8 / 8; SMA 50; order-block length 20; 10 % of equity
    highestbars(high, 8) == 0 -> swingHigh := high;  lowestbars(low, 8) == 0 -> swingLow := low;  eq = (swingHigh + swingLow) / 2;  close < eq and close > swingLow and close > sma and close >= lowest(low, 20) -> entry Buy;  close > eq and close < swingHigh and close < sma and close <= highest(high, 20) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels are kept from the last bar that was the highest high / lowest low of its 8-bar
      window (a tie with an earlier bar counts as the current bar; a loop). The order-block tests always
      hold (a close is never under the 20-bar lowest low or over the 20-bar highest high), so they feed
      nothing. The two setups cannot hold on one bar (the close is on opposite sides of the SMA). There
      is no exit: positions end at the opposite entry. REVERSAL INTENDED. The equity share is not
      ported. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing-range zones with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_473371_swing8_equilibrium_zones_sma50_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "swing_len": [8, 16],
    "sma_len": [50, 100],
}
DEFAULT_PARAMS = {"swing_len": 8, "sma_len": 50}


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


def _kept(level, hit):
    """The level of the last bar where `hit` held (na before the first), as a var."""
    v, k = level.to_numpy(dtype=float), hit.to_numpy()
    out = np.full(len(v), np.nan)
    cur = np.nan
    for i in range(len(v)):
        if k[i]:
            cur = v[i]
        out[i] = cur
    return pd.Series(out, index=level.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["swing_len"])
    sh = _kept(h, h >= h.rolling(n).max())
    sl = _kept(lo, lo <= lo.rolling(n).min())
    eq = (sh + sl) / 2
    ma = c.rolling(int(p["sma_len"])).mean()
    le = (c < eq) & (c > sl) & (c > ma)
    se = (c > eq) & (c < sh) & (c < ma)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
