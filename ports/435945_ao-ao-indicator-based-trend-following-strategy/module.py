"""AO and EMA trend entries with a percent bracket, 1-minute bars: a rising green candle crossing over the EMA 20 in an EMA 20 / 200 uptrend
with the AO over zero and the RSI 7 over 50 goes long; the mirror goes short (reversing); a long takes 10 % and stops at 1 / 1.05
(about 4.8 %), a short takes 1 / 1.10 and stops at 5 %.
Port of FMZ strategy #435945 "基于AO指标和均线的趋势跟踪策略AO-Indicator-Based-Trend-Following-Strategy" (Bingx ESTRATEGIA de Trading en 1 minuto).

FMZ source id: 435945

Source
    https://www.fmz.com/strategy/435945 (PineScript v5, FMZ last modified 2023-12-20 11:59:48).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 119-149), profit 10 %, stop 5 %; AO = SMA 5 - SMA 34 of hl2; RSI 7; EMA 20 / 200
    long: close > open and crossover(close, ema20) and ema20 > ema200 and ao > 0 and rsi7 > 50 -> entry long;  pentry = close;  exit(limit = pentry 1.10, stop = pentry / 1.05)
    short: close < open and crossunder(close, ema20) and ema20 < ema200 and ao < 0 and rsi7 < 50 -> entry short;  lentry = close;  exit(limit = lentry / 1.10, stop = lentry 1.05)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket fractions are the script's own: for a long, take 0.10 and stop 1 - 1/1.05 = 0.0476
      of the entry price; for a short, take 1 - 1/1.10 = 0.0909 and stop 0.05. They are given as per-bar
      stop Series that carry the side's values on the signal bar, shifted one bar inside stops()
      (re-based on the fill). The entry price variable is updated on every signal, even one that
      adds nothing, so a later same-side signal would move the author's levels: the port keeps the
      fill's levels. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-minute bars: not coarse. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, percent bracket and standard indicators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the profit and stop inputs stored.
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

NAME = "fmz_435945_ao_ema_trend_percent_bracket"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "profit": [10.0, 5.0],
    "stop": [5.0, 2.0],
}
DEFAULT_PARAMS = {"profit": 10.0, "stop": 5.0}


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


def _signals(bars_df):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    e20, e200 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / 7, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / 7, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    le = ((c > o) & (c > e20) & (c.shift(1) <= e20.shift(1)) & (e20 > e200) & (ao > 0) & (rsi > 50)).fillna(False)
    se = ((c < o) & (c < e20) & (c.shift(1) >= e20.shift(1)) & (e20 < e200) & (ao < 0) & (rsi < 50)).fillna(False)
    return le.astype(bool), se.astype(bool)


def simulate(bars_df, **params):
    le, se = _signals(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df)
    pf, sf = float(p["profit"]) / 100 + 1, float(p["stop"]) / 100 + 1
    ix = bars_df.index
    sl = pd.Series(np.where(le, 1 - 1 / sf, np.where(se, sf - 1, np.nan)), index=ix)
    tp = pd.Series(np.where(le, pf - 1, np.where(se, 1 - 1 / pf, np.nan)), index=ix)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
