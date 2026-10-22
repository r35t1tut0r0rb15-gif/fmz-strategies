"""Choppiness-index regimes, 45-minute bars: in a trending market (CI under 38.2) EMA 9 / 21 crossings with RSI 14 under 70 (over 30) go long (short) and any bar without that signal closes; in a ranging market (CI over 61.8) RSI under 30 (over 70) goes long (short) and RSI over 40 (under 60) closes; reversing. The 2 % / 4 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #476242 "自适应多状态EMA-RSI动量策略结合波动指数过滤系统-Adaptive-Multi-State-EMA-RSI-Momentum-Strategy-with-Choppiness-Index-Filter-System" (CI, EMA, RSI).

FMZ source id: 476242

Source
    https://www.fmz.com/strategy/476242 (PineScript v6, FMZ last modified 2024-12-27 14:05:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-153), CI 14, RSI 14, EMA 9 / 21; CI levels 38.2 / 61.8; stop 2 %, target 4 % of the current close
    ci = 100 log10(sum(atr14, 14) / log10(max(high[14], high) - min(low[14], low))) / log10(14);  trending: crossover(ema9, ema21) and rsi < 70 -> entry Long, crossover(ema21, ema9) and rsi > 30 -> entry Short;  ranging: rsi < 30 -> Long, rsi > 70 -> Short
    trending and not bull -> close Long;  trending and not bear -> close Short;  ranging and rsi > 40 -> close Long;  ranging and rsi < 60 -> close Short;  every bar: exit(stop = close x (1 -/+ 2 %), limit = close x (1 +/- 4 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The CI is ported as written: the denominator is log10 of the two-bar range (the high and low 14
      bars back against the current bar's), not the range itself; a range or log that is not positive
      gives no CI (no regime) rather than an infinite value. A close acts only on the held position and
      leaves a same-bar reversal standing (as #441963). The bracket is re-sent on every bar from that
      bar's close, so its levels move after entry: stops() cannot express a level re-set every bar, so it
      is described here and kept pending (as #438034, mark trailing_stop_pending). REVERSAL INTENDED. No
      sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, choppiness regimes with EMA crossings or RSI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476242_choppiness_regime_ema_cross_rsi_extreme_reversal"
FAMILY = "regime_switch"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ci_length": [14, 21],
    "fast": [9, 5],
}
DEFAULT_PARAMS = {"ci_length": 14, "fast": 9, "slow": 21, "rsi_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _log10(x):
    x = x.where(x > 0)
    return np.log10(x)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ci_length"])
    rng = np.maximum(h.shift(n), h) - np.minimum(lo.shift(n), lo)
    hl = _log10(rng)
    s_atr = _atr(bars_df, n).rolling(n).sum()
    ci = 100 * (_log10(s_atr / hl) / np.log10(n))
    r = _rsi(c, int(p["rsi_length"]))
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    trend = ci < 38.2
    rang = ci > 61.8
    bull = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70)
    bear = (s > f) & (s.shift(1) <= f.shift(1)) & (r > 30)
    le = (trend & bull) | (~trend & rang & (r < 30))
    se = (trend & bear) | (~trend & rang & (r > 70))
    lx = ((trend & ~bull) | (rang & (r > 40))) & ~se
    sx = ((trend & ~bear) | (rang & (r < 60))) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
