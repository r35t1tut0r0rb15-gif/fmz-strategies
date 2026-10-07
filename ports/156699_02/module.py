"""MA-of-high / MA-of-low breakout stop-and-reverse with a close-vs-MA exit (example 02).
Port of FMZ strategy #156699 "均线策略范例02" (moving-average strategy example 02).

Source
    https://www.fmz.com/strategy/156699 (MyLanguage, author "发明者量化-小小梦", FMZ last modified
    2019-07-12 10:23:45). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 17-23)
    M5H = MA(H,5); M5L = MA(L,5)
    C > M5H -> BPK;   C < M5L -> SPK
    C < MA(C,5) AND BKVOL>0 -> SP;   C > MA(C,5) AND SKVOL>0 -> BP
    AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars, one signal per bar, first valid statement in source
      order. BPK while short reverses: REVERSAL INTENDED (portfolio_kwargs {}; the engine's
      default opposite-entry reversal applies). BPK while long is not a signal.
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_156699_ma_high_low_reverse"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [3, 5, 8, 13],
}
DEFAULT_PARAMS = {"n": 5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["n"])
    c = bars_df["close"].to_numpy(dtype=float)
    mh = bars_df["high"].rolling(n).mean().to_numpy()
    ml = bars_df["low"].rolling(n).mean().to_numpy()
    mc = bars_df["close"].rolling(n).mean().to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos != 1 and c[i] > mh[i]:            # BPK
            le[i], pos = True, 1
        elif pos != -1 and c[i] < ml[i]:         # SPK
            se[i], pos = True, -1
        elif pos == 1 and c[i] < mc[i]:          # SP
            lx[i], pos = True, 0
        elif pos == -1 and c[i] > mc[i]:         # BP
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
