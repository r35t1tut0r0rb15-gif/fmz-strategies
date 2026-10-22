"""EMA 50 pullback continuation, 10-minute bars, long only: with the EMA 80 above the EMA 200, a close back above the EMA 50 the bar after the close dipped under it (and not below the previous close)
goes long; a stop 3.5 ATR(14) below the entry; a close 3.5 ATR above the entry but under the EMA 50 closes.
Port of FMZ strategy #440373 "Robust Trend Continuation Strategy" (Trend_Continuation).

FMZ source id: 440373

Source
    https://www.fmz.com/strategy/440373 (PineScript v5, FMZ last modified 2024-01-29 16:57:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-155), EMA 50 / 80 / 200 on close; number of candles 1; stop and target factors 3.5 / 3.5; ATR 14
    long = ema80 > ema200 and close > ema50 and crossunder(close[1], ema50) and allPositive (close >= close[1] and close >= ema50) -> entry Long
    atrAtLong = valuewhen(bought, atr(14), 0);  close >= avg + 3.5 atrAtLong and close < ema50 -> close Long;  close < avg -> strategy.exit(stop = avg - 3.5 atrAtLong)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR is taken on the fill bar in the script; the port uses the signal bar's ATR as a fraction
      of its close (as #434998). The stop is sl_stop, shifted one bar inside stops() and re-based on the
      fill; the script only sends it once a close is below the entry (it then stays), the port holds it
      from the fill (the difference is a first close-below bar that also reaches the level). The target
      is a close test sent at the next open. An entry while long is ignored, so trades start only from
      flat. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "10min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, EMA pullback and ATR levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440373_ema50_pullback_continuation_atr"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_factor": [3.5, 2.0],
    "tp_factor": [3.5, 2.0],
}
DEFAULT_PARAMS = {"sl_factor": 3.5, "tp_factor": 3.5, "ma1": 50, "ma2": 80, "ma3": 200, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _setup(bars_df, p):
    c = bars_df["close"]
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ma1", "ma2", "ma3"))
    c1 = c.shift(1)
    xu = (c1 < e1) & (c.shift(2) >= e1.shift(1))
    pos_ok = ~((c < c1) | (c < e1))
    long_ = (e2 > e3) & (c > e1) & xu & pos_ok
    a = _atr(bars_df, p["atr_len"]) / c
    return long_.to_numpy(), float(p["sl_factor"]) * a, float(p["tp_factor"]) * a, e1


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sig, sl_s, tp_s, e1 = _setup(bars_df, p)
    sl, tp, ev = sl_s.to_numpy(), tp_s.to_numpy(), e1.to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    lv = bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_):
                pos = 0
            elif cv[i] >= x * (1 + t_) and cv[i] < ev[i]:
                lx[i], pos = True, 0
        if pos == 0 and i + 1 < m and sig[i] and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = _setup(bars_df, p)[1]
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
