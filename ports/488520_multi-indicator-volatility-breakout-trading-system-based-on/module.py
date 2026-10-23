"""Hourly bars: a bar whose volume exceeds the sum of the previous 7 bars' volumes, with RSI 14 between 20 and 80, goes long on a green bar (upper wick at most twice the body) and short on a red one (lower wick at most twice the body), with a stop and target 2.5 ATR 14 from the signal close; reversing.
Port of FMZ strategy #488520 "Multi Indicator Volatility Breakout Trading System Based on Volume Price Relationship" (VolSpike ATR RSI Strategy with ATR Bands).

FMZ source id: 488520

Source
    https://www.fmz.com/strategy/488520 (PineScript v5, FMZ last modified 2025-03-28 15:33:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 157-256), volume > sum(volume, 7 previous bars); RSI 14 (80 / 20); ATR 14 x 2.5 bands from the close; TP multiplier 1; wick ratio <= 2; 10 % of equity
    volSpike = volume > sum of volume[1 .. 7] (from bar 8);  volSpike and 20 < rsi < 80 and close > open and (high - close) / body <= 2 -> entry Long, exit(stop = close - 2.5 atr, limit = close + 2.5 atr)
    ... close < open and (close - low) / body <= 2 -> entry Short, exit(stop = close + 2.5 atr, limit = close - 2.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands are the close +- 2.5 ATR, so the stop and target are both 2.5 ATR from the signal close
      (TP multiplier 1), sent on signal bars: ported as fractions of the fill, exact (1e-6 floor). A zero
      body counts as 0.0001 in the wick ratios, as written. REVERSAL INTENDED. 10 % of equity is sizing.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, extreme volume spikes with RSI and wick filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against the sum of the previous 7 bars; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488520_volspike_sum7_rsi_wick_atr_band_bracket_1h_reversal"
FAMILY = "volume_spike"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bars_back": [7, 5],
    "atr_mult": [2.5, 1.5],
}
DEFAULT_PARAMS = {"bars_back": 7, "atr_mult": 2.5, "tp_mult": 1.0, "max_wick": 2.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    k = int(p["bars_back"])
    pos = pd.Series(np.arange(len(c)), index=c.index)
    spike = (v > v.shift(1).rolling(k).sum()) & (pos > k)
    r = _rsi(c, 14)
    ok = spike & (r < 80) & (r > 20)
    body = (c - o).abs().where((c - o) != 0, 0.0001)
    mw = float(p["max_wick"])
    buy = ok & (c > o) & ((h - c) / body <= mw)
    sell = ok & (c < o) & ((c - lo) / body <= mw)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["atr_mult"]) * _atr(bars_df, 14)
    t = float(p["tp_mult"]) * d
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
            .mask(sf, (c + d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + t).shift(1) / o - 1)
            .mask(sf, 1 - (c - t).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
