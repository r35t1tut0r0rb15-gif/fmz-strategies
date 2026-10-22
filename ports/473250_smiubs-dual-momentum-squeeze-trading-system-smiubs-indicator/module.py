"""Falling "squeeze momentum" with a close crossing under its SMA 14, 2-hour bars, short only: both together sell short, with a 0.4 % target and 2.5 % stop from the fill.
Port of FMZ strategy #473250 "双重动量挤压交易系统SMIUBS指标组合策略-Dual-Momentum-Squeeze-Trading-System-SMIUBS-Indicator-Combination-Strategy" (Squeeze Momentum and Ultimate Buy/Sell with Stop Loss).

FMZ source id: 473250

Source
    https://www.fmz.com/strategy/473250 (PineScript v5, FMZ last modified 2024-11-28 15:52:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-136), momentum = SMA 5 of (SMA 5 of close - lowest low 20) - SMA 5 of (highest high 20 - close); SMA 14 of close; target avg x 0.996, stop avg x 1.025
    momentum falling and crossunder(close, sma14) -> entry Short;  short: exit(limit = avg x 0.996, stop = avg x 1.025)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ultimate buy" signal is only plotted. The bracket comes from the average (fill) price and is
      sent every bar while held: ported active from the fill bar (#440797) as the fixed fractions 0.004
      / 0.025 of the fill. Short only. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour
      bars: mark coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned
      2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, momentum-down shorts below an SMA with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473250_squeeze_momentum_down_sma14_cross_short"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.004, 0.02],
    "sl_pct": [0.025, 0.01],
}
DEFAULT_PARAMS = {"tp_pct": 0.004, "sl_pct": 0.025, "smi_len": 20, "smi_smooth": 5, "ult_len": 14}


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
    n, s = int(p["smi_len"]), int(p["smi_smooth"])
    smi = (c - lo.rolling(n).min()).rolling(s).mean() - (h.rolling(n).max() - c).rolling(s).mean()
    mom = smi.rolling(s).mean()
    ma = c.rolling(int(p["ult_len"])).mean()
    se = (mom < mom.shift(1)) & (c < ma) & (c.shift(1) >= ma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
