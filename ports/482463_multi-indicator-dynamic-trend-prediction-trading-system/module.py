"""RSI 14 below 30 with the raw stochastic below 20 goes long, RSI above 70 with the stochastic above 80 below a
fresh daily pivot high goes short; RSI or the stochastic back across 50 closes the trade, hourly bars.
Port of FMZ strategy #482463 "多指标动态趋势预测交易系统-Multi-Indicator-Dynamic-Trend-Prediction-Trading-System" (Intraday Leading Indicator Strategy).

FMZ source id: 482463

Source
    https://www.fmz.com/strategy/482463 (PineScript v5, FMZ last modified 2025-02-18 15:22:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-147), RSI 14 (70 / 30), stochastic 14 (80 / 20), daily pivots 3 / 3
    pivotHigh / pivotLow = request.security("D", ta.pivothigh(high, 3, 3) / ta.pivotlow(low, 3, 3))
    rsi < 30 and k < 20 and close > nz(pivotLow) -> entry long
    rsi > 70 and k > 80 and close < nz(pivotHigh) -> entry short
    rsi > 50 or k > 50 -> close long; rsi < 50 or k < 50 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily pivots are non-na only on the day a pivot is confirmed (3 days after it); house rule (#490787): the
      value of the last COMPLETED broker day (17:00 America/New_York) as of each hourly bar's close. On other days
      nz() makes them 0, so the long filter (close > 0) always passes and a short needs the close under a pivot high
      confirmed the previous day (as written). Pivots are strict on both sides (as #430850).
    * The closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the daily pivots without look-ahead.
    2 generic: PASS, RSI, a stochastic and confirmed pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily pivots; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482463_rsi_stoch_extremes_daily_pivot_filter"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "stoch_len": [14, 21],
}
DEFAULT_PARAMS = {"rsi_len": 14, "stoch_len": 14, "rsi_ob": 70.0, "rsi_os": 30.0, "st_ob": 80.0, "st_os": 20.0}
PIVOT = 3


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def precompute(raw_1m_df, symbol_key, **params):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    d = ohlc.groupby(broker_day(ohlc.index)).agg({"high": "max", "low": "min"}).dropna(how="all")
    dh, dl = d["high"].to_numpy(dtype=float), d["low"].to_numpy(dtype=float)
    ph = np.where(_pivots(dh, PIVOT, PIVOT, True), np.roll(dh, PIVOT), np.nan)
    pl = np.where(_pivots(dl, PIVOT, PIVOT, False), np.roll(dl, PIVOT), np.nan)
    end = (d.index + pd.Timedelta(hours=17)).tz_localize("America/New_York").tz_convert("UTC")
    daily = pd.DataFrame({"end": end, "piv_h": ph, "piv_l": pl}).sort_values("end")
    bar_end = pd.DataFrame({"end": bars.index + pd.Timedelta(FREQ)})
    got = pd.merge_asof(bar_end, daily, on="end", direction="backward")   # last broker day completed by the close
    bars["piv_h"] = got["piv_h"].to_numpy()
    bars["piv_l"] = got["piv_l"].to_numpy()
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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - ll) / (hh - ll)
    pl, ph = bars_df["piv_l"].fillna(0.0), bars_df["piv_h"].fillna(0.0)    # nz()
    buy = ((rsi < p["rsi_os"]) & (k < p["st_os"]) & (c > pl)).to_numpy()
    sell = ((rsi > p["rsi_ob"]) & (k > p["st_ob"]) & (c < ph)).to_numpy()
    xl = ((rsi > 50) | (k > 50)).to_numpy()
    xs = ((rsi < 50) | (k < 50)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and pos != -1:
            se[i], pos = True, -1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
