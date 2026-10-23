"""Hourly bars: the EMA 20 crossing over the EMA 50 above the EMA 200 with RSI 14 over 30, ATR 14 above its 10-bar average and volume above its 20-bar average goes long; the crossing under below the EMA 200 with RSI under 70 and the same filters goes short; no other exit; reversing.
Port of FMZ strategy #489042 "多指标协同EMA交叉量化策略-Multi-Indicator-Synergistic-EMA-Crossover-Quantitative-Strategy" (Multi-Indicator Synergistic EMA Crossover Quantitative Strategy).

FMZ source id: 489042

Source
    https://www.fmz.com/strategy/489042 (PineScript v6, FMZ last modified 2025-04-01 14:46:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 207-260), EMA 200 / 50 / 20 (a second EMA 50 is the one crossed); RSI 14 (30 / 70); ATR 14 > SMA 10 of ATR; volume > SMA 20
    long_condition = crossover(ema20, ema50_short) and close > ema200 and rsi > 30 and atr > sma(atr, 10) and volume > sma(volume, 20) -> entry Long
    short_condition = crossunder(ema20, ema50_short) and close < ema200 and rsi < 70 and the same filters -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: an opposite entry reverses, so the strategy is always in the market after the
      first signal. ema50 and ema50_short are the same EMA 50 (ema50 is unused). The title names
      ETH/USDT; the header is BTC_USDT. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings in the EMA 200 trend with volatility and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only (ETH/USDT named in the title)).
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

NAME = "fmz_489042_ema20_50_cross_ema200_rsi_atr_volume_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 12],
    "slow": [50, 26],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    e200 = c.ewm(span=200, adjust=False).mean()
    r = _rsi(c, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    filt = (atr > atr.rolling(10).mean()) & (v > v.rolling(20).mean())
    up_x = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    dn_x = (fast < slow) & (fast.shift(1) >= slow.shift(1))
    le = up_x & (c > e200) & (r > 30) & filt
    se = dn_x & (c < e200) & (r < 70) & filt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
