"""Hourly bars, long only: from flat, a close 1 % above the SMA 20, above the SMA 44 and 100 and the previous high (but not within 0.7 % of its own high), with RSI 14 above 50 and volume above its SMA 10, goes long, but only more than 10 bars after the last exit unless the SMA 20 / 44 just crossed; a 15 % target from the entry price, and a bar whose low is 3 % under the entry price closes it at the next open.
Port of FMZ strategy #440535 "Crossover Strategy of Moving Average Lines and Resistance Level Breakout" (Advanced Strategy with Conditional Stop Loss).

FMZ source id: 440535

Source
    https://www.fmz.com/strategy/440535 (PineScript v5, FMZ last modified 2024-01-31 14:34:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 143-194), SMA 20 / 44 / 100; RSI 14; volume SMA 10; target 15 %; stop 3 % (bar-close test); wait 10 bars
    buy_condition = (ma_cross and close > high[1] or bar_index - last_sell_candle > 10) and uptrend and close > ma20 x 1.01 and close > ma44 and close > ma100 and close > high[1] and rsi > 50 and volume > volumeAvg and not close_near_high
    position_size > 0: exit(limit = avg x 1.15);  low < avg x 0.97 -> close("Buy")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a limit order at the entry price + 15 %: ported as a fixed tp_stop of the fill; Pine
      sends it from the fill bar's close, the port arms it at the fill (a 15 % move within the fill bar
      is the only difference). The stop is a bar-close test of the low (the position closes at the next
      open), in the signals. last_sell_candle is the bar on which the position became flat (target or
      stop), tracked in the signals. Long only. No sizing code. Stop module: portfolio_kwargs {} (driver
      D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed target from the fill; bar-close stop in the signals.
    2 generic: PASS, trend-filtered breakouts with a post-exit wait.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440535_ma_stack_breakout_wait_15pct_target_close_stop_1h_long_only"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "profit_target": [0.15, 0.05],
    "wait_candles": [10, 20],
}
DEFAULT_PARAMS = {"profit_target": 0.15, "stop_loss": 0.03, "wait_candles": 10}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    m20, m44, m100 = c.rolling(20).mean(), c.rolling(44).mean(), c.rolling(100).mean()
    rsi = _rsi(c, 14)
    vol_ok = v > v.rolling(10).mean()
    cross = (((m20 > m44) & (m20.shift(1) <= m44.shift(1))) | ((m20 < m44) & (m20.shift(1) >= m44.shift(1))))
    near_high = (c >= h * 0.993) & (c <= h)
    base = ((c > m20) & (c > m20 * 1.01) & (c > m44) & (c > m100) & (c > h.shift(1)) & (rsi > 50) & vol_ok & ~near_high)
    after_cross = (cross & (c > h.shift(1))).to_numpy()
    base = base.to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    tp, sl, wait = float(p["profit_target"]), float(p["stop_loss"]), int(p["wait_candles"])
    m = len(base)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out, px, last_sell = 0, False, False, np.nan, 0
    for i in range(m):
        flat_now = False
        if pend_in:
            pos, pend_in, px = 1, False, ov[i]
        if pend_out:
            pos, pend_out, flat_now = 0, False, True
        if pos == 1 and hv[i] >= px * (1 + tp):           # the limit target fills inside the bar
            pos, flat_now = 0, True
        if flat_now:
            last_sell = i
        if pos == 1:
            if lv[i] < px * (1 - sl) and i + 1 < m:
                lx[i], pend_out = True, True
        elif not pend_in and base[i] and (after_cross[i] or i - last_sell > wait) and i + 1 < m:
            le[i], pend_in = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["profit_target"])}


def portfolio_kwargs(**params):
    return {}
