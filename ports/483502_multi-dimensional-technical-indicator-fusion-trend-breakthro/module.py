"""Hourly bars: a "double bottom" (20-bar low equal to the 50-bar low with the close crossing its EMA 20) or a "right shoulder" goes long, a "double top" or a "left shoulder" (the 10 bars ending 10 bars ago all under the 30-bar high) goes short, each on volume over 1.2 x its 20-bar average; the short wins on a bar with both; each trade gets a 1.5 ATR 14 stop and target from the signal close; reversing.
Port of FMZ strategy #483502 "Multi Dimensional Technical Indicator Fusion Trend Breakthrough Strategy" (Ultimate Pattern Finder).

FMZ source id: 483502

Source
    https://www.fmz.com/strategy/483502 (PineScript v5, FMZ last modified 2025-02-27 16:51:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-139), EMA 50; ATR 14 x 1.5; volume SMA 20 x 1.2; pattern tests on 20 / 30 / 50-bar extremes and EMA 20 crosses
    doubleBottom = lowest(low, 20) == lowest(low, 50) and cross(ema(close, 20), close);  rightShoulder = highest(high[10], 10) < highest(high, 30) and cross(close, ema20);  breakoutUp = close > highest(high, 50) and close > ema50
    longCondition = (doubleBottom or rightShoulder or breakoutUp) and volume > 1.2 x sma(volume, 20) -> entry Long, exit("Take Profit", limit = close + 1.5 atr, stop = close - 1.5 atr)
    shortCondition = (doubleTop or leftShoulder or breakoutDown) and the volume test -> entry Short, exit(same id, limit = close - 1.5 atr, stop = close + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The breakouts compare the close with a 50-bar high / low that includes the bar, so they never fire.
      leftShoulder (the earlier 10 bars under the 30-bar high) is true most of the time, and every right
      shoulder is also a left shoulder, so a right-shoulder long is always overridden by the later short
      call (weird case): longs come only from double bottoms off a left-shoulder bar. ta.cross is a
      crossing either way. The bracket is sent on signal bars as levels from that close: ported as
      fractions of the fill, exact (1e-6 floor); the frequent repeats re-send it (not followed:
      trailing_stop_pending). REVERSAL INTENDED. 100 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, chart-pattern approximations on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483502_pattern_finder_shoulders_double_tops_volume_atr_1h_reversal"
FAMILY = "chart_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "vol_mult": [1.2, 1.5],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "vol_mult": 1.2}


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
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    ema50 = c.ewm(span=50, adjust=False).mean()
    e20 = c.ewm(span=20, adjust=False).mean()
    cross = ((c > e20) & (c.shift(1) <= e20.shift(1))) | ((c < e20) & (c.shift(1) >= e20.shift(1)))
    dtop = (h.rolling(20).max() == h.rolling(50).max()) & cross
    dbot = (lo.rolling(20).min() == lo.rolling(50).min()) & cross
    lsh = h.shift(10).rolling(10).max() < h.rolling(30).max()
    rsh = lsh & cross
    bup = (c > h.rolling(50).max()) & (c > ema50)          # never true (the high includes the bar)
    bdn = (c < lo.rolling(50).min()) & (c < ema50)
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    sell = (dtop | lsh | bdn) & vol_ok
    buy = (dbot | rsh | bup) & vol_ok & ~sell              # the later short call wins
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["atr_mult"]) * _atr(bars_df, 14)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
            .mask(sf, (c + d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + d).shift(1) / o - 1)
            .mask(sf, 1 - (c - d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
