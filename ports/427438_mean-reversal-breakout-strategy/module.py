"""Buy the dip, long only, no bar size of its own: the low crossing under the SMA 10 of (low - 2 x
ATR 20) goes long; the long is closed 20 bars after its signal.
Port of FMZ strategy #427438 "Mean Reversal Breakout Strategy".

FMZ source id: 427438

Source
    https://www.fmz.com/strategy/427438 (PineScript v3, FMZ last modified 2023-09-21 10:35:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 121-134), dipness 2, smoothing 10, exit after 20 bars
    thedip = low - atr(20) x 2; buy = crossunder(low, sma(thedip, 10)) -> entry long
    buy[20] -> close long

Interpretation choices (Pine rules in SURVEY_README.md; skill section 5a)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending"
      (rule 1). precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df,
      params["bar_size"]); the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).
    * The time exit is an explicit exit signal 20 bars after the entry's signal (not
      max_hold_time). A new dip signal while long is ignored (pyramiding 0); an exit 20 bars after
      a signal that came while long still closes the position, as written.
    * Long only.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bar-count exit.
    2 generic: PASS, an ATR multiple.
    3 crypto-exchange-only: no.
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

NAME = "fmz_427438_buy_the_dip_atr"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dipness": [2.0, 1.0],
    "smoothness": [10, 20],
    "lookforward": [20, 10],
}
DEFAULT_PARAMS = {"dipness": 2.0, "smoothness": 10, "lookforward": 20, "atr_length": 20}


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


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    dip = lo - _rma(tr, int(p["atr_length"])) * p["dipness"]
    ds = dip.rolling(int(p["smoothness"])).mean()
    buy = ((lo < ds) & (lo.shift(1) >= ds.shift(1))).to_numpy()
    k = int(p["lookforward"])
    out = np.concatenate((np.zeros(k, dtype=bool), buy[:-k])) if k < len(buy) else np.zeros(len(buy), dtype=bool)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and out[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
