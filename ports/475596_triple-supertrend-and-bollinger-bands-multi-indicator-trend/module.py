"""Bollinger 20 / 2 breakouts with three supertrends (ATR 10 x 3 / 4 / 5) agreeing, bar size from the driver: a close over the upper band with all three up goes long, under the lower band with all three down goes short; any supertrend turning against the position closes it; reversing.
Port of FMZ strategy #475596 "Triple Supertrend and Bollinger Bands Multi Indicator Trend Following Strategy" (Demo GPT - Bollinger + Triple Supertrend Combo).

FMZ source id: 475596

Source
    https://www.fmz.com/strategy/475596 (PineScript v5, FMZ last modified 2024-12-20 14:28:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-209), BB 20, 2 sd; supertrends 10 / 3, 10 / 4, 10 / 5; commission 0.1 %, slippage 3; no backtest header
    close > upper and dir1 < 0 and dir2 < 0 and dir3 < 0 and size <= 0 -> entry Long;  long and (dir1 > 0 or dir2 > 0 or dir3 > 0) -> close Long;  close < lower and all dir > 0 and size >= 0 -> entry Short;  short and any dir < 0 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending"; precompute
      builds the bars with the house bar_sizes.build_bars with the driver's bar_size. Pine's supertrend
      direction -1 is the up-trend. A close coinciding with the opposite entry only repeats the
      reversal (#437773), so it is masked on entry bars. The date window is always true. REVERSAL
      INTENDED. The costs are not ported.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with three agreeing supertrends.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_475596_bb20_break_triple_supertrend_agree_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_bb": [20, 50],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"length_bb": 20, "atr_period": 10, "mult_bb": 2.0}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length_bb"])
    basis = c.rolling(n).mean()
    dev = float(p["mult_bb"]) * c.rolling(n).std(ddof=0)
    k = int(p["atr_period"])
    d1, d2, d3 = (_supertrend(bars_df, f, k)[1] for f in (3.0, 4.0, 5.0))
    all_up = (d1 < 0) & (d2 < 0) & (d3 < 0)
    all_dn = (d1 > 0) & (d2 > 0) & (d3 > 0)
    le = (c > basis + dev) & all_up
    se = (c < basis - dev) & all_dn
    lx = ((d1 > 0) | (d2 > 0) | (d3 > 0)) & ~se
    sx = ((d1 < 0) | (d2 < 0) | (d3 < 0)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
