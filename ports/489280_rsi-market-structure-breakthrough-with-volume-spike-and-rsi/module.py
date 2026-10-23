"""Hourly bars, from flat only: the close crossing above the last confirmed swing low (pivots 5 / 5) on volume over 2 x its 20-bar average with RSI 14 under 50 goes long; the close crossing below the last swing high on the same spike with RSI over 50 goes short; every trade closes on the 3rd bar after its signal bar, at the next open.
Port of FMZ strategy #489280 "市场结构突破与成交量峰值RSI多重指标交叉策略-Market-Structure-Breakthrough-with-Volume-Spike-and-RSI-Confluence-Strategy" (SMC Structure Break with Volume Spike + RSI Confluence).

FMZ source id: 489280

Source
    https://www.fmz.com/strategy/489280 (PineScript v5, FMZ last modified 2025-04-03 10:23:22).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 168-235), pivothigh / pivotlow 5 / 5; volume SMA 20 x 2; RSI 14 (50); hold 3 bars from the signal bar; initial capital
    long_condition = close > last_swing_low and close[1] <= last_swing_low and vol_spike and rsi < 50;  short_condition = close < last_swing_high and close[1] >= last_swing_high and vol_spike and rsi > 50
    position_size == 0: entry Long / Short, entryBar := bar_index;  position open and bar_index - entryBar >= 3 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels are the last confirmed pivots (seen 5 bars after the pivot bar, strict). The
      "break" crosses the swing LOW upwards for a long and the swing HIGH downwards for a short, as
      written. entryBar is the signal bar, so the close is sent on the 3rd bar after it and the trade
      holds three bars. Opposite entries cannot occur (entries only from flat). Initial capital is stored,
      not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a 3-bar time exit in the signals.
    2 generic: PASS, swing-level crossings on volume spikes with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: initial capital only (no sizing).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489280_swing_level_cross_volume_spike_rsi_3bar_hold_1h"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [3, 6],
    "vol_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"swing_len": 5, "hold": 3, "vol_mult": 2.0}


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


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k = int(p["swing_len"])
    ph, phv = _pivot_hit(h, 1, k, k)
    pl, plv = _pivot_hit(lo, -1, k, k)
    lsh = _fixnan(pd.Series(np.where(ph, phv, np.nan), index=c.index))
    lsl = _fixnan(pd.Series(np.where(pl, plv, np.nan), index=c.index))
    spike = v > v.rolling(20).mean() * float(p["vol_mult"])
    r = _rsi(c, 14)
    buy = (lsl.notna() & (c > lsl) & (c.shift(1) <= lsl) & spike & (r < 50)).to_numpy()
    sell = (lsh.notna() & (c < lsh) & (c.shift(1) >= lsh) & spike & (r > 50)).to_numpy()
    hold = int(p["hold"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, eb = 0, -1
    for i in range(m):
        held = tgt                          # the position after this bar's open
        if i + 1 >= m:
            break
        if held == 0:
            if sell[i]:                     # the later call wins (the two cannot coincide: RSI 50)
                se[i], tgt, eb = True, -1, i
            elif buy[i]:
                le[i], tgt, eb = True, 1, i
        elif i - eb >= hold:
            if held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
