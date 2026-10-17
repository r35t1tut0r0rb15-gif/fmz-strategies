"""Big-candle momentum, 30-minute bars: a green candle longer than the ATR 14 with the RSI 14 above 50 goes long, a red
candle longer than the ATR with the RSI under 50 goes short; always in after the first signal.
Port of FMZ strategy #433562 "基于RSI和ATR通道的超级scalping策略" (Super Scalper - 5 Min 15 Min).

FMZ source id: 433562

Source
    https://www.fmz.com/strategy/433562 (PineScript v4, FMZ last modified 2023-11-28 15:15:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 108-133), EMA 21 / 65 (plots only), RSI 14, ATR 14
    longCondition = open < close - atr;  shortCondition = open > close + atr
    longCondition and rsi > 50 -> entry long;  shortCondition and rsi < 50 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stopLoss / takeProfit variables are computed but never passed to an exit (the exits are
      commented out), and the EMA crosses are labels only. strategy.entry reverses: REVERSAL INTENDED.
      The title's 5 / 15-minute charts are not the header's period: FREQ = "30min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle body against the ATR and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 stored.
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

NAME = "fmz_433562_big_candle_rsi_momentum"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [1.0, 1.5],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"atr_mult": 1.0, "atr_len": 14, "rsi_len": 14}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    le = ((o < c - atr) & (r > 50)).astype(bool)
    se = ((o > c + atr) & (r < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
