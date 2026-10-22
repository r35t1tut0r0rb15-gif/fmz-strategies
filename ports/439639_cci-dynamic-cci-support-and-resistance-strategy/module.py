"""CCI-pivot support and resistance in the EMA 50 / 100 trend, 1-hour bars: in an uptrend, a green bar closing above the support (the last CCI 50 pivot low mapped back to price) after a 2-bar low under it
goes long; the mirror goes short; each trade has an ATR bracket (1.1 / 2.2 x the larger of ATR 100 and the previous day's largest ATR 100); reversing.
Port of FMZ strategy #439639 "动态CCI支撑阻力策略Dynamic-CCI-Support-and-Resistance-Strategy" (CCI based support and resistance strategy).

FMZ source id: 439639

Source
    https://www.fmz.com/strategy/439639 (PineScript v5, FMZ last modified 2024-01-22 16:37:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-229), CCI 50 of hlc3; pivots 50 / 50; buffer 10; trend matters, type cross (EMA 50 / 100); ksl 1.1, ktp 2.2; max-ATR period D
    uppercci = fixnan(pivothigh(cci, 50, 50)) - 10;  lowercci = fixnan(pivotlow(cci, 50, 50)) + 10;  res / sup = that x 0.015 dev(hlc3, 50) + sma(hlc3, 50)
    buy = trend up and lowest(2) < sup and close > open and close > sup;  sell mirror;  atr1 = max(previous day's largest atr(100), atr(100));  levels close -/+ 1.1 / 2.2 atr1 fixed once in the position

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are strict on both sides and known 50 bars after the pivot (#434470); fixnan holds the last
      one. The daily close from security("D") changes on the first bar of a day, so act_atr is the
      largest ATR(100) of the previous broker day (from the module's own bars). The bracket levels are
      set from the signal bar's close and frozen once in the position: sl_stop = 1.1 x atr1 / close and
      tp_stop = 2.2 x atr1 / close of the signal bar, shifted one bar inside stops() and re-based on the
      fill. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, CCI pivots mapped to price, EMA trend and ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily ATR maximum (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439639_cci_pivot_support_resistance_atr_bracket"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ksl": [1.1, 2.0],
    "ktp": [2.2, 4.0],
}
DEFAULT_PARAMS = {"ksl": 1.1, "ktp": 2.2, "cci_length": 50, "left": 50, "right": 50, "buffer": 10.0,
                  "fast_ma": 50, "slow_ma": 100, "atr_len": 100}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _pivot(x, left, right, low):
    """True at bar i when bar i - right is a strict pivot (both sides), known at bar i."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for i in range(left + right, m):
        p = i - right
        v = x[p]
        if np.isnan(v):
            continue
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if np.isnan(w).any():
            continue
        out[i] = (v < w).all() if low else (v > w).all()
    return out


def _held(x, flags, lag):
    """fixnan of the pivot value: the value lag bars back on each flagged bar, held until the next."""
    m = len(x)
    out = np.full(m, np.nan)
    cur = np.nan
    for i in range(m):
        if flags[i]:
            cur = x[i - lag]
        out[i] = cur
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (h + lo + c) / 3
    n = int(p["cci_length"])
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = ((src - ma) / (0.015 * dev)).to_numpy()
    L, R = int(p["left"]), int(p["right"])
    up_c = _held(cci, _pivot(cci, L, R, False), R) - float(p["buffer"])
    lo_c = _held(cci, _pivot(cci, L, R, True), R) + float(p["buffer"])
    scale, base = (0.015 * dev).to_numpy(), ma.to_numpy()
    res, sup = up_c * scale + base, lo_c * scale + base
    ef = c.ewm(span=int(p["fast_ma"]), adjust=False).mean().to_numpy()
    es = c.ewm(span=int(p["slow_ma"]), adjust=False).mean().to_numpy()
    m = len(c)
    t = np.zeros(m)
    q = 0
    for i in range(m):
        if ef[i] > es[i]:
            q = 1
        elif ef[i] < es[i]:
            q = -1
        t[i] = q
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    ll2, hh2 = lo.rolling(2).min().to_numpy(), h.rolling(2).max().to_numpy()
    buy = (t == 1) & (ll2 < sup) & (cv > ov) & (cv > sup)
    sell = (t == -1) & (hh2 > res) & (cv < ov) & (cv < res)
    atr = _atr(bars_df, p["atr_len"])
    day = broker_day(bars_df.index)
    dmax = atr.groupby(day).max().shift(1).reindex(day).to_numpy()
    av = atr.to_numpy()
    atr1 = np.where(np.isnan(dmax), av, np.fmax(dmax, av))
    return buy, sell, atr1 / cv


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell & ~buy, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, a = _setup(bars_df, p)
    ix = bars_df.index
    a = pd.Series(a, index=ix)
    return {"sl_stop": (float(p["ksl"]) * a).shift(1), "tp_stop": (float(p["ktp"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
