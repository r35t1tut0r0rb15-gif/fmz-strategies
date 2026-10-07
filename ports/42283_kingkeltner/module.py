"""Keltner (SMA + k*ATR) upper-band breakout, long only, with a close-based trailing exit.
Port of FMZ strategy #42283 "KingKeltner趋势策略_低频" (KingKeltner trend strategy, low frequency).

Source
    https://www.fmz.com/strategy/42283 (JavaScript, author "ipqhjjybj", ported by them from vnpy;
    FMZ last modified 2017-06-02 23:06:08). Verbatim copy: original_source.md. Read 2026-09-29.

Original signal (original_source.md lines 98-131)
    kk_ATR = TA.ATR(records, KK_Length); kk_Mid = TA.MA(records, KK_Length)
    kk_Up  = kk_Mid[last] + kk_ATR[last] * kkDev
    flat and LastRecord.Close > kk_Up        -> buy; intraTradeHigh = LastRecord.High
    long: intraTradeHigh = max(intraTradeHigh, LastRecord.High)
          LastRecord.Close < intraTradeHigh * (1 - trailingPrcnt/100)   -> sell all
    Defaults: KK_Length 11, kkDev 1.3, trailingPrcnt 15.

Interpretation choices
    * The bot polls the forming bar (records[len-1]); the port evaluates the same rule on each
      completed bar t (current bar included in the SMA/ATR windows and in the running high).
    * Criterion 2: the 15 % trailing distance is re-expressed as `trail_atr` multiples of the same
      ATR(KK_Length): exit when close[t] < running_high - trail_atr * ATR[t].
    * The trailing exit depends on the port's own position, so simulate() walks the bars once,
      tracking position exactly as the engine will (entry fills at the next open; exits likewise).
      The running high starts at the signal bar's high, as in the original (line 111).
    * Long only (spot). Shorts are never emitted, so opposite entries cannot occur.
    * No bar size in the source; FREQ = "bar_size_pending" (rule 2026-10-07: never choose a bar
      size; until 2026-10-07 this port used the old "1h" default). Logic unchanged.
    * Sizing (all-in buy, minMoney guard, SlidePrice) is in original_sizing.txt. No costs here.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_42283_kingkeltner_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-03, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kk_length": [10, 20, 40],
    "kk_dev": [1.0, 1.5, 2.0],
    "trail_atr": [3.0, 6.0, 12.0],
}
DEFAULT_PARAMS = {"kk_length": 11, "kk_dev": 1.3, "trail_atr": 6.0}


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
    return _rma(tr, n)  # tr[0] is NaN (no previous close), as in TA-Lib


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["kk_length"])
    close = bars_df["close"].to_numpy(dtype=float)
    high = bars_df["high"].to_numpy(dtype=float)
    atr = _atr(bars_df, n).to_numpy()
    upper = bars_df["close"].rolling(n).mean().to_numpy() + p["kk_dev"] * atr

    entries = np.zeros(len(close), dtype=bool)
    exits = np.zeros(len(close), dtype=bool)
    in_pos = False
    pending_entry = False   # entry signalled on the previous bar; filled at this bar's open
    run_high = np.nan
    for i in range(len(close)):
        if pending_entry:
            in_pos, pending_entry = True, False
        if in_pos:
            run_high = max(run_high, high[i])
            if not np.isnan(atr[i]) and close[i] < run_high - p["trail_atr"] * atr[i]:
                exits[i] = True
                in_pos = False      # engine exits at the next open; flat for signalling from i+1
            continue
        if not np.isnan(upper[i]) and close[i] > upper[i]:
            entries[i] = True
            pending_entry = True
            run_high = high[i]

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
