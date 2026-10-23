"""Broker days: a "KNN" average (the mean of the 3 past values of the SMA 5 of hl2, out of the last 30, closest to the RMA 5 of the close), smoothed by a WMA 5, turning up goes long and turning down goes short; reversing.
Port of FMZ strategy #451532 "KNN-机器学习策略基于-K-近邻算法的趋势预测交易系统-KNN-Machine-Learning-Strategy-Trend-Prediction-Trading-System-Based-on-K-Nearest-Neighbors-Algorithm" (money printer part 1 (KNN moving average, Blake_22)).

FMZ source id: 451532

Source
    https://www.fmz.com/strategy/451532 (PineScript v5, FMZ last modified 2024-05-15 17:09:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 97-255), PriceValue hl2 / 5; TargetValue Price Action (RMA 5); 3 closest of 30; smoothing 50 (plots only)
    knnMA = meanOfKClosest(sma(hl2, 5), rma(close, 5));  knnMA_ = wma(knnMA, 5);  LongCondtion = knnMA_[1] < knnMA_ and knnMA_[1] <= knnMA_[2];  ShortCondtion = knnMA_[1] > knnMA_ and knnMA_[1] >= knnMA_[2]
    entry Long when LongCondtion, close Long when ShortCondtion;  entry Short when ShortCondtion, close "short" when LongCondtion (wrong id)

Interpretation choices (Pine rules in SURVEY_README.md)
    * meanOfKClosest keeps three slots (seeded with distance 1e10, value 0) and replaces the first
      largest distance whenever a past value is closer, then averages the three slots, as written. The
      KNN classifier, its prediction and the colours only plot. The short close names "short" (the entry
      is "Short"), so it never acts; the long close fires with the short entry and acts only on a
      position the entry leaves unchanged: every turn reverses. Volume is not used (the VWAP options are
      not selected). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, turns of a nearest-neighbour smoothed average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_451532_knn_closest_values_average_turns_reversal"
FAMILY = "machine_learning_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_closest": [3, 5],
    "ma_len": [5, 10],
}
DEFAULT_PARAMS = {"k_closest": 3, "ma_len": 5, "target_len": 5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _knn_mean(val, tgt, k, window):
    vv, tv = val.to_numpy(dtype=float), tgt.to_numpy(dtype=float)
    m = len(vv)
    out = np.full(m, np.nan)
    for t in range(m):
        dist = np.full(k, 1e10)
        vals = np.zeros(k)
        for i in range(1, window + 1):
            if t - i < 0:
                continue                                 # value_[i] is na before the data: no update
            x = vv[t - i]
            d = abs(tv[t] - x)
            j_max = 0
            for j in range(1, k):
                if dist[j] > dist[j_max]:
                    j_max = j
            if d < dist[j_max]:
                dist[j_max], vals[j_max] = d, x
        out[t] = vals.sum() / k
    return pd.Series(out, index=val.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["k_closest"])
    val = ((h + lo) / 2).rolling(int(p["ma_len"])).mean()
    tgt = _rma(c, int(p["target_len"]))
    knn = _wma(_knn_mean(val, tgt, k, max(k, 30)), 5)
    k1, k2 = knn.shift(1), knn.shift(2)
    up = ((k1 < knn) & (k1 <= k2)).to_numpy()
    dn = ((k1 > knn) & (k1 >= k2)).to_numpy()
    m = len(up)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if up[i] and pos != 1:
            le[i], pos = True, 1
        elif dn[i] and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
