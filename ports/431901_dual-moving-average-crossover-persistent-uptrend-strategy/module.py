"""SMA 8 / 21 crosses faded with an angle filter, 15-minute bars, from flat: a recent SMA 8 / 21 cross down with a steeply
falling SMA 21 goes long (and a recent cross up with a steep rise goes short), each with 1 % target and stop levels
checked on the bar; a close beyond the Bollinger band against the trade also exits, and a strong bar at the target
reverses.
Port of FMZ strategy #431901 "Dual Moving Average Crossover Persistent Uptrend Strategy" (MJ-Dual Moving Average).

FMZ source id: 431901

Source
    https://www.fmz.com/strategy/431901 (PineScript v5, FMZ last modified 2023-11-13 10:47:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-277), SMA 8 / 21, angle 7 over 2 bars on ATR 10, look-back 15, TP / SL 1 %, BB 20 / 2
    angle = degrees(atan((sma21 - sma21[2]) / atr(10) / 2)); long = a cross up within the last 15 bars and angle > 7; short mirrored
    flat: short -> entry LONG (tp / sl = close x 1.01 / 0.99);  long -> entry SHORT (mirror)   (swapped as written)
    long: high > tp -> close (and a green body over 1.4 % of the close -> entry SHORT);  close < sl -> close;
          open >= upper band and close >= upper band -> close  (mirror for shorts)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are swapped in the source (the "short" setup enters long): ported as written. A
      setup's 15-bar window excludes the current bar. The target is tested on the bar's high and the
      stop on its close, each with strategy.close (next-open exits): close-checked, not orders.
    * The closes act on the position held at the bar's start and do not undo the reversal on a
      strong bar at the target. Entries otherwise only from flat. REVERSAL INTENDED (the target
      reversal). stdev is the population deviation. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, SMA crosses, an ATR-scaled angle and percentage levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431901_ma_cross_angle_fade"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "angle": [7, 3],
    "tp_sl": [1.0, 2.0],
}
DEFAULT_PARAMS = {"angle": 7, "tp_sl": 1.0, "lookback": 2, "atr_len": 10, "window": 15}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ma1, ma2 = c.rolling(8).mean(), c.rolling(21).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    atr = _rma(tr, int(p["atr_len"]))
    lb = int(p["lookback"])
    ang = np.degrees(np.arctan((ma2 - ma2.shift(lb)) / atr / lb)).to_numpy()
    xo = ((ma1 > ma2) & (ma1.shift(1) <= ma2.shift(1))).astype(float)
    xu = ((ma1 < ma2) & (ma1.shift(1) >= ma2.shift(1))).astype(float)
    w = int(p["window"])
    lcx = (xo.shift(1).rolling(w).max() > 0).to_numpy()
    scx = (xu.shift(1).rolling(w).max() > 0).to_numpy()
    a = float(p["angle"])
    lsig = lcx & (ang > a)
    ssig = scx & (ang < -a)
    mid, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    bh, bl = (mid + 2 * sd).to_numpy(), (mid - 2 * sd).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    k = float(p["tp_sl"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    ltp = lsl = stp = ssl = np.nan
    for i in range(m):
        start = pos
        if start == 0:
            if ssig[i]:
                ltp, lsl, pos = cv[i] * (1 + k), cv[i] * (1 - k), 1
            if lsig[i]:
                stp, ssl, pos = cv[i] * (1 - k), cv[i] * (1 + k), -1
        elif start == 1:
            if hv[i] > ltp:
                pos = 0
                if cv[i] - ov[i] > cv[i] * 0.014:
                    stp, ssl, pos = cv[i] * (1 - k), cv[i] * (1 + k), -1
            if pos == 1 and (cv[i] < lsl or (ov[i] >= bh[i] and cv[i] >= bh[i])):
                pos = 0
        else:
            if lv[i] < stp:
                pos = 0
                if ov[i] - cv[i] > cv[i] * 0.014:
                    ltp, lsl, pos = cv[i] * (1 + k), cv[i] * (1 - k), 1
            if pos == -1 and (cv[i] > ssl or (ov[i] < bl[i] and cv[i] < bl[i])):
                pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
