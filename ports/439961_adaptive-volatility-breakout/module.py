"""Hourly bars, long only: the close crossing over the upper Bollinger band (20, 1.5) with the EMA 20 / 50 spread above zero and above its EMA 20, or the close above the band with the volume flow indicator (130) or its EMA 5 positive (or the spread's EMA above 0.05) while either is under 14, goes long; the close crossing under the lower band, either VFI line above 19, or the spread under its EMA + 0.01 closes it.
Port of FMZ strategy #439961 "Adaptive Volatility Breakout" (Super Bollinger Band Breakout (beststockalert)).

FMZ source id: 439961

Source
    https://www.fmz.com/strategy/439961 (PineScript v4, FMZ last modified 2024-01-25 12:43:43).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 160-241), VFI length 130, coef 0.2, volume cutoff 2.5, signal 5; Bollinger 20 x 1.5; EMA 20 / 50 spread with EMA 20; sessions 0400-0935 / 0945-1700 (unused)
    entry Long when (crossover(close, upper) and diff > ediff and diff > 0) or (close > upper and (vfi > 0 or vfima > 0 or ediff > 0.05) and (vfi < 14 or vfima < 14))
    close Long when crossunder(close, lower) or vfi > 19 or vfima > 19 or diff < ediff + 0.01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pre-market high / low and the trade-session flag are computed but feed no order, so there is
      no session rule. ma(x, y) => 0 ? sma : x returns x (0 is false), so the VFI is not smoothed. VFI as
      LazyBear's: the 30-bar population deviation of log hlc3 changes sets the cutoff, volume is capped at
      2.5 x its 130-bar average of the previous bar, and the capped volume signed by the hlc3 move beyond
      the cutoff is summed over 130 bars and divided by that average. Pine's stdev is the population
      deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts with EMA-spread and volume-flow confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume flow indicator (capped volume over its 130-bar average); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (the session inputs feed no order).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439961_bollinger_breakout_ema_spread_vfi_1h_long_only"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [1.5, 2.0],
    "vfi_len": [130, 65],
}
DEFAULT_PARAMS = {"vfi_len": 130, "coef": 0.2, "vcoef": 2.5, "signal_len": 5, "bb_len": 20, "bb_mult": 1.5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["vfi_len"])
    typical = (h + lo + c) / 3
    inter = np.log(typical) - np.log(typical.shift(1))
    cutoff = float(p["coef"]) * inter.rolling(30).std(ddof=0) * c
    vave = v.rolling(n).mean().shift(1)
    vc = np.minimum(v, vave * float(p["vcoef"])).where(vave.notna())
    mf = typical - typical.shift(1)
    vcp = pd.Series(np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0.0)), index=c.index).where(cutoff.notna() & vc.notna())
    vfi = vcp.rolling(n).sum() / vave.where(vave != 0)
    vfima = vfi.ewm(span=int(p["signal_len"]), adjust=False).mean()
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    diff = (e20 - e50) * 100 / e20
    ediff = diff.ewm(span=20, adjust=False).mean()
    bl = int(p["bb_len"])
    basis = c.rolling(bl).mean()
    dev = float(p["bb_mult"]) * c.rolling(bl).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    x_up = (c > upper) & (c.shift(1) <= upper.shift(1))
    x_dn = (c < lower) & (c.shift(1) >= lower.shift(1))
    entry = ((x_up & (diff > ediff) & (diff > 0))
             | ((c > upper) & ((vfi > 0) | (vfima > 0) | (ediff > 0.05)) & ((vfi < 14) | (vfima < 14)))).to_numpy()
    leave = (x_dn | (vfi > 19) | (vfima > 19) | (diff < ediff + 0.01)).to_numpy()
    m = len(entry)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and leave[i]:
            lx[i], pos = True, 0
        elif pos == 0 and entry[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
