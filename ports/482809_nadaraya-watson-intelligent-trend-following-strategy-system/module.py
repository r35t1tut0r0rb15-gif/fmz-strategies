"""Crosses of a 500-bar Gaussian-kernel (Nadaraya-Watson) smoothing of the close and its 15-bar SMA, alternating long
and short after the first long, daily bars.
Port of FMZ strategy #482809 "基于Nadaraya-Watson核估计和移动平均交叉的智能趋势跟踪策略系统-Intelligent-Trend-Following-Strategy-System-Based-on-Nadaraya-Watson-Kernel-Estimation-and-Moving-Average-Crossover" (Nadaraya-Watson Strategy with Moving Average Crossover).

FMZ source id: 482809

Source
    https://www.fmz.com/strategy/482809 (PineScript v5, FMZ last modified 2025-02-20 14:54:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-148), bandwidth 8, MA lookback 15
    smoothed = sum(close[i] x w_i) / sum(w_i), i = 0..499, w_i = exp(-i^2 / (2 h^2)) (past bars only)
    crossover(smoothed, sma(smoothed, 15)) and not inPosition -> entry long, inPosition := true
    crossunder(...) and inPosition -> entry short, inPosition := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel sums 500 past closes: na until 500 bars exist (close[i] is na before the first bar), as written.
    * inPosition only alternates the two signals: a short cross before the first long is ignored; afterwards every
      cross reverses (REVERSAL INTENDED), so the strategy is always in. Signal module, no stops.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a kernel smoothing and an SMA of it.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_482809_nadaraya_watson_sma_cross_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bandwidth": [8.0, 4.0],
    "lookback": [15, 30],
}
DEFAULT_PARAMS = {"bandwidth": 8.0, "lookback": 15, "window": 500}


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


def _kernel(c, h, window):
    w = np.exp(-(np.arange(window, dtype=float) ** 2) / (h * h * 2))
    v = c.to_numpy(dtype=float)
    full = np.convolve(v, w)[:len(v)] / w.sum()          # out[t] = sum_i v[t - i] w[i]
    full[:window - 1] = np.nan                           # close[i] is na before the first bar
    return pd.Series(full, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sm = _kernel(bars_df["close"], float(p["bandwidth"]), int(p["window"]))
    ma = sm.rolling(int(p["lookback"])).mean()
    up = ((sm > ma) & (sm.shift(1) <= ma.shift(1))).to_numpy()
    dn = ((sm < ma) & (sm.shift(1) >= ma.shift(1))).to_numpy()
    m = len(up)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False                                         # var bool inPosition
    for i in range(m):
        if up[i] and not held:
            le[i], held = True, True
        if dn[i] and held:
            se[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
