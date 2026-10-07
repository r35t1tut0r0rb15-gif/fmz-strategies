"""Jurik MA ATR envelope reversion: long when hlc3 crosses up through the lower envelope,
short when it crosses down through the upper envelope (always in).
Port of FMZ strategy #361794 "baguette-by-multigrain".

Source
    https://www.fmz.com/strategy/361794 (PineScript v5, FMZ last modified 2022-05-09 00:17:31).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-166), JMA hlc3 144 phase 34, ATR 34 x 3
    j = f_jma(hlc3, 144, 34)       (adaptive Jurik MA, @gorx1 version)
    env: j +/- 3*ATR(34), the ATR held while j is unchanged
    crossover(hlc3, j_low) -> entry long;  else crossunder(hlc3, j_up) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_jma is reproduced line by line, including its na handling (nz only where written).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * The envelope is ATR-based: criterion 2 PASS.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361794_jma_atr_envelope_reversion"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "jma_len": [89, 144, 233],
    "atr_mul": [2.0, 3.0, 4.0],
}
DEFAULT_PARAMS = {"jma_len": 144, "jma_phase": 34, "atr_len": 34, "atr_mul": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _jma(src, length, phase):
    s = src.to_numpy(dtype=float)
    m = len(s)
    ln = 0.5 * (length - 1)
    len1 = max(np.log(np.sqrt(ln)) / np.log(2) + 2, 0)
    pow1 = max(len1 - 2, 0.5)
    len2 = np.sqrt(ln) * len1
    bet = len2 / (len2 + 1)
    beta = 0.45 * (ln - 1) / (0.45 * (ln - 1) + 2)
    pr = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    nz = lambda v: 0.0 if np.isnan(v) else v
    lower = np.full(m, np.nan)
    upper = np.full(m, np.nan)
    vola = np.full(m, np.nan)
    vsum = np.full(m, np.nan)
    avg = np.full(m, np.nan)
    ma1 = det0 = det1 = jma_prev = 0.0
    out = np.full(m, np.nan)
    for t in range(m):
        y = t + 1
        lb = lower[t - 1] if t else np.nan
        ub = upper[t - 1] if t else np.nan
        del2, del1 = abs(s[t] - lb), abs(s[t] - ub)
        vola[t] = 0.0 if del1 == del2 else (np.nan if np.isnan(del1) or np.isnan(del2) else max(del1, del2))
        v10 = vola[t - 10] if t >= 10 else np.nan
        vsum[t] = nz(vsum[t - 1] if t else np.nan) + 0.1 * (vola[t] - v10)
        if y <= 66:
            pa = nz(avg[t - 1] if t else np.nan)
            avg[t] = pa + 2.0 * (vsum[t] - pa) / 66
        else:
            w = vsum[t - 64:t + 1]
            avg[t] = np.nan if np.isnan(w).any() else w.mean()
        r = vola[t] / avg[t] if avg[t] > 0 else 0.0
        cap = len1 ** (1 / pow1)
        r = cap if r > cap else (1.0 if (r < 1 or np.isnan(r)) else r)
        pow2 = r ** pow1
        kv = bet ** np.sqrt(pow2)
        lower[t] = s[t] if y == 1 else (s[t] if del2 < 0 else s[t] - kv * del2)
        upper[t] = s[t] if y == 1 else (s[t] if del1 < 0 else s[t] + kv * del1)
        alpha = beta ** pow2
        ma1 = (1 - alpha) * s[t] + alpha * ma1
        det0 = (s[t] - ma1) * (1 - beta) + beta * det0
        ma2 = ma1 + pr * det0
        det1 = (ma2 - jma_prev) * (1 - alpha) ** 2 + alpha ** 2 * det1
        jma_prev = out[t] = jma_prev + det1
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hlc3 = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    j = _jma(hlc3, int(p["jma_len"]), p["jma_phase"])
    atr = (p["atr_mul"] * _atr_pine(bars_df, int(p["atr_len"]))).to_numpy()
    changed = (j.diff() != 0).to_numpy()
    held = np.full(len(atr), np.nan)
    for i in range(len(atr)):
        held[i] = atr[i] if (changed[i] or i == 0) else held[i - 1]
    jv = j.to_numpy()
    up_env, lo_env = jv + held, jv - held
    x = hlc3.to_numpy()
    x1, lo1, up1 = np.roll(x, 1), np.roll(lo_env, 1), np.roll(up_env, 1)
    warm = np.arange(len(x)) >= int(p["jma_len"])
    long_sig = warm & (x > lo_env) & (x1 <= lo1)
    short_sig = warm & (x < up_env) & (x1 >= up1)
    return _always_in(long_sig, short_sig, bars_df.index)


def portfolio_kwargs(**params):
    return {}
