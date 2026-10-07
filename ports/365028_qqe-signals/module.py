"""QQE signals: the smoothed RSI moving above its QQE trailing line goes long on the first bar
above; moving below goes short on the first bar below (always in).
Port of FMZ strategy #365028 "QQE signals".

Source
    https://www.fmz.com/strategy/365028 (PineScript v4, FMZ last modified 2022-05-23 11:32:09).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 46-101), RSI 10, smoothing 5, QQE factor 4.238
    RsiMa = ema(rsi(close, 10), 5); dar = ema(ema(|RsiMa[1] - RsiMa|, 19), 19) * 4.238
    longband / shortband ratchet around RsiMa (lines 68-69)
    trend := cross(RsiMa, shortband[1]) ? 1 : cross(longband[1], RsiMa) ? -1 : trend[1] (1 at start)
    TL = trend == 1 ? longband : shortband
    QQExlong counts bars with TL < RsiMa; qqeLong = QQExlong == 1 (and TL[1] - 50 != 0)
    qqeLong -> entry long; else qqeShort -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is either direction (a crossover or a crossunder), as in Pine v4.
    * "Thresh-hold" is declared but unused.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365028_qqe_line_side_change"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [10, 14],
    "sf": [5, 8],
    "qqe": [3.0, 4.238],
}
DEFAULT_PARAMS = {"rsi_len": 10, "sf": 5, "qqe": 4.238}


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
    n = int(p["rsi_len"])
    wp = n * 2 - 1
    rma = _rsi(bars_df["close"], n).ewm(span=int(p["sf"]), adjust=False).mean()
    dar = ((rma.shift(1) - rma).abs().ewm(span=wp, adjust=False).mean()
           .ewm(span=wp, adjust=False).mean() * p["qqe"]).to_numpy()
    r = rma.to_numpy()
    m = len(r)
    lb, sb, tl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    trend = 1.0
    xl = xs = 0

    def cross(a, a1, b, b1):
        return (a > b and a1 <= b1) or (a < b and a1 >= b1)

    for i in range(m):
        lb1 = lb[i - 1] if i else np.nan
        sb1 = sb[i - 1] if i else np.nan
        lb2 = lb[i - 2] if i >= 2 else np.nan
        sb2 = sb[i - 2] if i >= 2 else np.nan
        r1 = r[i - 1] if i else np.nan
        nl, ns = r[i] - dar[i], r[i] + dar[i]
        lb[i] = max(lb1, nl) if (r1 > lb1 and r[i] > lb1) else nl
        sb[i] = min(sb1, ns) if (r1 < sb1 and r[i] < sb1) else ns
        if cross(r[i], r1, sb1, sb2):
            trend = 1.0
        elif cross(lb1, lb2, r[i], r1):
            trend = -1.0
        tl[i] = lb[i] if trend == 1 else sb[i]
        xl = xl + 1 if tl[i] < r[i] else 0
        xs = xs + 1 if tl[i] > r[i] else 0
        tl1 = tl[i - 1] if i else np.nan
        flag = not np.isnan(tl1) and tl1 - 50 != 0
        le[i] = xl == 1 and flag
        se[i] = xs == 1 and flag
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
