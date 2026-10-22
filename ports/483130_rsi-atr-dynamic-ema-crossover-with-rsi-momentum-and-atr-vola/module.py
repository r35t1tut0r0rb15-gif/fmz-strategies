"""EMA 9 / 21 crossings with RSI 14 under 70 / over 30, hourly bars: the up-cross goes long and the down-cross goes short, each with a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #483130 "动态均线交叉结合RSI动量和ATR波动率的多层级确认交易策略-Dynamic-EMA-Crossover-with-RSI-Momentum-and-ATR-Volatility-Multi-Level-Confirmation-Trading-Strategy" (BTC Scalping Strategy).

FMZ source id: 483130

Source
    https://www.fmz.com/strategy/483130 (PineScript v5, FMZ last modified 2025-02-21 14:53:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-143), EMA 9 / 21; RSI 14 / 70 / 30; ATR 14; stop 1.5 ATR; target 3 ATR; risk 1 % sizing; pyramiding 1
    crossover(ema9, ema21) and rsi < 70 -> entry Long + exit(limit = close + 3 atr, stop = close - 1.5 atr)
    crossunder(ema9, ema21) and rsi > 30 -> entry Short + exit(limit = close - 3 atr, stop = close + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). The crossings alternate. An entry on
      the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The
      risk-sized quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-sized quantity stored, not ported.
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

NAME = "fmz_483130_ema9_21_cross_rsi_atr1_5_3_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_fast_length": [9, 5],
    "ema_slow_length": [21, 50],
}
DEFAULT_PARAMS = {"ema_fast_length": 9, "ema_slow_length": 21, "rsi_length": 14, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["ema_fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    lvl = {"l_sl": c - 1.5 * atr, "l_tp": c + 3 * atr, "s_sl": c + 1.5 * atr, "s_tp": c - 3 * atr}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
