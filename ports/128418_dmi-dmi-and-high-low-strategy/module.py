"""Fast/slow Kaufman adaptive moving average (AMA) cross, always in the market.
Port of FMZ strategy #128418 "动向指数DMI与高低点策略" (titled DMI and high-low; the code is an
AMA cross).

Source
    https://www.fmz.com/strategy/128418 (MyLanguage, author "阿基米德的浴缸", FMZ last modified
    2019-08-20 10:24:43). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 68-86), N 20, N1 4, N2 60, M 40, M1 8, M2 120
    ER  = ABS(C-REF(C,N)) / SUM(ABS(C-REF(C,1)),N)
    CS  = ER*(2/(N1+1) - 2/(N2+1)) + 2/(N2+1);  CQ = CS*CS
    AMA1 = EMA(DMA(C,CQ),2);  AMA2 the same with M, M1, M2
    BKVOL=0 AND REF(AMA1,1)<REF(AMA2,1) AND AMA2<AMA1 -> BPK
    SKVOL=0 AND REF(AMA1,1)>REF(AMA2,1) AND AMA2>AMA1 -> SPK

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars. DMA(X,A): Y = A*X + (1-A)*Y', seeded with X on the first
      bar where A exists; EMA(.,2) = ewm(span=2, adjust=False).
    * BPK closes a short and opens a long in one bar: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies). Always in the market after the
      first cross; no other exit in the source.
    * A zero denominator (N flat closes) leaves ER undefined; DMA then holds its last value.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_128418_kaufman_ama_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [10, 20, 30],
    "m": [40, 60, 80],
}
DEFAULT_PARAMS = {"n": 20, "n1": 4, "n2": 60, "m": 40, "m1": 8, "m2": 120}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ama(close, n, fast, slow):
    er = ((close - close.shift(n)).abs()
          / close.diff().abs().rolling(n).sum()).replace([np.inf, -np.inf], np.nan)
    cs = er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)
    alpha = (cs * cs).to_numpy()
    x = close.to_numpy(dtype=float)
    y = np.full(len(x), np.nan)
    prev = np.nan
    for i in range(len(x)):
        if np.isnan(alpha[i]):
            y[i] = prev
        elif np.isnan(prev):
            prev = y[i] = x[i]
        else:
            prev = y[i] = alpha[i] * x[i] + (1 - alpha[i]) * prev
    return pd.Series(y, index=close.index).ewm(span=2, adjust=False, ignore_na=True).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    a1 = _ama(close, int(p["n"]), p["n1"], p["n2"])
    a2 = _ama(close, int(p["m"]), p["m1"], p["m2"])
    up = ((a1.shift(1) < a2.shift(1)) & (a2 < a1)).to_numpy()
    dn = ((a1.shift(1) > a2.shift(1)) & (a2 > a1)).to_numpy()

    m = len(close)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if up[i] and pos != 1:          # BKVOL=0 -> BPK
            le[i], pos = True, 1
        elif dn[i] and pos != -1:       # SKVOL=0 -> SPK
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
