"""Composite 63 / 126 / 189 / 252-bar momentum turning positive while annualised volatility is at most 50 %, long
only, with a 5 % stop / 15 % target from the entry, 1-hour bars: the average of the four close-to-close momenta turning
above 0 with the 252-bar return volatility x sqrt(252) at or below 0.5 goes long; turning back below 0 (volatility
still at or below 0.5) closes it.
Port of FMZ strategy #483505 "多周期动量驱动型自适应波动率过滤策略-Multi-Period-Momentum-Driven-Adaptive-Volatility-Filtered-Strategy" (GOATED Long-Only).

FMZ source id: 483505

Source
    https://www.fmz.com/strategy/483505 (PineScript v5, FMZ last modified 2025-02-24 09:38:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-191), volatility threshold 0.5, SL 5 %, TP 15 %, momentum 63 / 126 / 189 /
252 bars, momentum threshold 0
    composite = mean of the non-na close / close[n] - 1; vol = stdev(change(close) / close[1], 252) x sqrt(252)
    long = vol <= 0.5 and composite > 0 and not (composite > 0)[1]
    while long: exit(stop = avg_price x 0.95, limit = avg_price x 1.15); close if vol <= 0.5 and the momentum turned off

Interpretation choices (Pine rules in SURVEY_README.md)
    * The periods are BARS (the source's "months" on a 1-hour chart), as written; the composite averages the momenta
      that exist (warm-up), as written. ta.stdev is the population standard deviation.
    * The exits use strategy.position_avg_price (the fill) on every bar while held: a fixed 5 % / 15 % bracket from the
      fill (house rule). The signal close is an exit signal at the next open.
    * Long only; the source has no shorts. Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed bracket from the fill.
    2 generic: PASS, momentum ratios, return volatility and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483505_composite_momentum_vol_filter_long"
FAMILY = "momentum"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "vol_threshold": [0.5, 1.0],
    "tp_pct": [15.0, 8.0],
}
DEFAULT_PARAMS = {"vol_threshold": 0.5, "mom_threshold": 0.0, "sl_pct": 5.0, "tp_pct": 15.0, "vol_len": 252}

PERIODS = (63, 126, 189, 252)


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
    comp = pd.concat([c / c.shift(n) - 1 for n in PERIODS], axis=1).mean(axis=1, skipna=True)
    n = int(p["vol_len"])
    vol = (c.diff() / c.shift(1)).rolling(n).std(ddof=0) * np.sqrt(252)
    vol_ok = vol.notna() & (vol <= p["vol_threshold"])
    mom_ok = comp.notna() & (comp > p["mom_threshold"])
    prev = mom_ok.shift(1, fill_value=False)
    long_e = (vol_ok & mom_ok & ~prev).astype(bool)
    long_x = (vol_ok & ~mom_ok & prev).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
