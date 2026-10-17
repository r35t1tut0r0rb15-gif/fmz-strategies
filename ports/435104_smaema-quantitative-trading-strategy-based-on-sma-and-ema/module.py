"""Swing trailing-line crosses, 3-minute bars: after a close above the previous 3-bar high the line is the 3-bar low, after a
close below the previous 3-bar low it is the 3-bar high; the close crossing above the line goes long, crossing below goes
short (reversing). The SMAs and the EMA are drawing only.
Port of FMZ strategy #435104 "基于SMAEMA的量化交易策略Quantitative-Trading-Strategy-Based-on-SMA-and-EMA" (StrategySMA 9/50/180 | EMA 20 | BUY/SELL).

FMZ source id: 435104

Source
    https://www.fmz.com/strategy/435104 (PineScript v4, FMZ last modified 2023-12-12 12:31:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-193), swing 3; SMA 9 / 50 / 180 and EMA 20 plotted only
    avd = close > highest(3)[1] ? 1 : close < lowest(3)[1] ? -1 : 0;  avn = valuewhen(avd != 0, avd, 0);  tsl = avn == 1 ? lowest(3) : highest(3)
    crossover(close, tsl) -> entry long;  crossunder(close, tsl) -> entry short;  strategy.exit(...) with no price does nothing

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two strategy.exit calls carry no level: no exit order. strategy.entry reverses: REVERSAL
      INTENDED. The 100 % of equity is sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435104_swing_trail_line_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "no": [3, 10],
}
DEFAULT_PARAMS = {"no": 3}


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
    n = int(p["no"])
    res, sup = h.rolling(n).max(), lo.rolling(n).min()
    avd = np.where(c > res.shift(1), 1, np.where(c < sup.shift(1), -1, 0))
    m = len(avd)
    avn = np.zeros(m)
    last = 0
    for i in range(m):
        if avd[i] != 0:
            last = avd[i]
        avn[i] = last
    tsl = np.where(avn == 1, sup.to_numpy(), res.to_numpy())
    cv = c.to_numpy(dtype=float)
    c1, t1 = np.concatenate(([np.nan], cv[:-1])), np.concatenate(([np.nan], tsl[:-1]))
    with np.errstate(invalid="ignore"):
        le = (cv > tsl) & (c1 <= t1)
        se = (cv < tsl) & (c1 >= t1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
