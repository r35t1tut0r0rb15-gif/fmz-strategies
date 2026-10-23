"""Small "trapping" candles against a SuperTrend 2 / 10 with strong volume (rising, or three bars of falling volume in a three-bar run), 5-minute bars: a small down candle in an up-trend goes long, a small up candle in a down-trend goes short; reversing.
Port of FMZ strategy #427820 "SuperTrend Reversal Trapping Strategy" (SuperTrend Trapping Candle Strategy).

FMZ source id: 427820

Source
    https://www.fmz.com/strategy/427820 (PineScript v5, FMZ last modified 2023-09-25 17:58:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 182-219), SuperTrend factor 2, ATR 10; candle height 0.003 of the close
    isSmallCandle = high - low < close x 0.003;  isStrongVolume = volume > volume[1] or (3 falling volumes with 3 rising / falling closes and opens)
    up-trend and close < open and strong volume and small -> entry Long;  down-trend and close > open and strong volume and small -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend is the Pine reference implementation (direction -1 = up-trend), as #375951. REVERSAL
      INTENDED. The margin settings are sizing. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, counter-candle entries in a SuperTrend with volume confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin_long / margin_short 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the strong-volume tests (rising, or three falling); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427820_supertrend2_10_small_trap_candle_volume_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [2.0, 3.0],
    "candle_divider": [0.003, 0.0015],
}
DEFAULT_PARAMS = {"factor": 2.0, "candle_divider": 0.003, "atr_period": 10}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[1]
    vdec = (v < v.shift(1)) & (v.shift(1) < v.shift(2))
    bulls_dec = vdec & (c > c.shift(1)) & (c.shift(1) > c.shift(2)) & (o > o.shift(1)) & (o.shift(1) > o.shift(2))
    bears_dec = vdec & (c < c.shift(1)) & (c.shift(1) < c.shift(2)) & (o < o.shift(1)) & (o.shift(1) < o.shift(2))
    strong = (v > v.shift(1)) | bulls_dec | bears_dec
    small = (h - lo) < c * float(p["candle_divider"])
    le = (d < 0) & (c < o) & strong & small
    se = (d > 0) & (c > o) & strong & small
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
