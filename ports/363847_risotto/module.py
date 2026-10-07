"""RISOTTO: a CMO-adaptive average (VAR) of RSI(100) crossing above its own Optimized Trend
Tracker (OTT, two bars back) goes long; crossing below goes short (always in).
Port of FMZ strategy #363847 "RISOTTO".

Source
    https://www.fmz.com/strategy/363847 (PineScript v4, FMZ last modified 2022-05-17 17:08:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-110), RSI 100, VAR period 50, OTT period 2, 0.2 %
    OTT_Func(src, len, pct): VAR := nz(a |CMO9| src) + (1 - a |CMO9|) nz(VAR[1]), a = 2/(len+1)
        long/short stops VAR -+ VAR*pct%, ratcheted; dir flips; OTT = MT * (200 +- pct) / 200
    VRSI = VAR of rsi(close, 100) (len 50);  RISOTTO = OTT of VRSI + 1000 (len 2, 0.2 %)
    crossover(VRSI + 1000, RISOTTO[2]) -> entry long; else crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Everything is in RSI units (scale-free). The nz() seeds (VAR from 0) are kept.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363847_risotto_rsi_ott_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [50, 100],
    "var_len": [25, 50],
    "ott_pct": [0.1, 0.2, 0.4],
}
DEFAULT_PARAMS = {"rsi_len": 100, "var_len": 50, "ott_pct": 0.2}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _ott(src, length, percent):
    """Anıl Özekşi OTT on VAR (CMO(9)-adaptive EMA): returns (VAR, OTT) arrays; nz() as coded."""
    s = np.asarray(src, dtype=float)
    m = len(s)
    a = 2 / (length + 1)
    prev_s = np.concatenate([[np.nan], s[:-1]])
    ud = np.where(s > prev_s, s - prev_s, 0.0)
    dd = np.where(s < prev_s, prev_s - s, 0.0)
    sud = pd.Series(ud).rolling(9).sum().to_numpy()
    sdd = pd.Series(dd).rolling(9).sum().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        cmo = np.nan_to_num((sud - sdd) / (sud + sdd), nan=0.0, posinf=0.0, neginf=0.0)
    var, ott = np.zeros(m), np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    d = 1
    for i in range(m):
        k = a * abs(cmo[i])
        term = k * s[i]
        var[i] = (0.0 if np.isnan(term) else term) + (1 - k) * (var[i - 1] if i else 0.0)
        fark = var[i] * percent * 0.01
        ls, ss = var[i] - fark, var[i] + fark
        lsp = ls if np.isnan(ls_prev) else ls_prev
        ssp = ss if np.isnan(ss_prev) else ss_prev
        ls = max(ls, lsp) if var[i] > lsp else ls
        ss = min(ss, ssp) if var[i] < ssp else ss
        d = 1 if (d == -1 and var[i] > ssp) else (-1 if (d == 1 and var[i] < lsp) else d)
        mt = ls if d == 1 else ss
        ott[i] = mt * (200 + percent) / 200 if var[i] > mt else mt * (200 - percent) / 200
        ls_prev, ss_prev = ls, ss
    return var, ott


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["rsi_len"])).to_numpy()
    vrsi, _ = _ott(rsi, int(p["var_len"]), 1.0)
    x = vrsi + 1000
    _, ris = _ott(x, 2, float(p["ott_pct"]))
    r2 = np.concatenate([[np.nan] * 2, ris[:-2]])
    r3 = np.concatenate([[np.nan] * 3, ris[:-3]])
    x1 = np.concatenate([[np.nan], x[:-1]])
    up = (x > r2) & (x1 <= r3)
    dn = (x < r2) & (x1 >= r3)
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
