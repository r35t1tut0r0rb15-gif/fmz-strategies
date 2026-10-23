"""Hourly bars, long only: the EMA 50 crossing over the EMA 200 with RSI 14 over 50 on volume over 1.5 x its 20-bar average goes long; the mirror crossing (RSI under 50, same volume test) closes it; a stop 1.5 ATR 14 under each bar's low and a target 3 x that distance above its close, re-sent every bar, are followed in the signals.
Port of FMZ strategy #481338 "三均线交叉趋势跟踪策略结合RSI和成交量确认系统-Triple-EMA-Crossover-Trend-Following-Strategy-with-RSI-and-Volume-Confirmation-System" (EMA Crossover Strategy).

FMZ source id: 481338

Source
    https://www.fmz.com/strategy/481338 (PineScript v5, FMZ last modified 2025-02-10 14:16:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 96-137), EMA 50 / 200; RSI 14; volume SMA 20 x 1.5; ATR 14; SL = low - 1.5 ATR, TP = close + 3 x (close - SL)
    buyCondition = crossover(ema50, ema200) and rsi > 50 and volume > sma(volume, 20) x 1.5 -> entry Long;  sellCondition = crossunder(...) and rsi < 50 and the volume test -> close Long
    every bar: exit("Take Profit", "Long", limit = close + (close - sl) x 3, stop = low - 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is re-sent every bar from that bar's low, close and ATR (including the signal bar, for the
      pending entry), so its levels move both ways; the house engine cannot move a bracket that way, so
      the signals follow it: a bar whose low reaches the previous bar's stop or whose high reaches its
      target closes the trade at the next open (mark trailing_stop_pending). The close needs the volume
      test too, so a quiet crossing under leaves the long open. Long only. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent bracket followed in the signals.
    2 generic: PASS, EMA 50 / 200 crossings with RSI and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481338_ema50_200_cross_rsi_volume_rolling_atr_bracket_1h_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_atr": [1.5, 2.5],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "sl_atr": 1.5, "rr": 3.0}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean() * 1.5
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & vol_ok).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & (r < 50) & vol_ok).to_numpy()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    stop = lo - float(p["sl_atr"]) * atr
    tgt = (c + (c - stop) * float(p["rr"])).to_numpy(dtype=float)
    stop = stop.to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and (ln[i] <= stop[i - 1] or hn[i] >= tgt[i - 1]):
            held = 0                       # the exit sent at the previous close is touched
        new = held
        if buy[i] and new == 0:
            new = 1
        elif sell[i] and held == 1:
            new = 0
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            else:
                lx[i] = True
            vpos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
