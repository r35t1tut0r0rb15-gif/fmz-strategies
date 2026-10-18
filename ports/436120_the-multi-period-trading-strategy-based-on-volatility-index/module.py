"""Williams VIX Fix rebounds, 1-hour bars, long only: after the VIX Fix leaves its extreme band, an up bar (and a close over the close three bars back, below a longer or medium
look-back close) buys; a stochastic %K cross over %D above 80 closes. Repeated entries (pyramiding 9) are held as one position.
Port of FMZ strategy #436120 "The Multi Period Trading Strategy Based on Volatility Index and Stochastic Oscillator" (Vix FIX / StochRSI Strategy).

FMZ source id: 436120

Source
    https://www.fmz.com/strategy/436120 (PineScript v5, FMZ last modified 2023-12-21 14:34:42).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 131-204), WVF look-back 22, Bollinger 20 / 2, percentile window 50 at 0.85; stochastic 14 / 3 / 3 at 80; filter look-backs 40 / 14, strength 3
    wvf = (highest(close, 22) - low) / highest(close, 22) 100;  upperBand = sma(wvf, 20) + 2 stdev(wvf, 20);  rangeHigh = highest(wvf, 50) 0.85
    alert3 = upRange (low > low[1] and close > high[1]) and close > close[3] and (close < close[40] or close < close[14]) and filtered;  alert4 = the aggressive version;  entry long on alert3 or alert4
    close long on crossover(K, D) and K > 80

Interpretation choices (Pine rules in SURVEY_README.md)
    * filtered = the VIX Fix was at or over its band the bar before and is now under both bands
      (alert3); the aggressive form needs it NOT under both (alert4). The extra entries while long
      (pyramiding 9) are sizing; an entry bar that is also a close bar leaves the position flat (entry
      dropped). Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, filters as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pyramiding input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436120_vix_fix_rebound_long"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd": [22, 30],
    "ph": [0.85, 0.9],
}
DEFAULT_PARAMS = {"pd": 22, "ph": 0.85, "bbl": 20, "mult": 2.0, "lb": 50, "lt_lb": 40, "mt_lb": 14, "strength": 3,
                  "stoch_len": 14, "smooth_k": 3, "smooth_d": 3, "ob": 80}


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
    hc = c.rolling(int(p["pd"])).max()
    wvf = (hc - lo) / hc * 100
    n = int(p["bbl"])
    s_dev = float(p["mult"]) * wvf.rolling(n).std(ddof=0)
    mid = wvf.rolling(n).mean()
    upper = mid + s_dev
    range_high = wvf.rolling(int(p["lb"])).max() * float(p["ph"])
    up_range = (lo > lo.shift(1)) & (c > h.shift(1))
    up_aggr = (c > c.shift(1)) & (c > o.shift(1))
    was = (wvf.shift(1) >= upper.shift(1)) | (wvf.shift(1) >= range_high.shift(1))
    below = (wvf < upper) & (wvf < range_high)
    filtered, filtered_aggr = was & below, was & ~below
    k_ = int(p["strength"])
    price_ok = (c > c.shift(k_)) & ((c < c.shift(int(p["lt_lb"]))) | (c < c.shift(int(p["mt_lb"]))))
    alert3 = up_range & price_ok & filtered
    alert4 = up_aggr & price_ok & filtered_aggr
    entry = (alert3 | alert4).fillna(False)
    sn = int(p["stoch_len"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(sn).min()) / (h.rolling(sn).max() - lo.rolling(sn).min())
    k = raw.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    exit_ = ((k > d) & (k.shift(1) <= d.shift(1)) & (k > float(p["ob"]))).fillna(False)
    false = pd.Series(False, index=bars_df.index)
    return (entry & ~exit_).astype(bool), exit_.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
