"""A hand-built SuperTrend-style band (hl2 -/+ 3 ATR 10) state with Stochastic 14 / 3 / 3 crossings, broker days: bullish with %K over %D under 20 goes long, bearish with %K under %D over 80 goes short; reversing, no other exit.
Port of FMZ strategy #482831 "Momentum Enhanced SuperTrend Stochastic Dual Indicator Trading Strategy" (SuperTrend + Stochastic Strategy).

FMZ source id: 482831

Source
    https://www.fmz.com/strategy/482831 (PineScript v5, FMZ last modified 2025-02-20 14:51:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-181), ATR 10 x 3; Stochastic %K 14, smooth 3, %D 3; 10 % of equity
    upper = close[1] > upper[1] ? max(hl2 + 3 atr, upper[1]) : hl2 + 3 atr;  lower = close[1] < lower[1] ? min(hl2 - 3 atr, lower[1]) : hl2 - 3 atr
    isBullish = close > upper[1] ? true : close < lower[1] ? false : isBullish[1]
    isBullish and crossover(k, d) and k < 20 -> entry Long;  not isBullish and crossunder(k, d) and k > 80 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band recursions are kept as written (the upper band ratchets UP while the previous close is
      over it, the lower band DOWN while under it; the bands start from the first bar with an ATR).
      isBullish starts true and holds while the close stays between the previous bands. Entries only:
      each reverses the other side (REVERSAL INTENDED), no other exit. The 10 % of equity size is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band state with Stochastic crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482831_hl2_atr10_x3_band_state_stoch14_kd_cross_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [3.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"multiplier": 3.0, "atr_period": 10, "k_period": 14, "d_period": 3, "smooth_k": 3}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_period"])).to_numpy()
    mid = ((h + lo) / 2).to_numpy(dtype=float)
    k_ = float(p["multiplier"])
    ub_b, lb_b = mid + k_ * atr, mid - k_ * atr
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    bull = np.zeros(m, dtype=bool)
    ub_p = lb_p = np.nan
    b = True
    for i in range(m):
        if np.isnan(ub_p):
            ub, lb = ub_b[i], lb_b[i]
        else:
            ub = max(ub_b[i], ub_p) if cv[i - 1] > ub_p else ub_b[i]
            lb = min(lb_b[i], lb_p) if cv[i - 1] < lb_p else lb_b[i]
        if cv[i] > ub_p:
            b = True
        elif cv[i] < lb_p:
            b = False
        bull[i] = b
        ub_p, lb_p = ub, lb
    n = int(p["k_period"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["d_period"])).mean()
    bs = pd.Series(bull, index=c.index)
    le = bs & (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20)
    se = ~bs & (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
