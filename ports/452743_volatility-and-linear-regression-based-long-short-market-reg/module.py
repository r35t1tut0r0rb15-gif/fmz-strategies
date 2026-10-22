"""Linear-regression 'slope' regimes beyond an ATR band, daily bars: with linreg(50, 1) - linreg(50, 0) over the threshold and the close over the regression end plus 2 ATR 14 it goes long; under minus the threshold with the close under the end minus 2 ATR it goes short; reversing.
Port of FMZ strategy #452743 "Volatility and Linear Regression based Long Short Market Regime Optimization Strategy" (Regime de Mercado com Regressão e Volatilidade Otimizado).

FMZ source id: 452743

Source
    https://www.fmz.com/strategy/452743 (PineScript v5, FMZ last modified 2024-05-28 17:40:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-146), linreg 50 (offsets 0 / 1); thresholds +- 1.0 (price units); ATR 14 x 2; EMA 10 / 50 confirmation
    slope = linreg(close, 50, 1) - linreg(close, 50, 0);  slope > 1.0 and close > linreg + 2 atr -> entry Buy;  slope < -1.0 and close < linreg - 2 atr -> entry Sell
    the same with ema10 > ema50 (< for shorts) -> entry Buy Confirmed / Sell Confirmed

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(.., 1) - linreg(.., 0) is minus the regression slope (the line's value one bar back minus
      its end), so the 'buy' regime is a FALLING regression line with the close over its end plus 2
      ATR; the port keeps it as written. The 1.0 thresholds are price amounts per bar, read against
      BTC near 42000 like other price units (#440456): the port tests the difference as a fraction
      of the close, 1 / 42000. The 'Confirmed' entries are a second same-side id and are refused
      while that side is held (pyramiding 1), so they add nothing. REVERSAL INTENDED. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit thresholds as fractions of 42000.
    2 generic: PASS, regression-difference regimes beyond an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452743_linreg_offset_difference_atr_band_reversal"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "atr_mult": [2.0, 1.0],
    "thr_frac": [2.38e-05, 0.001],
}
DEFAULT_PARAMS = {"length": 50, "atr_mult": 2.0, "thr_frac": 2.38e-05, "atr_len": 14}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _linreg_end(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(a.mean() + np.dot(w, a) / sxx * (n - 1) / 2.0), raw=True)


def _linreg_slope(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(np.dot(w, a) / sxx), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    end = _linreg_end(c, n)
    diff = -_linreg_slope(c, n)                # linreg(.., 1) - linreg(.., 0)
    vol = _atr(bars_df, p["atr_len"]) * float(p["atr_mult"])
    t = float(p["thr_frac"])
    le = (diff / c > t) & (c > end + vol)
    se = (diff / c < -t) & (c < end - vol)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
