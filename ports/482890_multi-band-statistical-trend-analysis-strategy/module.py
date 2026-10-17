"""Long while the close is above the 20-bar 95 % quantile of closes minus one standard deviation, flat otherwise,
1-hour bars.
Port of FMZ strategy #482890 "多波段统计趋势分析策略-Multi-Band-Statistical-Trend-Analysis-Strategy" (Multi-Band Comparison Strategy with Separate Entry/Exit Confirmation).

FMZ source id: 482890

Source
    https://www.fmz.com/strategy/482890 (PineScript v6, FMZ last modified 2025-02-20 16:45:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-252), length 20, upper quantile 0.95, confirmation bars 1 / 1
    quant_upper = sorted last 20 closes [round(19 x 0.95)]; trigger = close > quant_upper - stdev(close, 20)
    trigger held for 1 bar and position <= 0 -> entry long; not trigger for 1 bar and position > 0 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The quantile is the source's f_percentile (index round((n - 1) q) of the sorted window, incl. the current close);
      ta.stdev population. The other bands only colour plots.
    * With one-bar confirmations the strategy is long exactly while the trigger holds. Long only; no stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling quantile and standard deviation of closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482890_quantile_band_trigger_long"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "confirm_bars": [1, 3],
}
DEFAULT_PARAMS = {"length": 20, "upper_q": 0.95, "confirm_bars": 1}


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
    c = bars_df["close"]
    n = int(p["length"])
    j = int(np.floor((n - 1) * p["upper_q"] + 0.5))           # Pine math.round (half up)
    qu = c.rolling(n).apply(lambda w: np.sort(w)[j], raw=True)
    trig = (c > qu - c.rolling(n).std(ddof=0)).to_numpy()
    k = int(p["confirm_bars"])
    m = len(trig)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    on = off = 0
    for i in range(m):
        on = on + 1 if trig[i] else 0
        off = off + 1 if not trig[i] else 0
        le[i] = on >= k
        lx[i] = off >= k
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
