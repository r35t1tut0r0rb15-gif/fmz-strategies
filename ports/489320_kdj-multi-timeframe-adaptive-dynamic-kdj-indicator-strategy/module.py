"""A weighted KDJ of the day's last 1-, 5- and 15-minute bars (lengths 3 / 14 / 15 by each frame's ATR / close), EMA 5 smoothed, broker days: a K / D cross up under a trend-dependent J level, or an anticipated cross, with the total under 22 goes long; the mirror over 78 goes short; reversing (the per-bar stop from the open is pending).
Port of FMZ strategy #489320 "多重时间框架自适应动态KDJ指标策略-Multi-Timeframe-Adaptive-Dynamic-KDJ-Indicator-Strategy" (Adaptive KDJ (MTF)).

FMZ source id: 489320

Source
    https://www.fmz.com/strategy/489320 (PineScript v5, FMZ last modified 2025-04-03 15:13:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-231), frames "1" / "5" / "15"; method 1 (volatility lengths); weights 0.5 / 0.33 / 0.17; EMA 5; trend 40; TSL ATR 12 x 2.5 (no offset); stop open x (1 -/+ 0.28 %)
    per frame: length = vol > 0.03 ? 3 : vol > 0.002 ? 14 : 15;  rsv over that length of the frame's high / low / close (as daily series), k = sma(rsv, 3), d = sma(k, 3), j = 3k - 2d
    smoothed weighted K / D / J / total;  buy: J < level and crossover(K, D), or K rising with D falling within 5;  total < 22 -> entry Long;  mirror with total > 78 -> entry Short
    every bar: exit(trail_points = atr x 2.5 / mintick, stop = open x 0.9972) for Long;  mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "1", "5" and "15" are lower time frames requested without lookahead: each daily bar gets its last
      1-, 5- and 15-minute bar's high, low, close and ATR 14 / close (as #436765), built from minutes in
      precompute; the KDJ windows then run over those daily values with the per-bar length, as written. The
      stop is re-sent every bar from that bar's open (and the trail has no offset): not ported, mark
      trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. An entry on the
      other side reverses (REVERSAL INTENDED). MPL 2.0 source (the notice is kept: Mozilla Public License
      2.0, © Lausekopf). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent stop pending.
    2 generic: PASS, multi-frame adaptive KDJ crossings and anticipations.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); lower frames from its minutes.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489320_mtf_adaptive_kdj_cross_anticipate_extreme_reversal"
FAMILY = "stochastic"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smoothingLength": [5, 10],
    "trendLength": [40, 20],
}
DEFAULT_PARAMS = {"smoothingLength": 5, "trendLength": 40}

FRAMES = [(1, 0.5), (5, 0.33), (15, 0.17)]


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    for tf, _ in FRAMES:
        q = df.resample(f"{tf}min", label="left", closed="left").agg(
            {"high": "max", "low": "min", "close": "last"}).dropna(how="all")
        pc = q["close"].shift(1)
        tr = pd.concat([q["high"] - q["low"], (q["high"] - pc).abs(), (q["low"] - pc).abs()],
                       axis=1).max(axis=1, skipna=False)
        tr.iloc[0] = q["high"].iloc[0] - q["low"].iloc[0]
        t = pd.DataFrame({"k": broker_day(q.index), "h": q["high"].to_numpy(), "l": q["low"].to_numpy(),
                          "c": q["close"].to_numpy(), "v": (_rma(tr, 14) / q["close"]).to_numpy()})
        last = t.groupby("k").tail(1).set_index("k")           # each day's last lower-frame bar
        for col in ("h", "l", "c", "v"):
            bars[f"{col}{tf}"] = last[col].reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _kdj(hv, lv, cv, vol):
    m = len(cv)
    ln = np.where(vol > 0.03, 3, np.where(vol > 0.002, 14, 15))      # na compares false: 15
    rsv = np.full(m, np.nan)
    for i in range(m):
        n = int(ln[i])
        if i >= n - 1:
            hi, lo_ = np.max(hv[i - n + 1:i + 1]), np.min(lv[i - n + 1:i + 1])
            if hi > lo_:
                rsv[i] = 100 * (cv[i] - lo_) / (hi - lo_)
    k = pd.Series(rsv).rolling(3).mean()
    d = k.rolling(3).mean()
    return k.to_numpy(), d.to_numpy(), (3 * k - 2 * d).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    ak = ad = aj = 0.0
    for tf, w in FRAMES:
        k, d, j = _kdj(*(bars_df[f"{col}{tf}"].to_numpy(dtype=float) for col in ("h", "l", "c", "v")))
        ak, ad, aj = ak + k * w, ad + d * w, aj + j * w
    ak, ad, aj = (pd.Series(x, index=idx) for x in (ak, ad, aj))
    n = int(p["smoothingLength"])

    def ema(x):
        return x.ewm(span=n, adjust=False).mean()

    sk, sd, sj, st = ema(ak), ema(ad), ema(aj), ema((ak + ad + aj) / 3)
    ta_ = st.rolling(int(p["trendLength"])).mean()
    upt, dnt = ta_ > 60, ta_ < 40
    buy_lv = pd.Series(np.where(upt, 40, np.where(dnt, 15, 25)), index=idx)
    sell_lv = pd.Series(np.where(upt, 85, np.where(dnt, 60, 75)), index=idx)
    buy = (sj < buy_lv) & (sk > sd) & (sk.shift(1) <= sd.shift(1))
    sell = (sj > sell_lv) & (sk < sd) & (sk.shift(1) >= sd.shift(1))
    near = (sk - sd).abs() < 5
    ant_b = (sk.diff() > 0) & (sd.diff() < 0) & near
    ant_s = (sk.diff() < 0) & (sd.diff() > 0) & near
    le = (buy | ant_b) & (st < 22)
    se = (sell | ant_s) & (st > 78)
    false = pd.Series(False, index=idx)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
