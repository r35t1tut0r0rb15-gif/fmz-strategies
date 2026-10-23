"""The trend module of a multi-factor script, hourly bars, long only: in a strong ADX 10 trend (both bars at or above 30 and rising past its last three values) with a unanimous 10-14 bar trend score, SMA 8 above SMA 21 with the close above SMA 8 and a bullish previous bar goes long; the mirror bearish set closes, with a 2 % stop from the entry.
Port of FMZ strategy #430677 "Multi factor Strategy" (Strategy_1 (Multi-factor)).

FMZ source id: 430677

Source
    https://www.fmz.com/strategy/430677 (PineScript v4, FMZ last modified 2023-10-31 15:45:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 248-429), trend strategy on (oscillating / breakout off); Long; SMA 8 / 21; ADX 10, 30; trend score 10-14; stop 2 %; strategy() commented out
    intTrend = ADX >= 30 and ADX[1] >= 30 and ADX > highest(ADX[1], 3) ? (score > 4 ? 1 : score < -4 ? -1 : 0) : 0
    intTrend != 0 and sma(8) > sma(21) and close > sma(8) and close[1] > hl2[1] and open[1] < hl2[1] -> entry Lng TD;  exit(stop = avg x 0.98);  mirror set -> close Lng TD

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long entry needs a trend in EITHER direction (intTrend not 0), as written. The trend score adds +1
      / -1 for close >= nz(close[i]) over i = 10..14 (nz = 0 at the start). Only the trend module is on, so
      the breakout module's volume test never runs: ported as not using volume (check 8). The 2 % stop is a
      scalar fraction of the fill. The take-profit input is not used by the trend module. Long only. Stop
      module: portfolio_kwargs {} (driver D4). strategy() is commented out. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop from the fill.
    2 generic: PASS, ADX-gated SMA trend entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (20 % of equity, pyramiding 12) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 2017 .. 9999 window dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430677_adx_trend_score_sma8_21_pct2_stop_long"
FAMILY = "adx_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_trend": [30, 20],
    "stop_loss": [0.02, 0.04],
}
DEFAULT_PARAMS = {"adx_trend": 30, "stop_loss": 0.02, "fast_ma": 8, "slow_ma": 21, "adx_len": 10,
                  "ts_from": 10, "ts_to": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["adx_len"])
    up, dn = h.diff(), -lo.diff()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(up.where((up > dn) & (up > 0), 0.0), n) / trr)
    minus = _fixnan(100 * _rma(dn.where((dn > up) & (dn > 0), 0.0), n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    f, t = int(p["ts_from"]), int(p["ts_to"])
    score = sum(np.where(c >= c.shift(i).fillna(0.0), 1, -1) for i in range(f, t + 1))
    tdir = np.where(score > (t - f), 1, np.where(score < (f - t), -1, 0))
    lim = float(p["adx_trend"])
    grow = adx > adx.shift(1).rolling(3).max()
    strong = ((adx >= lim) & (adx.shift(1) >= lim) & grow).to_numpy()
    itrend = np.where(strong, tdir, 0)
    fm, sm = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    hl2_1 = ((h + lo) / 2).shift(1)
    f1 = (c.shift(1) > hl2_1) & (o.shift(1) < hl2_1)
    f3 = (c.shift(1) < hl2_1) & (o.shift(1) > hl2_1)
    le = pd.Series(itrend != 0, index=c.index) & (fm > sm) & (c > fm) & f1
    lx = (fm < sm) & (c < fm) & f3
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"])}


def portfolio_kwargs(**params):
    return {}
