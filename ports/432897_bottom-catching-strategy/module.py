"""RSI drops at an SMA 50 / 100 death cross, long only, 1-minute bars: the RSI 14 under 40 and more than 3 points below the
previous bar's, on a bar where the SMA 50 crosses under the SMA 100, goes long; the RSI over 65 on a bar where the SMA 9
crosses above the SMA 50 closes it.
Port of FMZ strategy #432897 "Bottom Catching Strategy" (V3 - Catching the Bottom (Coinrule)).

FMZ source id: 432897

Source
    https://www.fmz.com/strategy/432897 (PineScript v5, FMZ last modified 2023-11-22 15:46:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-186), RSI 14, drop 3, SMA 50 / 100 entry cross, SMA 9 / 50 exit cross, RSI 40 / 65
    rsi < 40 and rsi < rsi[1] - 3 and crossunder(sma50, sma100) -> entry long
    rsi > 65 and crossover(sma9, sma50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are SMAs (named EMA in the source). The start date (2022-04-01) is the author's
      window: dropped. Long only; Opposite entries cannot occur. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and SMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432897_rsi_drop_death_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 9],
    "drop": [3.0, 1.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "drop": 3.0, "buy_rsi": 40, "sell_rsi": 65}


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
    d = c.diff()
    n = int(p["rsi_len"])
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    s9, s50, s100 = (c.rolling(k).mean() for k in (9, 50, 100))
    dc = (s50 < s100) & (s50.shift(1) >= s100.shift(1))
    gc = (s9 > s50) & (s9.shift(1) <= s50.shift(1))
    le = ((r < float(p["buy_rsi"])) & (r < r.shift(1) - float(p["drop"])) & dc).astype(bool)
    lx = ((r > float(p["sell_rsi"])) & gc).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
