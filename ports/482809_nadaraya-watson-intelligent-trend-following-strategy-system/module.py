"""A one-sided Nadaraya-Watson (Gaussian, bandwidth 8, 500 bars) smoothing of the close crossing its SMA 15, broker days: the first up-cross goes long, then each down-cross reverses short and each up-cross reverses long; reversing.
Port of FMZ strategy #482809 "基于Nadaraya-Watson核估计和移动平均交叉的智能趋势跟踪策略系统-Intelligent-Trend-Following-Strategy-System-Based-on-Nadaraya-Watson-Kernel-Estimation-and-Moving-Average-Crossover" (Nadaraya-Watson Strategy with Moving Average Crossover).

FMZ source id: 482809

Source
    https://www.fmz.com/strategy/482809 (PineScript v5, FMZ last modified 2025-02-20 14:54:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-152), bandwidth 8; 500-bar kernel loop; SMA 15; 10 % of equity; MPL 2.0 notice (UniCapInvest)
    smoothed = sum(src[i] * gauss(i, 8), i = 0..499) / sum(gauss(i, 8));  ma = sma(smoothed, 15)
    crossover(smoothed, ma) and not inPosition -> entry Long, inPosition := true;  crossunder(smoothed, ma) and inPosition -> entry Short, inPosition := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel weights only the current and past closes (lag i = 0..499), so it is causal; src[i] is na
      before bar 499, so smoothed is na there, as the na sum gives. The inPosition flag only stops a short
      before the first long: after it the crossings alternate, each reversing (REVERSAL INTENDED). The
      10 % of equity size is sizing. The MPL 2.0 notice is kept with the verbatim copy (ported, stated).
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, kernel-smoothed close crossing its SMA.
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

NAME = "fmz_482809_nadaraya_watson8_sma15_cross_alternating_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bandwidth": [8.0, 4.0],
    "lookback": [15, 30],
}
DEFAULT_PARAMS = {"bandwidth": 8.0, "lookback": 15, "kernel_bars": 500}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n, bw = int(p["kernel_bars"]), float(p["bandwidth"])
    lag = np.arange(n, dtype=float)
    w = np.exp(-(lag ** 2) / (bw * bw * 2))
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    sm = np.full(m, np.nan)
    if m >= n:
        sm[n - 1:] = np.convolve(cv, w, mode="full")[n - 1:m] / w.sum()    # sum of c[t - i] * w[i]
    s = pd.Series(sm, index=c.index)
    ma = s.rolling(int(p["lookback"])).mean()
    up = ((s > ma) & (s.shift(1) <= ma.shift(1))).to_numpy()
    dn = ((s < ma) & (s.shift(1) >= ma.shift(1))).to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    inpos = False
    for i in range(m):
        if up[i] and not inpos:
            le[i], inpos = True, True
        if dn[i] and inpos:
            se[i], inpos = True, False
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), false, pd.Series(se, index=c.index), false.copy()


def portfolio_kwargs(**params):
    return {}
