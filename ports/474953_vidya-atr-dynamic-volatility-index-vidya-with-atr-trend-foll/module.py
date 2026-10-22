"""VIDYA band breaks, daily bars: the close crossing over the smoothed VIDYA (10, momentum 20) plus 2 ATR 200 goes long, crossing under it minus 2 ATR 200 goes short; reversing.
Port of FMZ strategy #474953 "动态波动率指标VIDYA结合ATR趋势跟踪反转策略-Dynamic-Volatility-Index-VIDYA-with-ATR-Trend-Following-Reversal-Strategy" (VIDYA Auto-Trading(Reversal Logic)).

FMZ source id: 474953

Source
    https://www.fmz.com/strategy/474953 (PineScript v5, FMZ last modified 2024-12-13 10:21:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-160), VIDYA length 10, momentum 20; SMA 15 smoothing; band 2 x ATR 200
    vidya := a x |cmo| / 100 x src + (1 - a x |cmo| / 100) x nz(vidya[1]) (var 0);  v = sma(vidya, 15);  crossover(close, v + 2 atr200) -> close Sell, entry Buy;  crossunder(close, v - 2 atr200) -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VIDYA is the source's recursion from a var seed of 0 with nz of the previous value (so it
      climbs from 0 at the start, and restarts from 0 after any na CMO, as written), then its SMA 15;
      CMO over 20 bars. The closes only repeat the reversals. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive-average ATR band breaks.
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

NAME = "fmz_474953_vidya10_atr200_band_break_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vidya_length": [10, 20],
    "band": [2.0, 1.5],
}
DEFAULT_PARAMS = {"vidya_length": 10, "band": 2.0, "momentum": 20}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mom = c.diff()
    n = int(p["momentum"])
    pos_sum = mom.where(mom >= 0, 0.0).where(mom.notna(), 0.0).rolling(n).sum()
    neg_sum = (-mom).where(mom < 0, 0.0).where(mom.notna()).rolling(n).sum()   # -na stays na
    cmo = (100 * (pos_sum - neg_sum) / (pos_sum + neg_sum)).abs().to_numpy(dtype=float)
    alpha = 2 / (int(p["vidya_length"]) + 1)
    s = c.to_numpy(dtype=float)
    v = np.full(len(s), np.nan)
    prev = 0.0
    for i in range(len(s)):
        k = alpha * cmo[i] / 100
        v[i] = k * s[i] + (1 - k) * prev if not np.isnan(k) else np.nan
        prev = 0.0 if np.isnan(v[i]) else v[i]
    vid = pd.Series(v, index=c.index).rolling(15).mean()
    atr = _atr(bars_df, 200) * float(p["band"])
    up, dn = vid + atr, vid - atr
    le = (c > up) & (c.shift(1) <= up.shift(1))
    se = (c < dn) & (c.shift(1) >= dn.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
