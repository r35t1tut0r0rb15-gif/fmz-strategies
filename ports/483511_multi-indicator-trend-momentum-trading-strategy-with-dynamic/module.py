"""Hourly bars: the EMA 20 crossing over the EMA 50 with RSI 14 over 30, a positive MACD histogram and volume over twice its 20-bar average goes long with a stop 3.5 ATR 14 under the signal close; the mirror goes short; reversing.
Port of FMZ strategy #483511 "Multi Indicator Trend Momentum Trading Strategy with Dynamic Risk Management System" (The Money Printer v2).

FMZ source id: 483511

Source
    https://www.fmz.com/strategy/483511 (PineScript v6, FMZ last modified 2025-02-24 09:50:52).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 92-177), EMA 20 / 50; RSI 14 (30 / 70); MACD 12 / 26 / 9; volume SMA 20 x 2; ATR 14; "trailing" stop 3.5 ATR; risk-based qty
    longEntry = crossover(ema20, ema50) and rsi > 30 and macd_hist > 0 and volume > 2 x sma(volume, 20) -> entry Long (qty = equity x 2 % / max(2.5 atr, 1)), exit("Trailing Stop", "Long", stop = close - 3.5 atr)
    shortEntry mirrored (rsi < 70) -> entry Short, exit(same id, "Short", stop = close + 3.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing" stop is a fixed level sent on the signal bar only, from that close: ported as a
      fraction of the fill, exact (1e-6 floor); there is no target. Both sides share one exit id, but the
      calls only happen on their own signal bars (which never coincide). The 2.5 ATR stop and the
      quantity (with its price-unit floor of 1) only size the trade. REVERSAL INTENDED. The risk-based
      quantity and 5 % of equity are sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal close as a fraction of the fill.
    2 generic: PASS, EMA crossings confirmed by RSI, MACD and volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based qty and 5 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against twice its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483511_ema20_50_cross_rsi_macd_volume_atr_stop_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_mult": [3.5, 2.5],
    "vol_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"stop_mult": 3.5, "vol_mult": 2.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    e1, e2 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    buy = (e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (r > 30) & (hist > 0) & vol_ok
    sell = (e1 < e2) & (e1.shift(1) >= e2.shift(1)) & (r < 70) & (hist < 0) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["stop_mult"]) * _atr(bars_df, 14)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
            .mask(sf, (c + d).shift(1) / o - 1))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
