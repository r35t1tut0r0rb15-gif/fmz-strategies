"""EMA 9 / 21 crosses with RSI 14 off its extremes and a 2.5 ATR stop / 5 ATR target, bar size pending: EMA 9 crossing
above EMA 21 with RSI above 30 goes long; crossing below with RSI below 70 goes short.
Port of FMZ strategy #483063 "基于EMA交叉与RSI过滤的自适应动态止盈止损策略-Adaptive-Dynamic-Stop-Loss-and-Take-Profit-Strategy-Based-on-EMA-Crossover-and-RSI-Filter" (High Win Rate Dogecoin Strategy).

FMZ source id: 483063

Source
    https://www.fmz.com/strategy/483063 (PineScript v6, FMZ last modified 2025-02-27 17:06:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 85-116), EMA 9 / 21, ATR 14 x 2.5, RSI 14 (70 / 30)
    long = crossover(ema9, ema21) and rsi > 30; short = crossunder(ema9, ema21) and rsi < 70
    entry + exit(limit = close +- 5 ATR, stop = close -+ 2.5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1). precompute builds
      the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size (never
      in GRID / DEFAULT_PARAMS). "Dogecoin" in the title is a label.
    * The bracket is fixed at the signal bar: sl_stop = atr_mult x ATR / close, tp_stop = 2 x sl_stop, shifted one bar
      inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, RSI and ATR multiples.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483063_ema9_21_cross_rsi_atr_bracket_pending"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.5, 1.5],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "atr_len": 14, "atr_mult": 2.5, "rr": 2.0, "rsi_len": 14,
                  "rsi_ob": 70, "rsi_os": 30}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi > p["rsi_os"])).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi < p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
