"""Hourly bars, long only (the 1-hour settings): RSI 18 crossing over its SMA 50 on a green bar closing above the prior 5-bar high, with volume over 1.2 x its 20-bar average and EMA 35 above EMA 100, goes long with a 2.5 ATR stop and a target of only 0.125 ATR from the signal close; an RSI cross back under its SMA or a close under the prior 5-bar low closes it.
Port of FMZ strategy #488502 "多时间周期RSI-SMA动态交叉自适应交易系统-Multi-Timeframe-RSI-SMA-Dynamic-Crossover-Adaptive-Trading-System" (Multi-Timeframe RSI-SMA Strategy [EB]).

FMZ source id: 488502

Source
    https://www.fmz.com/strategy/488502 (PineScript v5, FMZ last modified 2025-03-28 11:36:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 196-327), timeframe switches ("60": RSI 18, SMA 50, ATR x 2.5, tpPerc 5, volume x 1.2); EMA int(50 x 0.7) / 100; ATR 14
    entryCondition = crossover(rsi, sma(rsi, 50)) and volume > 1.2 x sma(volume, 20) and ema35 > ema100 and close > open and close > highest(high, 5)[1] -> entry Long, exit(stop = close - 2.5 atr, limit = close + 2.5 atr x 5 / 100)
    exitCondition = crossunder(rsi, rsiSMA) or close < lowest(low, 5)[1] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The settings come from the chart timeframe; the header's 1 hour picks RSI 18, SMA 50, ATR x 2.5,
      tpPerc 5 and volume x 1.2. The target is 2.5 ATR x 5 % = 0.125 ATR above the close, as written
      (weird case), and the stop 2.5 ATR under it, both sent on the signal bar: ported as fractions of the
      fill, exact (1e-6 floor). The entry and the close never meet on one bar. Long only. 100 % of equity
      is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, RSI / SMA crossings on breakout bars with volume and trend filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488502_rsi_sma_cross_breakout_volume_atr_tiny_target_1h_long_only"
FAMILY = "rsi_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.5, 1.5],
    "tp_perc": [5.0, 100.0],
}
DEFAULT_PARAMS = {"rsi_len": 18, "sma_len": 50, "atr_mult": 2.5, "tp_perc": 5.0, "vol_mult": 1.2}


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
    n = int(p["sma_len"])
    r = _rsi(c, int(p["rsi_len"]))
    rs = r.rolling(n).mean()
    ef = c.ewm(span=int(n * 0.7), adjust=False).mean()
    es = c.ewm(span=n * 2, adjust=False).mean()
    entry = ((r > rs) & (r.shift(1) <= rs.shift(1)) & (v > v.rolling(20).mean() * float(p["vol_mult"]))
             & (ef > es) & (c > o) & (c > h.rolling(5).max().shift(1)))
    ex = ((r < rs) & (r.shift(1) >= rs.shift(1))) | (c < lo.rolling(5).min().shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["atr_mult"]) * _atr(bars_df, 14)
    lf = le.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, (c + d * float(p["tp_perc"]) / 100).shift(1) / o - 1)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
