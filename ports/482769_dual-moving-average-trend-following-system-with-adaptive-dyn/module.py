"""Up-closes above the SMA 100 and its SMA 200 with Williams %R rising three bars above -20 after a quiet bar (range
<= 0.5 %), long only, closed below the averages, on an SMA 100 / 200 bear cross state or %R below -80, 30-minute bars.
Port of FMZ strategy #482769 "双均线趋势跟踪交易系统与自适应动态过滤策略-Dual-Moving-Average-Trend-Following-System-with-Adaptive-Dynamic-Filtering-Strategy" (EMA & MA Crossover Strategy).

FMZ source id: 482769

Source
    https://www.fmz.com/strategy/482769 (PineScript v5, FMZ last modified 2025-02-27 17:51:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-203), SMA 100, "EMA" = SMA 200 of the SMA 100, %R 14, run-up 0.5 %
    buy = (close > xMA and close > xEMA) and (close > open and close > close[1])
          or xMA > xEMA and close < previous daily close x 0.018 and HMA 70 rising and EMA 20 > 30 > 40 > 50 < close
    buy1 = %R rising over 3 bars and %R > -20 and %R[1] > -20
    buy and buy1 and close[1] exists and (high[1] - low[1]) / low[1] <= 0.5 % -> entry long
    (close < xMA and close < xEMA) or xMA < xEMA or %R < -80 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second branch of buy compares the close with 1.8 % of the daily close: never true on any market (a price
      level that is unreachable, criterion 2): dropped as inert (as #492009), with the HMA / EMA-stack filters and the
      daily request that only it uses. The day high / low and the %R lines feed only drawings.
    * Closes are written after the entry: they act on the position held at the bar's start and never undo an entry
      on that bar (#430850). State machine; exits emitted only on going flat.
    * Long only. Signal module, no stops. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMAs, Williams %R and a percentage range filter (the 1.8 %-of-price branch is inert and dropped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the day-high / day-low block feeds only drawings).
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482769_sma100_200_upclose_wpr_quiet_bar_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [100, 50],
    "run_up": [0.5, 1.0],
}
DEFAULT_PARAMS = {"ma_len": 100, "ma2_len": 200, "wpr_len": 14, "run_up": 0.5}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    x_ma = c.rolling(int(p["ma_len"])).mean()
    x_ema = x_ma.rolling(int(p["ma2_len"])).mean()
    n = int(p["wpr_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wpr = 100 * (c - hh) / (hh - ll)
    buy = (c > x_ma) & (c > x_ema) & (c > o) & (c > c.shift(1))
    buy1 = ((wpr > wpr.shift(1)) & (wpr.shift(1) > wpr.shift(2)) & (wpr.shift(2) > wpr.shift(3))
            & (wpr > -20) & (wpr.shift(1) > -20))
    quiet = (h.shift(1) - lo.shift(1)) / lo.shift(1) * 100 <= p["run_up"]
    enter = (buy & buy1 & quiet & c.shift(1).notna()).to_numpy()
    leave = (((c < x_ma) & (c < x_ema)) | (x_ma < x_ema) | (wpr < -80)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if enter[i] and pos == 0:
            le[i], pos = True, 1
        if leave[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
