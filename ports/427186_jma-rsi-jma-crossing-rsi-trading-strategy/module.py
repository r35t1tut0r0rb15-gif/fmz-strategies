"""RSI crossing its own Jurik-style smoothing, long only as written: RSI(14) crossing above JMA(7,
phase 50, power 2) of the RSI goes long; RSI crossing back under it closes the long; a stop sits
at the entry price / 1.08.
Port of FMZ strategy #427186 "JMA Crossing RSI Trading Strategy".

FMZ source id: 427186

Source
    https://www.fmz.com/strategy/427186 (PineScript v4, FMZ last modified 2023-09-18 21:42:50).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 163-246), RSI 14, JMA length 7 phase 50 power 2, stop on
    jma of rsi: e0 = (1 - a) rsi + a e0[1]; e1 = (rsi - e0)(1 - b) + b e1[1];
                e2 = (e0 + pr e1 - jma[1])(1 - a)^2 + a^2 e2[1]; jma = e2 + jma[1]   (nz() of the [1] terms)
    crossover(rsi, jma) -> entry long; crossunder(rsi, jma) and close > long_price -> close long
    crossunder(rsi, jma) and close < short_price -> entry short; crossover -> close short
    exit(stop = position_avg_price / 1.08) for longs, x 1.08 for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * long_price and short_price are re-declared as 0.0 on every bar (not `var`) and set to the
      close only on the signal bar itself. So on a later cross-under bar long_price is 0 and the
      long always closes; the short entry needs close < short_price = that bar's close, which is
      never true: the script never shorts. Ported as it behaves: long only.
    * The stop is the entry price / 1.08, i.e. sl_stop = 1 - 1 / 1.08 of the fill price.
      Daily bars with a stop: mark coarse_bar_stop.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      The start / end date inputs are the author's backtest window (constant true): dropped.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is fixed at entry.
    2 generic: PASS, oscillator crosses, a stop as a fraction of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash qty 5000 stored in original_sizing.txt; the stop is ported via stops().
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427186_rsi_jma_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_length": [14, 9],
    "jma_length": [7, 14],
    "stop_factor": [1.08, 1.04],
}
DEFAULT_PARAMS = {"rsi_length": 14, "jma_length": 7, "phase": 50, "power": 2, "stop_factor": 1.08}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


def _jma(src, length, phase, power):
    pr = 0.5 if phase < -100 else 2.5 if phase > 100 else phase / 100 + 1.5
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    m = len(src)
    out = np.full(m, np.nan)
    e0p = e1p = e2p = jp = np.nan
    nz = (lambda v: 0.0 if np.isnan(v) else v)
    for i in range(m):
        x = src[i]
        e0 = (1 - alpha) * x + alpha * nz(e0p)
        e1 = (x - e0) * (1 - beta) + beta * nz(e1p)
        e2 = (e0 + pr * e1 - nz(jp)) * (1 - alpha) ** 2 + alpha ** 2 * nz(e2p)
        j = e2 + nz(jp)
        out[i] = j
        e0p, e1p, e2p, jp = e0, e1, e2, j
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    j = _jma(r, int(p["jma_length"]), float(p["phase"]), float(p["power"]))
    r1 = np.concatenate(([np.nan], r[:-1]))
    j1 = np.concatenate(([np.nan], j[:-1]))
    up = (r > j) & (r1 <= j1)
    dn = (r < j) & (r1 >= j1)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(up, index=idx), pd.Series(dn, index=idx), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": 1 - 1 / float(p["stop_factor"])}


def portfolio_kwargs(**params):
    return {}
