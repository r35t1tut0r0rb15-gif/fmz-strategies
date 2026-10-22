"""Z-score extremes with RSI and Supertrend confirmation, daily bars: a 75-bar z-score of at least 1.1 with the RSI 14 over 60 while Pine's Supertrend direction is negative (up) goes long, a z-score of -1.1 or less with the RSI under 40 while the direction is positive goes short; reversing.
Port of FMZ strategy #473141 "基于Z分数和超级趋势的动态交易策略多空切换系统-Z-Score-and-Supertrend-Based-Dynamic-Trading-Strategy-Long-Short-Switching-System" (Z-Score Long and Short Strategy with Supertrend).

FMZ source id: 473141

Source
    https://www.fmz.com/strategy/473141 (PineScript v5, FMZ last modified 2024-11-27 16:01:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-132), z = (close - SMA 75) / sd 75; thresholds +-1.1 (constants); RSI 14, 60 / 40; ta.supertrend(2, 11)
    z >= 1.1 and rsi > 60 and direction < 0 -> entry Long;  z <= -1.1 and rsi < 40 and direction > 0 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's ta.supertrend direction is -1 in an up trend, so the long needs an up-trending Supertrend
      (the comments say "down", the code says direction < 0). The z-score uses the population standard
      deviation. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, z-score extremes with RSI and Supertrend confirmation.
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

NAME = "fmz_473141_zscore75_rsi_supertrend_confirm_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [75, 50],
    "factor": [2.0, 3.0],
}
DEFAULT_PARAMS = {"len": 75, "factor": 2.0, "atr_period": 11, "rsi_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    z = (c - c.rolling(n).mean()) / c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    dr, _ = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    dr = pd.Series(dr, index=c.index)
    le = (z >= 1.1) & (r > 60) & (dr < 0)
    se = (z <= -1.1) & (r < 40) & (dr > 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
