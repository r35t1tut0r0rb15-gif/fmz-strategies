"""Close vs typical-price EMA stop-and-reverse, gated by the EMA staying inside a band around
its own smoothed value.
Port of FMZ strategy #188507 "典型价格百分比通道-凯尔特纳与百分比通道变形" (typical-price percent
channel, a Keltner / percent-channel variant).

Source
    https://www.fmz.com/strategy/188507 (MyLanguage, author "cyberking", FMZ last modified
    2020-03-05 21:36:49). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 30-39), N 21
    DX = EMA((H+L+C)/3, N);  KRTHR = EMA(DX,N)*1.05;  KRTXR = EMA(DX,N)/1.05
    C > DX AND DX < KRTHR -> BPK;   C < DX AND DX > KRTXR -> SPK;   AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Criterion 2: the +5 % / -4.76 % bands become EMA(DX,N) +/- `band_atr` x Wilder ATR(14).
    * Daily bars (backtest period 1d) are broker days (17:00 New York); close-price model, one
      signal per bar, BPK first.
    * BPK/SPK reverse in one bar: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default
      opposite-entry reversal applies). Always in after the first signal.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_188507_typical_ema_band_gate_reverse"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [10, 21, 40],
    "band_atr": [0.5, 1.25, 2.5],
}
DEFAULT_PARAMS = {"n": 21, "band_atr": 1.25, "atr_length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["n"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    dx = ((h + lo + c) / 3).ewm(span=n, adjust=False).mean()
    centre = dx.ewm(span=n, adjust=False).mean()
    band = p["band_atr"] * _atr(bars_df, int(p["atr_length"]))
    long_sig = ((c > dx) & (dx < centre + band)).to_numpy()     # NaN band -> False
    short_sig = ((c < dx) & (dx > centre - band)).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if long_sig[i] and pos != 1:
            le[i], pos = True, 1
        elif short_sig[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
