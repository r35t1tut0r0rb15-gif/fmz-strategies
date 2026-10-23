"""Hourly bars: the SMA 9 crossing over the SMA 21 with MACD above its signal, volume above its 20-bar average and ATR / close under 1.5 goes long; the mirror goes short; each with a stop and a target whose tick counts are 2 and 4 times the ATR (0.2 / 0.4 ATR on the source's 0.1 tick); reversing.
Port of FMZ strategy #449721 "Multi Indicator Trend Following Strategy" (Jancok Strategycs v3).

FMZ source id: 449721

Source
    https://www.fmz.com/strategy/449721 (PineScript v5, FMZ last modified 2024-04-28 14:25:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 124-166), SMA 9 / 21; MACD 12 / 26 / 9; volume SMA 20; volatility threshold 1.5; loss = atr x 2, profit = atr x 4 (ticks); trailing off
    long_condition = crossover(sma9, sma21) and macd > signal and volume > sma(volume, 20) and atr / close < 1.5 -> entry Long, exit(loss = atr x 2, profit = atr x 4)
    short_condition mirror -> entry Short, exit(loss = atr x 2, profit = atr x 4)

Interpretation choices (Pine rules in SURVEY_README.md)
    * loss / profit are counts of ticks, but the script passes an ATR (a price) as the count: on the
      header's BTC_USDT (0.1 tick) the stop is 0.2 ATR and the target 0.4 ATR from the entry (weird case;
      as #437390 for the tick conversion). They are sent on the signal bar only, from that bar's ATR:
      ported as (k x ATR[signal]) / fill, exact. The volatility filter (ATR / close < 1.5) is always true.
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR-tick bracket from the signal bar as fractions of the fill.
    2 generic: PASS, SMA crossings confirmed by MACD and volume.
    3 crypto-exchange-only: no (exchange pair in the header only; tick counts converted at the source's 0.1 tick).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449721_sma9_21_cross_macd_volume_atr_tick_bracket_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_k": [0.2, 1.0],
    "tp_k": [0.4, 2.0],
}
DEFAULT_PARAMS = {"short_ma": 9, "long_ma": 21, "vol_len": 20, "vol_thresh": 1.5, "sl_k": 0.2, "tp_k": 0.4}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    a, b = c.rolling(int(p["short_ma"])).mean(), c.rolling(int(p["long_ma"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    calm = _atr(bars_df, 14) / c < float(p["vol_thresh"])
    up = (a > b) & (a.shift(1) <= b.shift(1)) & (macd > sig) & vol_ok & calm
    dn = (a < b) & (a.shift(1) >= b.shift(1)) & (macd < sig) & vol_ok & calm
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    atr = _atr(bars_df, 14)
    filled = le.shift(1, fill_value=False) | se.shift(1, fill_value=False)
    sl_f = (float(p["sl_k"]) * atr).shift(1) / o
    tp_f = (float(p["tp_k"]) * atr).shift(1) / o
    return {"sl_stop": sl_f.where(filled), "tp_stop": tp_f.where(filled)}


def portfolio_kwargs(**params):
    return {}
