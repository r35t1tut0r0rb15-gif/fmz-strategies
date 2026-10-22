"""A one-pole smoothed close (b = exp(-1.414 pi / 100)) with a 2 % channel and Stochastic 14 / 3 / 3 extremes, hourly bars: the close crossing over the lower band with %K and %D under 20 goes long, crossing under the upper band with both over 80 goes short; the close crossing the midline or the opposite extreme closes; reversing.
Port of FMZ strategy #483073 "Trend Detection Strategy Based on Gaussian Channel and Stochastic RSI Filter" (Gaussian Channel + Stochastic RSI Filter).

FMZ source id: 483073

Source
    https://www.fmz.com/strategy/483073 (PineScript v6, FMZ last modified 2025-02-21 11:42:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-190), length 100; channel 2 %; Stochastic 14 / 3 / 3, levels 80 / 20; date range 2023-2069
    mid = na(mid[1]) ? close : (1 - b) close + b mid[1], b = exp(-1.414 x 3.14159 / 100);  high / low = mid x (1 +/- 2 %)
    crossover(close, low) and k < 20 and d < 20 -> entry Long;  crossunder(close, high) and k > 80 and d > 80 -> entry Short
    crossunder(close, mid) or overbought -> close Long;  crossover(close, mid) or oversold -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Stochastic RSI" is the Stochastic of the price, as written. The 2023-2069 date range is a
      backtest window and is dropped like other date windows. A close on the bar of an entry is masked by
      the entry; an entry on the other side reverses (REVERSAL INTENDED). No sizing code (margin 100 /
      100). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed percent channel crossings with Stochastic extremes.
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

NAME = "fmz_483073_smoothed_close_2pct_channel_stoch_extreme_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "input_length": [100, 50],
    "input_mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"input_length": 100, "input_mult": 2.0, "stoch_period": 14, "smooth_k": 3, "smooth_d": 3,
                  "ob": 80.0, "os": 20.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    b = np.exp(-1.414 * 3.14159 / int(p["input_length"]))
    cv = c.to_numpy(dtype=float)
    mid = np.full(len(cv), np.nan)
    for i in range(len(cv)):
        mid[i] = cv[i] if (i == 0 or np.isnan(mid[i - 1])) else (1 - b) * cv[i] + b * mid[i - 1]
    mid = pd.Series(mid, index=c.index)
    q = float(p["input_mult"]) / 100
    up, dn = mid * (1 + q), mid * (1 - q)
    n = int(p["stoch_period"])
    rng = h.rolling(n).max() - lo.rolling(n).min()
    k = (100 * (c - lo.rolling(n).min()) / rng.where(rng > 0)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    os_ = (k < float(p["os"])) & (d < float(p["os"]))
    ob = (k > float(p["ob"])) & (d > float(p["ob"]))
    le = (c > dn) & (c.shift(1) <= dn.shift(1)) & os_
    se = (c < up) & (c.shift(1) >= up.shift(1)) & ob
    lx = ((c < mid) & (c.shift(1) >= mid.shift(1))) | ob
    sx = ((c > mid) & (c.shift(1) <= mid.shift(1))) | os_
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
