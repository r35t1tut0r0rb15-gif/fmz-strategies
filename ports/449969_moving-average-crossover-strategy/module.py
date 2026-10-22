"""SMA 5 / 20 crossings after four closes on the same side of the SMA 5, 1-hour bars, with a 150-tick target: a cross up after four closes above the SMA 5 goes long, the mirror goes short; reversing.
Port of FMZ strategy #449969 "Moving Average Crossover Strategy" (Moving Average Crossover Strategy (SMA 5 / 20, 4-bar filter)).

FMZ source id: 449969

Source
    https://www.fmz.com/strategy/449969 (PineScript v4, FMZ last modified 2024-04-30 17:33:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-143), SMA 5 / 20; four-bar filter on the SMA 5; target 150 ticks; trading hours always on
    crossover(sma5, sma20) and close[1..4] > sma5[1..4] -> entry Buy, exit(profit = 150);  crossunder and close[1..4] < sma5[1..4] -> entry Sell, exit(profit = 150)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 150-tick target (mintick 0.1 = 15 price units) is re-expressed as tp_stop =
      k_atr x ATR(14) / close of the signal bar, shifted one bar inside stops() and re-based on the
      fill; 0.1 is the reading against a 1-hour BTC ATR near 150. There is no stop. isMarketOpen is
      always true. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed on the signal bar.
    2 generic: PASS, SMA crossings with a four-bar side filter, tick target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick target quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the trading-hours flag is always true).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449969_sma5_20_cross_four_bar_side_tick_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.1, 1.0],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"k_atr": 0.1, "slow": 20, "fast": 5, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    above = pd.Series(True, index=c.index)
    below = pd.Series(True, index=c.index)
    for k in range(1, 5):
        above &= c.shift(k) > f.shift(k)
        below &= c.shift(k) < f.shift(k)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & above
    se = (f < s) & (f.shift(1) >= s.shift(1)) & below
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
