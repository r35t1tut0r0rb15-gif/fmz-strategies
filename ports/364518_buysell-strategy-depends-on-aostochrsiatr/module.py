"""AO + Stochastic + RSI: oversold stochastic (%K < 20) and RSI(low) < 30 with a rising Awesome
Oscillator goes long; the mirror goes short. Each entry carries a stop one ATR beyond the signal
bar and a target one ATR from its close.
Port of FMZ strategy #364518 "Buy&Sell Strategy depends on AO+Stoch+RSI+ATR by SerdarYILMAZ".

Source
    https://www.fmz.com/strategy/364518 (PineScript v4, FMZ last modified 2022-05-20 16:19:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 73-126), AO 3 / 17 on hl2, stoch 14 / 3, RSI(low, 10),
ATR 14 (rma of tr)
    k = sma(stoch(close, high, low, 14), 3)
    Long  = k < 20 and rsi < 30 and AO rising -> entry long,  exit(stop = low - atr, limit = close + atr)
    Short = k > 80 and rsi > 70 and AO falling -> entry short, exit(stop = high + atr, limit = close - atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Stop and target are set from the signal bar: stops() returns sl_stop = (close - (low - atr))
      / close and tp_stop = atr / close (shorts mirrored), shifted one bar inside stops(); vbt
      re-bases them on the fill price.
    * A repeated same-side signal while in the position re-sets the exit levels in Pine; vbt keeps
      the levels of the entry. This moving stop carries the mark trailing_stop_pending.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_364518_ao_stoch_rsi_atr_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stoch_k": [9, 14],
    "rsi_len": [7, 10, 14],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"ao_fast": 3, "ao_slow": 17, "stoch_k": 14, "stoch_d": 3, "rsi_len": 10, "atr_len": 14}


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


def _tr(bars):
    """Pine v4 `tr` (handle_na = false): na on the first bar."""
    pc = bars["close"].shift(1)
    return pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(),
                      (bars["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)


def _signals(bars_df, p):
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + l) / 2
    ao = hl2.rolling(int(p["ao_fast"])).mean() - hl2.rolling(int(p["ao_slow"])).mean()
    n = int(p["stoch_k"])
    st = 100 * (c - l.rolling(n).min()) / (h.rolling(n).max() - l.rolling(n).min())
    k = st.rolling(int(p["stoch_d"])).mean()
    rsi = _rsi(l, int(p["rsi_len"]))
    long_c = ((k < 20) & (rsi < 30) & (ao > ao.shift(1))).to_numpy()
    short_c = ((k > 80) & (rsi > 70) & (ao < ao.shift(1))).to_numpy()
    return long_c, short_c


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(long_c, index=idx), false.copy(), pd.Series(short_c, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _signals(bars_df, p)
    c = bars_df["close"]
    atr = _rma(_tr(bars_df), int(p["atr_len"]))
    sl = ((c - (bars_df["low"] - atr)) / c).where(long_c, ((bars_df["high"] + atr - c) / c).where(short_c))
    tp = (atr / c).where(long_c | short_c)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
