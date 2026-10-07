"""RSI 30/70 swing (long only) taken only while ATR is above its (mis-scaled) recent average.
Port of FMZ strategy #345036 "ATR-RSI组合策略" (ATR-RSI combination).

Source
    https://www.fmz.com/strategy/345036 (JavaScript, author "一刀", FMZ last modified
    2022-02-13 17:19:57). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-149), rsi_period 20, atr_period 14, atrma_period 20
    records = GetRecords(PERIOD_M15); atr = TA.ATR(records, atr_period)
    atrma = (sum of the last atrma_period ATR values) / atr_period          [sic]
    active = atr[-1] > atrma
    active and RSI < 30 and last status != BUY  -> status BUY, buy with all cash
    active and RSI > 70 and last status != SELL -> status SELL, sell all coins

Interpretation choices
    * The bot polls the forming 15-min bar every 60 s; the port evaluates on completed bar t
      ([-1] -> t). TA.ATR / TA.RSI are Wilder's.
    * atrma divides a 20-value sum by atr_period (14), so "active" means ATR above 20/14 of its
      20-bar mean. Ported exactly as written (flagged in PORT_NOTES).
    * The BUY/SELL status alternates, so the position is in from a BUY event to the next SELL
      event. Long only (spot); shorts are never emitted, so opposite entries cannot occur.
    * FREQ = "15min" (code requests PERIOD_M15).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_345036_atr_active_rsi_swing_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # code requests PERIOD_M15
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [12, 20, 30],
    "atrma_period": [10, 18, 20],
}
DEFAULT_PARAMS = {"rsi_period": 20, "atr_period": 14, "atrma_period": 20}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    atr = _atr(bars_df, int(p["atr_period"]))
    atrma = atr.rolling(int(p["atrma_period"])).sum() / int(p["atr_period"])   # as written
    active = (atr > atrma).to_numpy()
    rsi = _rsi(bars_df["close"], int(p["rsi_period"])).to_numpy()

    m = len(rsi)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    status = 0          # 0 none yet, 1 BUY, 2 SELL
    for i in range(m):
        if not active[i]:
            continue
        if rsi[i] < 30 and status != 1:
            entries[i], status = True, 1
        elif rsi[i] > 70 and status != 2:
            if status == 1:
                exits[i] = True
            status = 2

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
