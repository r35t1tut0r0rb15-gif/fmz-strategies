"""Hourly bars: a green bar with RSI 14 under 30 on volume over 1.5 x its 20-bar average goes long with a stop 1 ATR 14 under its low and a target at twice that risk; a red bar with RSI over 70 on such volume goes short (mirrored); reversing.
Port of FMZ strategy #482875 "Volume Spike and RSI Enhanced Trading Strategy" (Volume Spike & RSI Scalping (Session Restricted)).

FMZ source id: 482875

Source
    https://www.fmz.com/strategy/482875 (PineScript v6, FMZ last modified 2025-02-20 16:08:21).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 106-146), RSI 14 (30 / 70); volume SMA 20 x 1.5; ATR 14; RR 2
    long_condition = volume_spike and rsi < 30 and close > open -> stop_loss = low - atr, take_profit = close + (close - stop_loss) x 2, entry Buy, exit("Take Profit/Stop Loss", "Buy", ...)
    short_condition = volume_spike and rsi > 70 and close < open -> mirrored, entry Sell, exit(same id, "Sell", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars, as levels from that bar: ported as fractions of the fill, exact
      (1e-6 floor). Both sides share one exit id, but a long and a short signal never meet on one bar, so
      each trade keeps its own bracket until the opposite entry reverses it; a repeated signal while in
      the trade re-sends it from the new bar (not followed: trailing_stop_pending). There is no session
      code despite the title. REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; candle-ATR bracket at the signal bar as fractions of the fill.
    2 generic: PASS, RSI extremes with reversal candles on volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h; the title's session restriction is not in the code).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482875_rsi_extreme_candle_volume_spike_atr_rr2_1h_reversal"
FAMILY = "rsi_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 1.5],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"rr": 2.0, "vol_mult": 1.5}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    r = _rsi(c, 14)
    spike = v > v.rolling(20).mean() * float(p["vol_mult"])
    buy = spike & (r < 30) & (c > o)
    sell = spike & (r > 70) & (c < o)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    atr = _atr(bars_df, 14)
    rr = float(p["rr"])
    sl_l, sl_s = lo - atr, h + atr
    tp_l, tp_s = c + (c - sl_l) * rr, c - (sl_s - c) * rr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - sl_l.shift(1) / o)
            .mask(sf, sl_s.shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, tp_l.shift(1) / o - 1)
            .mask(sf, 1 - tp_s.shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
