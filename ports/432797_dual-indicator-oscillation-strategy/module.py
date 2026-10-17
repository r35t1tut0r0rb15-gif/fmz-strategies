"""Stochastic and RSI extremes, 1-minute bars: the RSI 14 and the stochastic K (14, smoothed 3) both under 20 go long, both
over 80 go short; a bracket 100 USD either side of the close (re-placed every bar) becomes an ATR bracket fixed at the
signal bar.
Port of FMZ strategy #432797 "Dual Indicator Oscillation Strategy" (Estrategia de Oscilador Estocástico y RSI).

FMZ source id: 432797

Source
    https://www.fmz.com/strategy/432797 (PineScript v4, FMZ last modified 2023-11-21 15:50:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 87-113), stoch 14 / 3 / 3, RSI 14, levels 20 / 80, stop 100, target 100 (price units)
    rsi < 20 and k < 20 -> entry long;  rsi > 80 and k > 80 -> entry short
    every bar: exit(long, stop = close - 100, limit = close + 100);  exit(short, stop = close + 100, limit = close - 100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 100 price-unit distances become sl_atr / tp_atr x Wilder ATR 14 (about 4 ATR
      on 1-minute BTC, ATR about 25 USD).
    * The exits are re-placed every bar around the latest close, so the levels move after entry:
      stops() cannot express that (rule 2, mark trailing_stop_pending). The port fixes the bracket at
      the signal bar (ATR / close of that bar, shifted one bar, re-based on the fill).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (the per-bar re-placement pending).
    2 generic: ADAPT, price-unit distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_432797_stoch_rsi_extreme_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [4.0, 1.5],
    "tp_atr": [4.0, 1.5],
}
DEFAULT_PARAMS = {"k_len": 14, "smooth_k": 3, "rsi_len": 14, "os": 20, "ob": 80, "atr_len": 14, "sl_atr": 4.0,
                  "tp_atr": 4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = c.diff()
    ru = d.clip(lower=0).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    rd = (-d.clip(upper=0)).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    r = 100 - 100 / (1 + ru / rd)
    os_, ob = float(p["os"]), float(p["ob"])
    le = ((r < os_) & (k < os_)).astype(bool)
    se = ((r > ob) & (k > ob)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
