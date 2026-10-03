"""Always-in RSI-slope entry with fixed target/stop, reversing after a stop.
Port of FMZ strategy #119038 "Paul-The-Gambler-Lévy-Gold-Edition" (signals only; its
martingale sizing is stored separately).

Source
    https://www.fmz.com/strategy/119038 (Python, author "FawkesPan", FMZ last modified
    2018-09-28 16:53:43). Verbatim copy: original_source.md. Read 2026-09-29.

Original signal (original_source.md lines 116-195)
    no position: RSI14[-2] < RSI14[-1] -> open long, else open short
    long:  price > entry*(1+TAKE_PROFIT) -> cover (take profit)
           price < entry*(1-STOP_LOSS)   -> cover and open short (x AMP size)
    short: mirror image.  Defaults: STOP_LOSS 0.015, TAKE_PROFIT 0.03.

Interpretation choices
    * RSI is taken on completed bars: signal on bar t uses rsi[t] vs rsi[t-1] (the original
      compares the forming bar with the last completed one).
    * The reverse-after-stop rule needs to know that the stop fired, and stops() cannot feed
      back into signals. So target and stop are evaluated inside simulate() on bar CLOSES
      (the original polls the ticker every 30 s). A breach on bar k emits the exit (target) or
      the reverse entry (stop) on bar k, filled at k+1's open. This is a declared change of
      fill timing, not an intrabar stop.
    * Criterion 2: the 1.5 % / 3 % distances become `sl_atr` / `tp_atr` multiples of ATR(14)
      measured on the signal bar, applied to the actual entry fill (next open).
    * Position state is tracked exactly as the engine fills it (entry at next open).
      REVERSAL INTENDED on a stop: the opposite entry is emitted with no separate exit, and
      portfolio_kwargs is {} so the engine's default reversal applies.
    * Martingale sizing (AMP x size, RISK_LIMIT, START_SIZE), leverage and the weekly contract are
      sizing / venue set-up, stored in original_sizing.txt. No costs here.
    * No bar size in the source; FREQ = "1h" (README rule).
"""
import numpy as np
import pandas as pd

NAME = "fmz_119038_rsi_slope_reverse_on_stop"
FREQ = "1h"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_atr": [1.0, 2.0, 3.0],
    "tp_atr": [2.0, 4.0, 6.0],
}
DEFAULT_PARAMS = {"sl_atr": 2.0, "tp_atr": 4.0, "rsi_period": 14, "atr_length": 14}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    opn = bars_df["open"].to_numpy(dtype=float)
    close = bars_df["close"].to_numpy(dtype=float)
    rsi = _rsi(bars_df["close"], int(p["rsi_period"])).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    m = len(close)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))

    pos = 0            # position the engine holds during bar i (after this bar's open fill)
    pending = 0        # direction signalled on the previous bar, filled at this bar's open
    pend_atr = np.nan  # ATR on the signal bar of the pending entry
    entry = tp = sl = np.nan
    for i in range(m):
        if pending:
            pos, entry = pending, opn[i]
            tp = entry + pos * p["tp_atr"] * pend_atr
            sl = entry - pos * p["sl_atr"] * pend_atr
            pending = 0
        if pos == 1:
            if close[i] > tp:
                lx[i], pos = True, 0
            elif close[i] < sl:
                se[i], pending, pend_atr, pos = True, -1, atr[i], 0
            continue
        if pos == -1:
            if close[i] < tp:
                sx[i], pos = True, 0
            elif close[i] > sl:
                le[i], pending, pend_atr, pos = True, 1, atr[i], 0
            continue
        if i == 0 or np.isnan(rsi[i]) or np.isnan(rsi[i - 1]) or np.isnan(atr[i]):
            continue
        if rsi[i - 1] < rsi[i]:
            le[i], pending = True, 1
        else:
            se[i], pending = True, -1
        pend_atr = atr[i]

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
