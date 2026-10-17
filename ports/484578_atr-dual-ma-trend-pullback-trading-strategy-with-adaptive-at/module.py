"""EMA 10 / 50 trend pullbacks reclaiming the fast EMA with a 2 ATR stop and a 4 ATR target, 2-hour bars: in an up-trend,
after a bar closing under EMA 10 but holding above EMA 50, a bar opening under EMA 10 and closing above it goes long;
the down-trend mirror goes short; the target is twice the stop distance.
Port of FMZ strategy #484578 "双均线趋势回调自适应ATR止盈止损量化交易策略-Dual-MA-Trend-Pullback-Trading-Strategy-with-Adaptive-ATR-Based-Risk-Management" (Pullback Strategy).

FMZ source id: 484578

Source
    https://www.fmz.com/strategy/484578 (PineScript v5, FMZ last modified 2025-03-03 09:49:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 195-237), EMA 10 / 50, ATR 14, stop x 2, target 2 x the stop distance
    pullback = trend_up and close < ema10 and low > ema50;  long = trend_up and pullback[1] and open < ema10 and
    close > ema10 (short mirrored with high < ema50);  entry + exit(stop = close -+ 2 ATR, limit = close +- 4 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = 2 x that, shifted one bar
      inside stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, EMAs and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484578_ema_pullback_reclaim_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 1.5],
    "fast": [10, 20],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "atr_len": 14, "sl_mult": 2.0, "tp_ratio": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up, dn = f > s, f < s
    pull = up & (c < f) & (lo > s)
    rally = dn & (c > f) & (h < s)
    long_e = (up & pull.shift(1, fill_value=False) & (o < f) & (c > f)).astype(bool)
    short_e = (dn & rally.shift(1, fill_value=False) & (o > f) & (c < f)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
