"""EMA channel state with a range-comparison state, 1-hour bars: both long opens a long, both short opens a short, any other combination
closes (the "Trade reverse" input flips the side).
Port of FMZ strategy #435713 "基于双EMA和价格波动率指标的量化交易策略Quantitative-Trading-Strategy-Based-on-Double-EMA-and-Price-Volatility-Index" (Combo 2/20 EMA & (H-L)/C Histogram).

FMZ source id: 435713

Source
    https://www.fmz.com/strategy/435713 (PineScript v5, FMZ last modified 2023-12-18 11:26:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 169-216), EMA 14 channel state; range look-back 20, SMA 16 of the range (price, not percent)
    EMA20: xXA = ema(close, 14);  nHH = max(high, high[1]);  nLL = min(low, low[1]);  nXS = nLL > xXA or nHH < xXA ? nLL : nHH;  pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : last
    HLCH: sma(|high - low|, 16)[20] > |high - low| ? 1 : < ? -1 : last
    pos = both 1 -> 1;  both -1 -> -1;  else 0;  possig = reverse ? -pos : pos;  entry long / short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Two persistent states combined (the first compares an EMA-based level with the previous close, the
      second compares the current range with the average range 20 bars back); a flip from one agreed
      side to the other on one bar is a reversal (REVERSAL INTENDED); any disagreement closes. The
      start-date input (2005) is the author's window: dropped. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel state and a range comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435713_ema_channel_range_combo"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length": [14, 20],
}
DEFAULT_PARAMS = {"reverse": False, "length": 14, "barsback": 20, "sma_length": 16}


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


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh, nll = np.maximum(h, h.shift(1)), np.minimum(lo, lo.shift(1))
    nxs = pd.Series(np.where((nll > xa) | (nhh < xa), nll, nhh), index=c.index)
    c1 = c.shift(1)
    # pos := nXS > close[1] ? -1 : (nXS < close[1] ? 1 : last)
    a = _state((nxs < c1).to_numpy(), (nxs > c1).to_numpy())
    rng = (h - lo).abs()
    sm = rng.rolling(int(p["sma_length"])).mean().shift(int(p["barsback"]))
    b = _state((sm > rng).to_numpy(), (sm < rng).to_numpy())
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
