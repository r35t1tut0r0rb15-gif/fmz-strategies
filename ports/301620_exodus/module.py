"""EMA(8/34) cross confirmed by a MACD histogram sign change within a few bars, with a close
stop and a fixed reward-to-risk target ("three-MA system Exodus").
Port of FMZ strategy #301620 "三均线系统Exodus".

Source
    https://www.fmz.com/strategy/301620 (JavaScript, author "Exodus[策略代写]", FMZ last
    modified 2021-11-28 07:20:15). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 60-262), afterEmaCrossTime 4, stopLossRate true (1),
winLossRate 5, period 60, EMA 8/34/89, MACD 16/26/9
    once per `period` minutes (just after a bar opens), on r = GetRecords(PERIOD_M1*period):
    Close(): long and (Last < entry*(1-1%) or Last > entry*(1+5%)) -> close; short mirror
    EMA8/EMA34 cross -> emaMeet = 1 (golden) / 2 (dead), lastEmaCrossTime = bar time
    MACD histogram sign change -> macdMeet = 1 / 2, lastMacdCrossTime = bar time
    both crosses within afterEmaCrossTime hours:
        emaMeet == 1 && macdMeet == 1 && dif >= 0 -> open long (only when no position)
        emaMeet == 2 && macdMeet == 2 && dif < 0  -> open short (only when no position)

Interpretation choices
    * The loop wakes just after each bar opens and reads records[-1] (the new bar); the port
      evaluates on completed bar t ([-1] -> t; ticker.Last -> close[t]).
    * The cross windows are in hours; with the default 60-minute bars that is a bar count,
      `within` = 4 bars.
    * Criterion 2: the 1 % stop and the 1 % x 5 target become `stop_atr` x Wilder ATR(14) of the
      signal bar and `win_loss` x that distance, measured from the entry fill (next open).
      Both are close checks -> exit signals (rule 3 by analogy), not sl_stop/tp_stop.
    * Close() runs before the entry logic each pass; the port does not open on the bar an exit
      fires (flat first). Entries only from flat: opposite entries cannot occur;
      portfolio_kwargs also returns upon_opposite_entry="ignore" (rule 6).
    * EMA89 is computed but unused in the code. FMZ TA.EMA = pandas ewm(adjust=False).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_301620_ema_cross_macd_confirm"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # code requests PERIOD_M1 * period, period = 60 (argument default)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "within": [2, 4, 8],
    "stop_atr": [1.0, 2.0, 3.0],
    "win_loss": [2.0, 5.0],
}
DEFAULT_PARAMS = {"within": 4, "stop_atr": 2.0, "win_loss": 5.0, "ema1": 8, "ema2": 34,
                  "macd1": 16, "macd2": 26, "macd3": 9, "atr_length": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    e1 = close.ewm(span=int(p["ema1"]), adjust=False).mean().to_numpy()
    e2 = close.ewm(span=int(p["ema2"]), adjust=False).mean().to_numpy()
    dif_s = (close.ewm(span=int(p["macd1"]), adjust=False).mean()
             - close.ewm(span=int(p["macd2"]), adjust=False).mean())
    hist = (dif_s - dif_s.ewm(span=int(p["macd3"]), adjust=False).mean()).to_numpy()
    dif = dif_s.to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    o = bars_df["open"].to_numpy(dtype=float)
    c = close.to_numpy(dtype=float)
    k = int(p["within"])

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    ema_meet = macd_meet = 0
    ema_t = macd_t = -10 ** 9
    pos, pending, entry, dist, pend_dist = 0, 0, np.nan, np.nan, np.nan
    for i in range(1, m):
        if pending:
            pos, entry, dist, pending = pending, o[i], pend_dist, 0
        exited = False
        if pos == 1 and (c[i] < entry - dist or c[i] > entry + p["win_loss"] * dist):
            lx[i], pos, exited = True, 0, True
        elif pos == -1 and (c[i] > entry + dist or c[i] < entry - p["win_loss"] * dist):
            sx[i], pos, exited = True, 0, True
        if (e1[i - 1] < e2[i - 1]) != (e1[i] < e2[i]):          # GetCrossStatus
            cross = 1 if e1[i] > e2[i] else (2 if e1[i] < e2[i] else 0)
            if cross and cross != ema_meet:
                ema_meet, ema_t = cross, i
        if (hist[i] < 0) != (hist[i - 1] < 0):
            if hist[i] > 0:
                macd_meet, macd_t = 1, i
            elif hist[i] < 0:
                macd_meet, macd_t = 2, i
        if pos == 0 and not exited and i - ema_t <= k and i - macd_t <= k and not np.isnan(atr[i]):
            if ema_meet == 1 and macd_meet == 1 and dif[i] >= 0:
                le[i], pending, pend_dist = True, 1, p["stop_atr"] * atr[i]
            elif ema_meet == 2 and macd_meet == 2 and dif[i] < 0:
                se[i], pending, pend_dist = True, -1, p["stop_atr"] * atr[i]

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
