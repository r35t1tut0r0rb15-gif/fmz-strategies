"""RSI 4 extremes, 1-hour bars: the RSI 4 crossing below 5 goes long, crossing above 95 goes short (reversing); each trade
carries a 150-tick target and a 230-tick stop, re-expressed as ATR multiples.
Port of FMZ strategy #435002 "基于RSI指标和MA均线的趋势跟踪策略RSI-MA-Trend-Following-Strategy" (4All).

FMZ source id: 435002

Source
    https://www.fmz.com/strategy/435002 (PineScript v2, FMZ last modified 2023-12-11 16:14:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 138-171), RSI 4 (Wilder), rsin 5 (levels 5 / 95); TP 15 x 10 = 150 ticks, SL 23 x 10 = 230 ticks, trail off
    long = crossunder(rsi, 5) -> entry long;  short = crossover(rsi, 95) -> entry short;  exit(profit = 150, loss = 230) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 150 / 230 ticks of 0.1 on hourly BTC (15 / 23 USD) are about 0.075 / 0.115 x the
      hourly Wilder ATR 14 of the signal bar (tp_atr / sl_atr, fractions of the signal close
      shifted one bar inside stops(), re-based on the fill).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_435002_rsi4_extreme_tick_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsin": [5, 15],
    "atr_scale": [1.0, 10.0],
}
DEFAULT_PARAMS = {"rsi_len": 4, "rsin": 5, "atr_len": 14, "tp_atr": 0.075, "sl_atr": 0.115, "atr_scale": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    lo_l, hi_l = float(p["rsin"]), 100 - float(p["rsin"])
    le = ((rsi < lo_l) & (rsi.shift(1) >= lo_l)).to_numpy()
    se = ((rsi > hi_l) & (rsi.shift(1) <= hi_l)).to_numpy()
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr_f = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["atr_scale"])
    return {"sl_stop": (float(p["sl_atr"]) * atr_f).shift(1), "tp_stop": (float(p["tp_atr"]) * atr_f).shift(1)}


def portfolio_kwargs(**params):
    return {}
