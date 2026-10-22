"""Four long setups on a 200-bar Bollinger band and a MACD(12, 26, 9) histogram, 1-hour bars, long only: band re-entries, histogram crossings over zero with a band re-entry or above the EMA 20, and a
histogram crossing over a small floor under the upper band; the low crossing under the EMA 20 or the close 1.16 % under the fill closes.
Port of FMZ strategy #442643 "基于布林带和MACD的量化交易策略Quantitative-Trading-Strategy-Based-on-Bollinger-Bands-and-MACD" (Nabz-BBMACD-2022-V1.1 (BBM-Nabz)).

FMZ source id: 442643

Source
    https://www.fmz.com/strategy/442643 (PineScript v5, FMZ last modified 2024-02-23 14:30:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-238), BB 200 / 2; MACD 12 / 26 / 9; EMA 20 / 50 / 100 / 200 (only the 20 trades); RSI 6 (unused)
    L1: close[1] < lower[1] and crossover(close, lower);  L2: crossover(delta, 0) and crossover(close, lower);  L3: crossover(delta, 0) and low > ema20 and close[1] < low;  L4: crossover(delta, 0.01) and high[1] < upper and not crossunder(close, ema20) -> entry RSI_BB_L
    crossunder(low, ema20) and close < ema20 -> close;  close < entry_price / 1.01175734321249 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * All four setups enter the same id; while long they are refused (default pyramiding). The 0.01
      histogram floor is in price units: as a fraction of the close at the BTC reading of 42000,
      2.4e-7 x close. The second close compares the bar close with the open trade's fill price, read
      at the bar close from the bar the long is held at. The RSI and the colours only plot. Long only.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit histogram floor -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442643_bb200_macd_hist_setups_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [200, 100],
    "stop_div": [1.01175734321249, 1.02],
}
DEFAULT_PARAMS = {"bb_length": 200, "stop_div": 1.01175734321249, "fast": 12, "slow": 26, "signal": 9,
                  "floor_frac": 2.4e-07}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xunder(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    e20 = c.ewm(span=20, adjust=False).mean()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = 2 * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    zero = pd.Series(0.0, index=c.index)
    d0 = _xover(delta, zero)
    l1 = (c.shift(1) < lower.shift(1)) & _xover(c, lower)
    l2 = d0 & _xover(c, lower)
    l3 = d0 & (lo > e20) & (c.shift(1) < lo)
    l4 = _xover(delta, float(p["floor_frac"]) * c) & (h.shift(1) < upper) & ~_xunder(c, e20)
    go = (l1 | l2 | l3 | l4).to_numpy()
    x1 = (_xunder(lo, e20) & (c < e20)).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    sd = float(p["stop_div"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fill = False, np.nan
    for i in range(m):
        if go[i] and not held:
            le[i] = True
            if i + 1 < m:
                fill = ov[i + 1]
        elif held and (x1[i] or cv[i] < fill / sd):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
