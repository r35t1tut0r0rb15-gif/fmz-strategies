"""Stochastic-RSI crossings on the side of an hourly pivot with ROC confirmation, daily bars: %K crossing over %D with the close above the pivot and ROC 9 positive goes long, the mirror goes short;
reversing.
Port of FMZ strategy #449957 "Pivot-and-Momentum-Strategy-枢轴动量策略" (Pivot and Momentum).

FMZ source id: 449957

Source
    https://www.fmz.com/strategy/449957 (PineScript v5, FMZ last modified 2024-04-30 16:39:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-154), pivot from the 60-minute high / low / close [1]; stochastic RSI 3 / 3 / 14 / 14; ROC 9
    pivot = (security("60", high[1]) + low[1] + close[1]) / 3;  close > pivot and crossover(k, d) and roc > 0 -> close short, entry long;  close < pivot and crossunder(k, d) and roc < 0 -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 60-minute request is a lower time frame than the daily chart, so it returns the day's LAST
      hourly bar's value of high[1] / low[1] / close[1], i.e. the day's second-last hourly bar (as
      #436765), built from left-labelled hourly bars grouped by broker day. R1 / S1 only plot. Each
      close comes with the opposite entry: one reversal. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the hourly values end with the daily bar.
    2 generic: PASS, stochastic-RSI crossings with a pivot side and ROC sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449957_hourly_pivot_side_stochrsi_cross_roc_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "roc_len": [9, 14],
    "stoch_len": [14, 9],
}
DEFAULT_PARAMS = {"roc_len": 9, "stoch_len": 14, "rsi_len": 14, "k": 3, "d": 3}


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
    h1 = df.resample("1h", label="left", closed="left").agg(
        {"high": "max", "low": "min", "close": "last"}).dropna(how="all")
    piv = (h1["high"].shift(1) + h1["low"].shift(1) + h1["close"].shift(1)) / 3
    bars["pivot"] = piv.groupby(broker_day(h1.index)).last()          # the day's last hourly bar's [1] values
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    piv = bars_df["pivot"]
    r = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(sn).min(), r.rolling(sn).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r).where(hi_r > lo_r)
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    rl = int(p["roc_len"])
    roc = 100 * (c - c.shift(rl)) / c.shift(rl)
    le = (c > piv) & (k > d) & (k.shift(1) <= d.shift(1)) & (roc > 0)
    se = (c < piv) & (k < d) & (k.shift(1) >= d.shift(1)) & (roc < 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
