"""The EMA 50 of the close against a 100-bar rolling VWAP of hlc3, 2-hour bars, long only (the direction input is LONG): the EMA crossing over the VWAP goes long; crossing back under, or a close 8 % under the entry, closes.
Port of FMZ strategy #427354 "基于EMA和累积成交量的多空交易策略EMA-and-Cumulative-Volume-Crossover-Strategy-for-Long-Short" (EMA_cumulativeVolume_crossover[Strategy]).

FMZ source id: 427354

Source
    https://www.fmz.com/strategy/427354 (PineScript v4, FMZ last modified 2023-09-20 11:48:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 127-197), EMA 50; rolling VWAP sum(hlc3 x volume, 100) / sum(volume, 100); stop 8 % (close test); partial profits off; direction LONG; risk 10 %
    crossover(ema(50), vwapValue) and LONG -> entry LE;  crossunder(ema(50), vwapValue) -> close LE;  close < avg x 0.92 (position_size >= 1) -> close LE
    (SHORT branch: close / open patterns under the VWAP -> entry SE, with its own exits; not selected)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The direction input selects LONG, so the short branch never runs. position_size >= 1 is read as
      "in a position" (the risk-based quantity is a size test on the source's instrument; as #426617), so
      the 8 % close stop applies against the fill. The partial exits are off. Long only. The risk-based
      quantity and 20 % of equity are sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop.
    2 generic: PASS, EMA against a rolling VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 10 % / (close x 8 %), 20 % of equity, capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the 100-bar rolling VWAP; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427354_ema50_rolling_vwap100_cross_long_close_stop"
FAMILY = "vwap_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [50, 20],
    "cumulative_period": [100, 50],
}
DEFAULT_PARAMS = {"ema_length": 50, "cumulative_period": 100, "stop": 8.0}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["cumulative_period"])
    vw = (v * (h + lo + c) / 3).rolling(n).sum() / v.rolling(n).sum()
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    xu = ((ema > vw) & (ema.shift(1) <= vw.shift(1))).to_numpy()
    xd = ((ema < vw) & (ema.shift(1) >= vw.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = float(p["stop"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill = 0, np.nan
    for i in range(m):
        if pos == 1 and (xd[i] or cv[i] < fill * (1 - k)):
            lx[i] = True
            pos = 0
        elif pos == 0 and xu[i] and i + 1 < m:
            le[i] = True
            pos, fill = 1, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
