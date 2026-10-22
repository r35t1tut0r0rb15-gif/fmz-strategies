"""Up bars closing above an SMA 100 and its SMA 200 with Williams %R 14 rising three bars above -20 and a quiet previous bar (range at most 0.5 %), 30-minute bars, long only: entered from flat; the close under both averages, the SMA 100 under its SMA 200, or %R under -80 closes.
Port of FMZ strategy #482769 "Dual Moving Average Trend Following System with Adaptive Dynamic Filtering Strategy" (EMA & MA Crossover Strategy).

FMZ source id: 482769

Source
    https://www.fmz.com/strategy/482769 (PineScript v5, FMZ last modified 2025-02-27 17:51:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-208), SMA 100, SMA(SMA 100, 200); %R 14; run-up 0.5 %; HMA 70 and EMA 20 / 30 / 40 / 50 (second branch); ignore 1 candle
    buy = (close > xMA and close > xEMA and close > open and close > close[1]) or (xMA > xEMA and close < prevDayClose x 0.018 and hma rising and EMA stack)
    buy and %R rising 3 bars and %R, %R[1] > -20 and close[1] exists and (high[1] - low[1]) / low[1] <= 0.5 % -> entry Buy
    (close < xMA and close < xEMA) or xMA < xEMA or %R < -80 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second buy branch needs the close under 1.8 % of the previous day's close, which cannot happen on
      a positive price, so only the first branch can buy, as written (the day's high / low and the HMA are
      then unused). %R uses the 14-bar highest high and lowest low. "Ignore first N candles" only drops
      the first bar of the data. An entry and a close can both be true on one bar (when the SMA 100 is
      under its SMA 200): the entry comes first, so from flat the entry stands and the close does not act
      on it; when a long is held into the bar the entry is ignored and the close acts (as #441963): a loop.
      Long only. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend-side up bars with a %R momentum filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the previous-day branch cannot fire).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482769_sma100_200_up_bar_wpr_rising_quiet_prev_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ma": [100, 50],
    "run_up_threshold": [0.5, 1.0],
}
DEFAULT_PARAMS = {"length_ma": 100, "run_up_threshold": 0.5, "length_ema": 200, "wpr_length": 14}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    xma = c.rolling(int(p["length_ma"])).mean()
    xema = xma.rolling(int(p["length_ema"])).mean()
    n = int(p["wpr_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    pr = 100 * (c - hh) / (hh - ll)
    b1 = (pr > pr.shift(1)) & (pr.shift(1) > pr.shift(2)) & (pr.shift(2) > pr.shift(3)) & (pr > -20) & (pr.shift(1) > -20)
    buy = (c > xma) & (c > xema) & (c > o) & (c > c.shift(1))
    run_up = (h.shift(1) - lo.shift(1)) / lo.shift(1) * 100
    valid = c.shift(1).notna() & (run_up <= float(p["run_up_threshold"]))
    lc = (buy & b1 & valid).to_numpy()
    xc = (((c < xma) & (c < xema)) | (xma < xema) | (pr < -80)).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xc[i]:
            lx[i], pos = True, 0                  # the close acts on the long held into the bar
        elif pos == 0 and lc[i]:
            le[i], pos = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
