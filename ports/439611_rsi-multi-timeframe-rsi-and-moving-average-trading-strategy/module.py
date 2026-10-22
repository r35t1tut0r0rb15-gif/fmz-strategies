"""Stochastic RSI crosses in the SMA 5 / WMA 144 trend, 1-hour bars: a stochastic RSI cross up under 20 with the SMA 5 above the WMA 144 goes long, a cross down over 80 with it below goes short; each trade has
a stop 2 ATR beyond the 20-bar swing and a target as far again plus 6 ATR; reversing.
Port of FMZ strategy #439611 "基于RSI和平均线的多时间框架交易策略Multi-timeframe-RSI-and-Moving-Average-Trading-Strategy" (Stoch + WMA + SMA strat).

FMZ source id: 439611

Source
    https://www.fmz.com/strategy/439611 (PineScript v4, FMZ last modified 2024-01-22 11:00:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-226), swing stop and target on, lookback 20, SL expander 10, TP expander 30; reverse off; trailing off; stochastic RSI 14 / 14 / 3 / 3, levels 20 / 80; WMA 144
    stobuy = crossover(k, d) and k < 20;  stosell = crossunder(k, d) and k > 80;  mabuy = sma 5 > wma 144 (security "60" on the 1-hour chart reads the same)
    LSL = swing low(20) - atr(14) / 5 x 10;  lTP = avg + (avg - swing low) + atr / 5 x 30 (fixed when the position changes);  short mirror;  exit(stop = SL, limit = TP) each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("60") on the 1-hour chart is the chart's own value. The swing levels and the ATR are
      fixed when the position changes (the fill bar, read at its close); the port takes them from the
      signal bar, as #434998: sl_stop = (close - (swing low - 2 ATR)) / close and tp_stop = (close -
      swing low + 6 ATR) / close of the signal bar for a long (the mirror for a short), shifted one bar
      inside stops() and re-based on the fill. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing bracket from the signal bar.
    2 generic: PASS, stochastic RSI, averages, swing levels and ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439611_stoch_rsi_sma5_wma144_swing_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing": [20, 10],
    "tp_exp": [30, 15],
}
DEFAULT_PARAMS = {"swing": 20, "tp_exp": 30, "sl_exp": 10, "stoch_os": 20, "stoch_ob": 80, "smooth_k": 3,
                  "smooth_d": 3, "length_rsi": 14, "length_stoch": 14, "wma_len": 144}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _signals(bars_df, p):
    c = bars_df["close"]
    r = _rsi(c, int(p["length_rsi"]))
    n = int(p["length_stoch"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100 * (r - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    stobuy = (k > d) & (k.shift(1) <= d.shift(1)) & (k < float(p["stoch_os"]))
    stosell = (k < d) & (k.shift(1) >= d.shift(1)) & (k > float(p["stoch_ob"]))
    w = _wma(c, int(p["wma_len"]))
    s5 = c.rolling(5).mean()
    mabuy = s5 > w
    mabear = (s5 <= w) & w.notna() & s5.notna()
    return stobuy & mabuy, stosell & mabear


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    c = bars_df["close"]
    n = int(p["swing"])
    sw_lo, sw_hi = bars_df["low"].rolling(n).min(), bars_df["high"].rolling(n).max()
    a5 = _atr(bars_df, 14) / 5
    slx, tpx = float(p["sl_exp"]) * a5, float(p["tp_exp"]) * a5
    sl = ((c - (sw_lo - slx)) / c).where(up, ((sw_hi + slx - c) / c).where(dn))
    tp = ((c - sw_lo + tpx) / c).where(up, ((sw_hi - c + tpx) / c).where(dn))
    return {"sl_stop": sl.where(sl > 0).shift(1), "tp_stop": tp.where(tp > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
