"""Bollinger 30 / 1.5 snap-backs with an RSI 9 dip, no bar size in the source, long only: after a close under the lower band, a green bar with the RSI 9 at or under 25 buys from flat, with a stop 2 ATR 10 under and a target 2 ATR over the signal bar's low; an RSI over 75 closes all.
Port of FMZ strategy #458034 "RSI-布林通道整合策略动态自适应的多指标交易系统-RSI-Bollinger-Bands-Integration-Strategy-A-Dynamic-Self-Adaptive-Multi-Indicator-Trading-System" (BB-RSI-Benac-Long).

FMZ source id: 458034

Source
    https://www.fmz.com/strategy/458034 (PineScript v5, FMZ last modified 2024-07-29 14:00:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 170-226), Bollinger 30 / 1.5; RSI 9 (labelled 13); ATR 10; stop / target 2 ATR from the signal bar's low
    close[2] < lower[1] and close[1] > open[1] and rsi[1] <= 25 and flat -> entry Long, stop = low - 2 atr, target = low + 2 atr
    long: exit(limit = target, stop = stop);  rsi > 75 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed on the signal bar from its low and ATR: ported as fractions of the signal
      close ((close - (low - 2 atr)) / close and (low + 2 atr - close) / close), applied to the fill and
      followed in the loop on each bar's low / high so the flat test lines up; a signal whose target
      sits at or under its close would fill at once and is sent as no trade. The exit is sent while in
      the position, ported active from the fill bar (#440797). The RSI close is a bar-close test. The
      source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. Long
      only. Stop module: portfolio_kwargs {} (driver D4). No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-low levels as fractions; from flat in a loop.
    2 generic: PASS, band snap-backs with an RSI dip.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458034_bollinger_snapback_rsi9_dip_atr_bracket_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_len": [30, 20],
    "rsi_len": [9, 14],
    "atr_mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"bb_len": 30, "bb_mult": 1.5, "rsi_len": 9, "atr_mult": 2.0, "atr_len": 10}


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
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["bb_len"])
    lower = c.rolling(n).mean() - float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    sig = ((c.shift(2) < lower.shift(1)) & (c.shift(1) > o.shift(1)) & (r.shift(1) <= 25)).to_numpy()
    out = (r > 75).to_numpy()
    a = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"])
    sl_f = ((c - (lo - a)) / c).to_numpy()
    tp_f = ((lo + a - c) / c).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_a, tp_a = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, fi, slf, tpf = 0, 0, -1, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, fi = 1, i
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and (lv[i] <= ov[fi] * (1 - slf) or hv[i] >= ov[fi] * (1 + tpf)):
            pos = 0                              # the stop or target fills inside the bar
        if sig[i] and pos == 0 and i + 1 < m and sl_f[i] > 0 and tp_f[i] > 0:
            le[i], pend, slf, tpf = True, 1, sl_f[i], tp_f[i]
            sl_a[i], tp_a[i] = slf, tpf
        if out[i] and pos == 1:
            lx[i], pend = True, 2
    return le, lx, sl_a, tp_a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_a, tp_a = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl_a, index=ix).shift(1), "tp_stop": pd.Series(tp_a, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
