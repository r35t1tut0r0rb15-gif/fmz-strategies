"""Dip buys above the SMA 200 with a 5 % stop, 1-hour bars, long only: the close under the previous 5-bar average low with the close above the SMA 200 goes long; the close over the previous 5-bar average
high closes; a stop 5 % under the fill.
Port of FMZ strategy #441142 "Reversal Tracking Strategy" (REVERSALS).

FMZ source id: 441142

Source
    https://www.fmz.com/strategy/441142 (PineScript v4, FMZ last modified 2024-02-06 10:03:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 170-203), StopLoss 0.95 (of the average price); bars 5; SMA 200 filter; qty 1
    close > sma(high, 5)[1] -> close_all;  close < sma(low, 5)[1] and close > sma(close, 200) -> entry Long qty 1;  every bar: strategy.exit(stop = position_avg_price 0.95)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the average price x 0.95: a fixed fraction 0.05 under the fill. The script's exit has
      an na level on the flat signal bar, so its stop is first placed at the fill bar's close; the port's
      stop is active from the fill bar (as #440797). The close_all is written before the entry; the
      conditions cannot meet on one bar. Long only. Stop module: portfolio_kwargs {} (driver D4). The qty
      of 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, average-low dips, average-high exits and the SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
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

NAME = "fmz_441142_avg_low_dip_above_sma200_pct_stop_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bars": [5, 10],
    "sl": [0.05, 0.03],
}
DEFAULT_PARAMS = {"bars": 5, "sl": 0.05, "trend_len": 200}


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
    k = int(p["bars"])
    xs = (c > h.rolling(k).mean().shift(1)).to_numpy()
    go = ((c < lo.rolling(k).mean().shift(1)) & (c > c.rolling(int(p["trend_len"])).mean())).to_numpy()
    s_ = float(p["sl"])
    ov = bars_df["open"].to_numpy(dtype=float)
    lv = lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        if pos == 1 and i >= entry_i and xs[i]:
            lx[i], pos = True, 0
        elif pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
