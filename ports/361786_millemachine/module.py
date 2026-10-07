"""HMA turning-point entries filtered by a rising/falling McGinley baseline, exit on the next HMA
turn, 2-ATR initial stop (its ratcheting trail is pending).
Port of FMZ strategy #361786 "MilleMachine" (Milleman).

Source
    https://www.fmz.com/strategy/361786 (PineScript v4, FMZ last modified 2022-05-08 16:22:45).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 66-203), Mode LongShort, ATR x2, BL McGinley 50,
EI HMA 46, trailing stop on (EMA of low 5 / of high 2)
    GoLong  = crossover(EI, EI[1]) and flat and BL/BL[1] > 1
    GoShort = crossunder(EI, EI[1]) and flat and BL/BL[1] < 1
    ExitLong = long and crossunder(EI, EI[1]) -> close_all;  ExitShort mirror
    SL = 1 - close/(close + 2*ATR(14)); entry: stop at close*(1-SL) (long) / close*(1+SL) (short)
    while in position: stop := max(stop, EMA(low,5)*(1-SL)) (long), min(.., EMA(high,2)*(1+SL)) (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(EI, EI[1]) = the HMA turning up (EI > EI[1] and EI[1] <= EI[2]).
    * The initial stop is fixed at entry: stops() returns sl_stop = SL of the signal bar,
      shifted one bar inside stops() (vbt reads it on the fill bar); the level is re-based on the
      fill price. The ratcheting trail cannot be expressed by stops(): rule 2, mark
      trailing_stop_pending, described in PORT_NOTES. UseTP is off in the source (no target).
    * simulate() tracks the position from its own signals and cannot see stop-outs; entries need
      a flat position, so after a stop-out the next entry waits for the next HMA turn (PORT_NOTES).
      Opposite entries cannot occur; portfolio_kwargs returns upon_opposite_entry="ignore".
    * No backtest header: FREQ = "bar_size_pending" (rule 1). If the project sets a bar size
      above 1 h, the mark coarse_bar_stop also applies.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_361786_hma_turn_mcginley_filter"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ei_len": [30, 46, 60],
    "bl_len": [30, 50, 100],
    "atr_mult": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"ei_len": 46, "bl_len": 50, "atr_mult": 2.0, "atr_length": 14}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    half, root = int(n / 2), int(round(np.sqrt(n)))
    return _wma(2 * _wma(x, half) - _wma(x, n), root)


def _mcginley(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if i == 0 or np.isnan(out[i - 1]):
            out[i] = v[i]
        else:
            out[i] = out[i - 1] + (v[i] - out[i - 1]) / (n * (v[i] / out[i - 1]) ** 4)
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ei = _hma(c, int(p["ei_len"]))
    bl = _mcginley(c, int(p["bl_len"]))
    up = ((ei > ei.shift(1)) & (ei.shift(1) <= ei.shift(2))).to_numpy()
    dn = ((ei < ei.shift(1)) & (ei.shift(1) >= ei.shift(2))).to_numpy()
    bl_up = (bl / bl.shift(1) > 1).to_numpy()
    bl_dn = (bl / bl.shift(1) < 1).to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos == 0:
            if up[i] and bl_up[i]:
                le[i], pos = True, 1
            elif dn[i] and bl_dn[i]:
                se[i], pos = True, -1
        elif pos == 1 and dn[i]:
            lx[i], pos = True, 0
        elif pos == -1 and up[i]:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    x_atr = p["atr_mult"] * _atr_pine(bars_df, int(p["atr_length"]))
    sl = x_atr / (bars_df["close"] + x_atr)        # SL fraction on the signal bar
    return {"sl_stop": sl.shift(1)}                 # read on the fill bar


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
