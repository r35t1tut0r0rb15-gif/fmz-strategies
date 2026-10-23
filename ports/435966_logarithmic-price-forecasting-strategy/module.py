"""Hourly bars, long only: a "logistic" price forecast ((close + sd 20) / (1 + sd / close x exp(-z)), z = SMA 10 / sd 100 of the signed volume) above 1.005 x the close goes long, under 0.995 x the close closes.
Port of FMZ strategy #435966 "Logarithmic Price Forecasting Strategy" (Logistic).

FMZ source id: 435966

Source
    https://www.fmz.com/strategy/435966 (PineScript v4, FMZ last modified 2023-12-20 14:40:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 140-178), signed volume by roc(close, 1); net SMA 10 / stdev 100; price stdev 20; thresholds 1.005 / 0.995
    volume_net = roc > 0 ? volume : -volume;  z = sma(volume_net, 10) / stdev(volume_net, 100);  std = stdev(close, 20)
    pred = (close + std) / (1 + std / close x exp(-z));  pred > close x 1.005 -> entry Long;  pred < close x 0.995 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0..100 loop only sets one of volume_pos / volume_neg to the bar's volume (both start at 0 each
      bar), so volume_net is the bar's volume signed by its close change (a zero change counts as down).
      z is a ratio of volume statistics, so the units cancel. Long only. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-z-driven logistic forecast against the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the signed-volume z score; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435966_logistic_forecast_signed_volume_z_long"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "std_len": [20, 50],
    "net_len": [100, 50],
}
DEFAULT_PARAMS = {"std_len": 20, "net_len": 100, "sma_len": 10, "up": 1.005, "dn": 0.995}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    roc = c.pct_change()
    net = pd.Series(np.where(roc > 0, v, -v), index=c.index)
    sd_n = net.rolling(int(p["net_len"])).std(ddof=0)
    z = net.rolling(int(p["sma_len"])).mean() / sd_n.where(sd_n != 0)
    sd = c.rolling(int(p["std_len"])).std(ddof=0)
    pred = (c + sd) / (1 + sd / c * np.exp(-z))
    buy = (pred > c * float(p["up"])).to_numpy()
    sell = (pred < c * float(p["dn"])).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            le[i], pos = True, 1
        elif pos == 1 and sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
