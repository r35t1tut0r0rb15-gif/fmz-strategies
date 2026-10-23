"""Five averages of the close over 136 bars (VWMA, RMA, SMA, WMA and EMA) all rising goes long, all falling goes short; reversing; no bar size in the source.
Port of FMZ strategy #434606 "移动平均线聚合MACD策略Moving-Average-Aggregation-MACD-Strategy" (MACD Multi-MA Strategy).

FMZ source id: 434606

Source
    https://www.fmz.com/strategy/434606 (PineScript v2, FMZ last modified 2023-12-07 17:35:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 81-119), fast 8, slow 144: every average uses length 144 - 8 = 136
    ma = vwma(close, 136), ma1 = rma(close, 136), ma2 = sma, ma3 = wma, ma4 = ema (all 136)
    all five above their previous values -> entry Long;  all five below -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every average uses len2 - len1 = 136, as written (the "MACD" in the title is never computed). No
      exits: the opposite entry reverses. No backtest header or input names a bar size: FREQ =
      "bar_size_pending"; the bars come from the house bar_sizes.build_bars. REVERSAL INTENDED. No sizing
      code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average slope agreement.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) in vwma(close, 136); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_434606_five_ma_136_slope_agreement_reversal"
FAMILY = "ma_slope"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [8, 20],
    "len2": [144, 100],
}
DEFAULT_PARAMS = {"len1": 8, "len2": 144}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["len2"]) - int(p["len1"])
    vs = v.rolling(n).sum()
    mas = [(c * v).rolling(n).sum() / vs.where(vs != 0), _rma(c, n), c.rolling(n).mean(), _wma(c, n),
           c.ewm(span=n, adjust=False).mean()]
    up = np.logical_and.reduce([(m > m.shift(1)).to_numpy() for m in mas])
    dn = np.logical_and.reduce([(m < m.shift(1)).to_numpy() for m in mas])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up, index=ix), false, pd.Series(dn, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
