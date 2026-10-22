"""Wick spikes of the last hour of each 3-hour bar: a top wick of at least 0.62 % of the close (and no bottom wick as large) goes long, a bottom wick goes short, each with a 0.42 % target and a 1 % stop from the fill; reversing.
Port of FMZ strategy #482817 "Volatility Spike Indicator Smart Trading Strategy" (Spike Strategy 1h Optimized).

FMZ source id: 482817

Source
    https://www.fmz.com/strategy/482817 (PineScript v6, FMZ last modified 2025-02-27 17:43:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-137), spike threshold 0.62 %; target 0.42 %; stop 1 %; "60" security on a 3h chart; 30000 USDT per trade
    [spike_up, spike_down] = security("60", (high - close) / close >= 0.62 %, (close - low) / close >= 0.62 %)
    spike_up and not spike_down -> entry Long;  spike_down and not spike_up -> entry Short
    position long -> exit(limit = avg x 1.0042, stop = avg x 0.99);  position short -> exit(limit = avg x 0.9958, stop = avg x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "60" is a LOWER time frame than the 3-hour chart, requested without lookahead: each chart bar gets
      the values of its last hourly bar (as #436765), built from the bar's own minutes in precompute.
      The spikes read the hour's high and low against its close as written (a top wick goes long). The
      brackets are sent from the fill bar's close around the average price; ported as fixed fractions of
      the fill, active from the fill bar (as #440797). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. The 30000 USDT quantity and the 100 % of equity default are sizing. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, hourly wick spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 30000 USDT per trade and 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482817_last_hour_wick_spike0_62_pct_bracket_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "spike_threshold": [0.62, 1.0],
    "profit_target": [0.42, 0.8],
}
DEFAULT_PARAMS = {"spike_threshold": 0.62, "profit_target": 0.42, "stop_loss": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    hr = _resample(raw_1m_df, "1h")
    last = hr.groupby(hr.index.floor(FREQ)).last()        # each 3-hour bar's last hourly bar
    bars["h1_high"] = last["high"].reindex(bars.index)
    bars["h1_low"] = last["low"].reindex(bars.index)
    bars["h1_close"] = last["close"].reindex(bars.index)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hc = bars_df["h1_close"]
    thr = float(p["spike_threshold"]) / 100
    up = (bars_df["h1_high"] - hc) / hc >= thr
    dn = (hc - bars_df["h1_low"]) / hc >= thr
    false = pd.Series(False, index=bars_df.index)
    return up & ~dn, false, dn & ~up, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["profit_target"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
