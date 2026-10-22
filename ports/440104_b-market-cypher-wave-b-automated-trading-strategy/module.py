"""WaveTrend crossings in the extreme zones, 1-hour bars: the WaveTrend line crossing over its 3-bar average while under -70 goes long, crossing under it while over 70 goes short; reversing (the default
stop, target and trail inputs are 0, which places no levels).
Port of FMZ strategy #440104 "市场密码波浪B自动买卖策略Market-Cypher-Wave-B-Automated-Trading-Strategy" (MCB CIRCLE ONLY PGB STRAT BUN TP SL TEST).

FMZ source id: 440104

Source
    https://www.fmz.com/strategy/440104 (PineScript v5, FMZ last modified 2024-01-26 16:16:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 281-772), WaveTrend 9 / 12 / 3 on hlc3; overbought 70 (oversold -70); stop, target and trail inputs 0
    esa = ema(hlc3, 9);  de = ema(|hlc3 - esa|, 9);  wt1 = ema((hlc3 - esa) / (0.015 de), 12);  wt2 = sma(wt1, 3)
    long = crossover(wt1, wt2) and wt1 < -70;  short = crossunder(wt1, wt2) and wt1 > 70;  pos = long ? 1 : short ? -1 : pos[1];  entries when pos[1] differs;  strategy.exit stop / limit from the 99999 placeholders

Interpretation choices (Pine rules in SURVEY_README.md)
    * The WaveTrend is requested on the chart's own timeframe, so the security calls are the chart
      series. The higher-timeframe Heikin-Ashi requests (lookahead on), the money-flow area, the
      divergences and the other panels only feed plots and alerts and are not ported. With the inputs at
      0 the stop, target and trail become 99999 fractions: the long stop is below zero, the short stop
      and both targets out of reach, so strategy.exit places nothing that can fill; the position flags
      only change on the signals. strategy.initial_capital = 50000 and the equity > 0 gate are sizing
      (the gate stays true). strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the lookahead requests feed plots only.
    2 generic: PASS, WaveTrend crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: initial capital and equity gate are sizing.
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

NAME = "fmz_440104_wavetrend_extreme_cross"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ob_level": [70, 53],
    "avg_len": [12, 21],
}
DEFAULT_PARAMS = {"ob_level": 70, "avg_len": 12, "channel_len": 9, "ma_len": 3}


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
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    n1 = int(p["channel_len"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    de = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * de.where(de > 0))
    wt1 = ci.ewm(span=int(p["avg_len"]), adjust=False).mean()
    wt2 = wt1.rolling(int(p["ma_len"])).mean()
    ob = float(p["ob_level"])
    up = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1)) & (wt1 < -ob)
    dn = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)) & (wt1 > ob)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
