"""EMA 9 / 21 trend breakouts with an RSI 50 filter and an ATR bracket, no bar size in the source: with EMA 9 above
EMA 21, RSI 14 above 50 and the close above the previous high the strategy goes long; the mirror goes short; each
trade has a stop 2 ATR away and a target 6 ATR away (the source's trailing stop is pending).
Port of FMZ strategy #491891 "多时间框架趋势突破策略与RSI过滤及ATR风险管理-Multi-Timeframe-Trend-Breakout-Strategy-with-RSI-Filter-and-ATR-Based-Risk-Management" (Trend Breakout Strategy with Separated Alerts).

FMZ source id: 491891

Source
    https://www.fmz.com/strategy/491891 (PineScript v5, FMZ last modified 2025-04-24 16:55:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-142), EMA 9 / 21, RSI 14, ATR 14, SL 2 ATR, TP 3 x SL, trail trigger 50 % of TP
    bull_trend = crossover(ema9, ema21) or ema9 > ema21;  bear_trend = the mirror
    long = bull_trend and rsi > 50 and close > high[1];  short = bear_trend and rsi < 50 and close < low[1]
    on entry: exit(stop = close -+ 2 ATR, limit = close +- 6 ATR, trail_points = 3 ATR, trail_offset = 2 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1). precompute
      builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies
      bar_size (never in GRID / DEFAULT_PARAMS).
    * The bracket is placed once, on the signal bar, from its close and ATR: sl_stop = 2 x ATR / close, tp_stop =
      3 x that, shifted one bar inside stops() and re-based on the fill price (house rule).
    * The trail (trail_points / trail_offset take ticks; the author passes ATR price distances, read as price
      distances as #427592): from 3 ATR of profit, a stop 2 ATR behind the best price. The house trail cannot start
      after an ATR-measured profit (activate_after is a fixed fraction, and with no bar size no fraction can be
      judged), so it is not emitted: mark trailing_stop_pending, described in PORT_NOTES.md.
    * Every signal bar is an entry (pyramiding 0: a same-side signal while held is ignored by Pine and the engine
      alike); entries reverse (REVERSAL INTENDED). A long and a short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (driver D4). The alert flags are not signals.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar; the trail pending (mark).
    2 generic: PASS, EMAs, RSI and ATR multiples.
    3 crypto-exchange-only: no.
    4 signals only: the 2 %-risk quantity quoted; the bracket ported via stops(); all exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491891_ema_trend_breakout_rsi_atr_bracket"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 1.0],
    "tp_ratio": [3.0, 1.5],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 21, "rsi_len": 14, "atr_len": 14, "sl_atr": 2.0, "tp_ratio": 3.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((ef > es) & (rsi > 50) & (c > h.shift(1))).astype(bool)
    short_e = ((ef < es) & (rsi < 50) & (c < lo.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dist = p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": dist.shift(1), "tp_stop": (p["tp_ratio"] * dist).shift(1)}


def portfolio_kwargs(**params):
    return {}
