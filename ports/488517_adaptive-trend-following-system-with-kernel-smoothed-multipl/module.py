"""Five kernel-weighted moving averages (beta 20, Gaussian 100, Epanechnikov 150, beta 200, Gaussian 250), broker days: three or more ordered pairs rising (falling) with RSI 7 under 40 (over 60) and the RSI 7 of the first average at or over (under) 0.5 x 100, held for 4 bars in a row, goes long (short); reversing (the close-based trailing stops are pending).
Port of FMZ strategy #488517 "Adaptive Trend Following System with Kernel Smoothed Multiple Moving Averages" (B4100 - NW Trend Ribbon Strategy).

FMZ source id: 488517

Source
    https://www.fmz.com/strategy/488517 (PineScript v5, FMZ last modified 2025-03-28 15:13:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-545), kernels Beta 20 / Gaussian 100 / Epanechnikov 150 / Beta 200 / Gaussian 250 (alpha = beta = 3, bandwidth 0.3); crossings 3; RSI 7 / 40 / 60; strength RSI 7 of MA1, 0.5; confirmation 4; trail 2 % / 1 %; ATR(1) trail x 200; commission 0.02 %
    ma_k = sum(src[i] x kernel_k[i], i = 0 .. len-1);  count of ma_k > ma_k+1 (k = 1..4) >= 3 and rsi7 < 40 and rsi(ma1, 7) / 100 >= 0.5 -> long count += 1, short count := 0, else long count := 0;  mirror
    long count >= 4 -> entry Long;  short count >= 4 -> entry Short
    held: close-based ratchet trail (2 % activation, 1 % offset; close - 200 x ATR(1)) re-sent every bar as the stop

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each kernel weights the current bar first (index 0), as written; the weights are normalised to sum
      1. The confirmation counters are followed in a loop, as written (a short-condition bar also resets
      the long count). The entries are states and repeat while held. The stop is a ratchet of bar closes
      (1 % under the best close once the close is 2 % over the entry, and 200 x ATR(1) under the close),
      re-sent each bar: the house trail on minute closes cannot express it, so it is not ported, mark
      trailing_stop_pending (as #440449); the opposite entry is the exit. The ATR take-profit and hard
      stop are off. An entry on the other side reverses (REVERSAL INTENDED). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-ratchet trail pending.
    2 generic: PASS, kernel-MA ribbon order with RSI and trend-strength filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity and commission 0.02 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_488517_kernel_ma_ribbon_order_rsi7_strength_confirm4_reversal"
FAMILY = "ma_ribbon"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "maCrossoversRequired": [3, 4],
    "trendConfirmationPeriod": [4, 2],
}
DEFAULT_PARAMS = {"maCrossoversRequired": 3, "trendConfirmationPeriod": 4, "rsiLength": 7, "rsiOverbought": 60,
                  "rsiOversold": 40, "trendStrengthLength": 7, "minTrendStrength": 0.5, "maxTrendStrength": 0.5}

KERNELS = [("beta", 20), ("gauss", 100), ("epan", 150), ("beta", 200), ("gauss", 250)]


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


def _kernel(kind, n, alpha=3.0, beta=3.0, bw=0.3):
    x = np.arange(n) / (n - 1)
    if kind == "beta":
        w = x ** (alpha - 1) * (1 - x) ** (beta - 1)
    elif kind == "gauss":
        w = np.exp(-0.5 * ((x - 0.5) / bw) ** 2)
    else:
        w = np.maximum(0.0, 1 - ((x - 0.5) / bw) ** 2)
    return w / w.sum()


def _kernel_ma(c, kind, n):
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        k = _kernel(kind, n)
        out[n - 1:] = sliding_window_view(v, n) @ k[::-1]   # kernel[0] weights the current bar
    return pd.Series(out, index=c.index)


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mas = [_kernel_ma(c, k, n) for k, n in KERNELS]
    nl = sum((mas[i] > mas[i + 1]).astype(int) for i in range(4))
    ns = sum((mas[i] < mas[i + 1]).astype(int) for i in range(4))
    req = int(p["maCrossoversRequired"])
    r = _rsi(c, int(p["rsiLength"]))
    ts = _rsi(mas[0], int(p["trendStrengthLength"])) / 100
    lc = ((nl >= req) & (r < float(p["rsiOversold"])) & (ts >= float(p["minTrendStrength"]))).to_numpy()
    sc = ((ns >= req) & (r > float(p["rsiOverbought"])) & (ts <= float(p["maxTrendStrength"]))).to_numpy()
    k = int(p["trendConfirmationPeriod"])
    m = len(lc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lcnt = scnt = 0
    for i in range(m):
        if lc[i]:
            lcnt, scnt = lcnt + 1, 0
        else:
            lcnt = 0
        if sc[i]:
            scnt, lcnt = scnt + 1, 0
        else:
            scnt = 0
        le[i], se[i] = lcnt >= k, scnt >= k
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), false, pd.Series(se, index=c.index), false.copy()


def portfolio_kwargs(**params):
    return {}
