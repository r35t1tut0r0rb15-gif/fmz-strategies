"""FTL range filter: price (hl2) on the right side of a slow ohlc4 range filter that is trending,
after the opposite state, filtered by the Ultimate Oscillator and EMA 144, enters long or short
(always in).
Port of FMZ strategy #362887 "FTL - Range Filter X2 + EMA + UO".

Source
    https://www.fmz.com/strategy/362887 (PineScript v5, FMZ last modified 2022-05-13 16:11:48).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 99-384), trigger filter ohlc4 / 48 / 3.4, EMA 144,
UO 7/14/28 (overbought 60, oversold 40)
    smrng = ema(ema(|x - x[1]|, t), 2t - 1) * m;  filt2 = range filter of ohlc4 by smrng
    upward2 / downward2 = bars the filter has risen / fallen (reset on the opposite move)
    longCond  = hl2 > filt2 and hl2 != hl2[1] and upward2 > 0;  shortCond mirrors
    CondIni := longCond ? 1 : shortCond ? -1 : CondIni[1]
    long  = longCond and CondIni[1] == -1 and UO <= 60 and close > EMA144
    short = shortCond and CondIni[1] == 1 and UO >= 40 and close < EMA144
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions compare the LEADING filter's source (hl2) with the trigger filter, as coded.
      The leading filter itself, the EMA crosses and pullback markers only draw: not ported.
    * The range multipliers scale an average of the bar-to-bar move (scale-free).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362887_range_filter_uo_ema"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per2": [30, 48],
    "mult2": [2.6, 3.4],
    "ema_len": [100, 144],
}
DEFAULT_PARAMS = {"per2": 48, "mult2": 3.4, "ema_len": 144, "uo_ob": 60.0, "uo_os": 40.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smoothrng(x, t, m):
    avrng = (x - x.shift(1)).abs().ewm(span=t, adjust=False).mean()
    return avrng.ewm(span=t * 2 - 1, adjust=False).mean() * m


def _rngfilt(x, r):
    """Range filter: follows x only when it moves more than r away; nz(prev) = 0 at the start."""
    xv, rv = x.to_numpy(dtype=float), r.to_numpy(dtype=float)
    out = np.full(len(xv), np.nan)
    for i in range(len(xv)):
        prev = out[i - 1] if i and not np.isnan(out[i - 1]) else 0.0
        if xv[i] > prev:
            out[i] = prev if xv[i] - rv[i] < prev else xv[i] - rv[i]
        else:
            out[i] = prev if xv[i] + rv[i] > prev else xv[i] + rv[i]
    return pd.Series(out, index=x.index)


def _up_down_counts(f):
    fv = f.to_numpy(dtype=float)
    up, dn = np.zeros(len(fv)), np.zeros(len(fv))
    for i in range(1, len(fv)):
        if fv[i] > fv[i - 1]:
            up[i], dn[i] = up[i - 1] + 1, 0
        elif fv[i] < fv[i - 1]:
            up[i], dn[i] = 0, dn[i - 1] + 1
        else:
            up[i], dn[i] = up[i - 1], dn[i - 1]
    return up, dn


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


def _uo(bars, lens=(7, 14, 28)):
    c, pc = bars["close"], bars["close"].shift(1)
    hi, lo = np.maximum(bars["high"], pc), np.minimum(bars["low"], pc)
    bp, tr = c - lo, hi - lo
    a = [bp.rolling(n).sum() / tr.rolling(n).sum() for n in lens]
    return 100 * (4 * a[0] + 2 * a[1] + a[2]) / 7


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (h + l) / 2
    src2 = (o + h + l + c) / 4
    filt2 = _rngfilt(src2, _smoothrng(src2, int(p["per2"]), float(p["mult2"])))
    up2, dn2 = _up_down_counts(filt2)
    moved = (src != src.shift(1)).to_numpy()
    long_c = (src > filt2).to_numpy() & moved & (up2 > 0)
    short_c = (src < filt2).to_numpy() & moved & (dn2 > 0)
    m = len(c)
    ini = np.zeros(m)
    for i in range(m):
        ini[i] = 1.0 if long_c[i] else (-1.0 if short_c[i] else (ini[i - 1] if i else 0.0))
    ini1 = np.concatenate([[0.0], ini[:-1]])
    uo = _uo(bars_df)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_ = long_c & (ini1 == -1) & ~(uo > p["uo_ob"]).to_numpy() & (c > ema).to_numpy()
    short = short_c & (ini1 == 1) & ~(uo < p["uo_os"]).to_numpy() & (c < ema).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
