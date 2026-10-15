"""RSI-CCI fusion, long only by default: the z-scores of RSI(14) and CCI(14) are blended 50 / 50 and
rescaled; the blend crossing above its own lower band (SMA -1 stdev, 14 bars) goes long, crossing
under its upper band closes the long.
Port of FMZ strategy #427272 "RSI-CCI Fusion Strategy".

FMZ source id: 427272

Source
    https://www.fmz.com/strategy/427272 (PineScript v5, FMZ last modified 2023-09-19 16:42:18).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 158-208), length 14, RSI weight 0.5, shorts off
    rsi_z = (rsi - sma(rsi, 14)) / stdev(rsi, 14); cci_z likewise; z = 0.5 rsi_z + 0.5 cci_z
    rescaled = z x stdev(z, 14) + sma(z, 14)
    upper / lower = sma(rescaled, 14) +- stdev(rescaled, 14)
    crossover(rescaled, lower) -> entry long; crossunder(rescaled, upper) -> close long
    (with shorts on: crossunder -> entry short, crossover -> close short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (pyramiding 0, bar-close orders).
    * ta.cci = (src - sma) / (0.015 x mean absolute deviation from the sma), over 14 bars;
      ta.stdev is the population standard deviation; all windows include the current bar
      (rolling statistics ending at the bar, no whole-series figure).
    * Shorts are off by default: long only; the grid also tries shorts on (`enable_short`), in
      which case entries reverse (REVERSAL INTENDED).
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling z-scores of oscillators (dimensionless).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (strategy() commented out).
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only by default; REVERSAL INTENDED with shorts on.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427272_rsi_cci_fusion"
FAMILY = "zscore_reversion"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "rsi_weight": [0.5, 0.8],
    "enable_short": [False, True],
}
DEFAULT_PARAMS = {"length": 14, "rsi_weight": 0.5, "enable_short": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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
    return pd.Series(val, index=close.index)


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda w: np.mean(np.abs(w - w.mean())), raw=True)
    return (src - ma) / (0.015 * dev)


def _z(x, n):
    return (x - x.rolling(n).mean()) / x.rolling(n).std(ddof=0)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    w = float(p["rsi_weight"])
    c = bars_df["close"]
    z = w * _z(_rsi(c, n), n) + (1 - w) * _z(_cci(c, n), n)
    rs = z * z.rolling(n).std(ddof=0) + z.rolling(n).mean()
    mid, sd = rs.rolling(n).mean(), rs.rolling(n).std(ddof=0)
    upper, lower = mid + sd, mid - sd
    buy = ((rs > lower) & (rs.shift(1) <= lower.shift(1))).to_numpy()
    sell = ((rs < upper) & (rs.shift(1) >= upper.shift(1))).to_numpy()
    shorts = bool(p["enable_short"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i] and pos != 1:
            pos = 1
        elif sell[i] and shorts and pos != -1:
            pos = -1
        elif sell[i] and pos == 1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
