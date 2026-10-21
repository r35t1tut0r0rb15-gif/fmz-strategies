"""EMA 9 / 15 crossings above or below the EMA 50 with a one-tick bracket, 10-minute bars: the EMA 9 crossing over the EMA 15 with the close above the EMA 50 goes long, the mirror short, reversing; every
position has a 1-tick target and a 0.5-tick stop, re-expressed as ATR multiples.
Port of FMZ strategy #437765 "基于EMA均线交叉的短期量化交易策略Quantitative-Trading-Strategy-Based-on-EMA-Crossover" (EMA Crossover Strategy).

FMZ source id: 437765

Source
    https://www.fmz.com/strategy/437765 (PineScript v4, FMZ last modified 2024-01-05 14:01:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 124-151), EMA 9 / 15 / 50; exit "TP/SL" profit 1, loss 0.5 (ticks) for every entry
    buy = crossover(ema 9, ema 15) and close > ema 50 -> entry Buy;  sell = crossunder and close < ema 50 -> entry Sell;  exit("TP/SL", profit = 1, loss = 0.5) for all entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick bracket is re-expressed as sl_stop = k_atr x ATR(14) / close and tp_stop = 2 x
      sl_stop of the signal bar, shifted one bar inside stops() and re-based on the fill; 0.0007 is the
      reading (0.5 tick of 0.1 on BTC against a 10-minute ATR near 70: almost immediate exits), 0.5 a stop
      that leaves room. The exits without levels inside the ifs place no order. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick bracket stored.
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

NAME = "fmz_437765_ema_cross_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.0007, 0.5],
    "fast": [9, 5],
}
DEFAULT_PARAMS = {"k_atr": 0.0007, "fast": 9, "medium": 15, "long": 50, "atr_len": 14, "tp_ratio": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    md = c.ewm(span=int(p["medium"]), adjust=False).mean()
    lg = c.ewm(span=int(p["long"]), adjust=False).mean()
    up = (f > md) & (f.shift(1) <= md.shift(1)) & (c > lg)
    dn = (f < md) & (f.shift(1) >= md.shift(1)) & (c < lg)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
