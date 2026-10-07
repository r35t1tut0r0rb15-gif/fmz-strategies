"""Swing Hull / RSI / EMA: with the 500-bar Hull rising, a close dipping below EMA 59 (from above)
goes long; with it falling, a close below EMA 96 after being above EMA 59 goes short. RSI 14
crossing above 70 closes longs, crossing below 30 closes shorts; a fixed stop protects both.
Port of FMZ strategy #365668 "Swing Hull/rsi/EMA Strategy".

Source
    https://www.fmz.com/strategy/365668 (PineScript v2/v3 syntax, FMZ last modified 2022-05-25 16:06:18).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-129), Hull period 500, RSI 14 (70 / 30),
EMA 59 / 96, stop 75 * 10 ticks
    n1 = wma(2 wma(close, 250) - wma(close, 500), 22);  n2 = the same one bar earlier
    short: n1 <= n2 and close < ema96 and close[1] > ema59[1] -> entry short
    long:  n1 > n2 and close < ema59 and close[1] > ema59[1] -> entry long
    close short on crossunder(rsi, 30); close long on crossover(rsi, 70)
    exit(loss = 750 ticks) on either side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop is 750 ticks (instrument-specific price units). It becomes
      sl_atr x ATR(14) at the signal bar, as an sl_stop fraction of the signal close shifted one
      bar inside stops(); vbt re-bases it on the fill price.
    * The RSI closes are close-based exit signals. A close on the bar of a new entry on the same
      side does not apply (the entry is not open yet).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365668_hull_swing_ema_pullback"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "hull_period": [250, 500],
    "sl_atr": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"hull_period": 500, "rsi_len": 14, "rsi_hi": 70, "rsi_lo": 30, "fast": 59, "slow": 96,
                  "sl_atr": 2.0}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _signals(bars_df, p):
    c = bars_df["close"]
    n = int(p["hull_period"])
    diff = 2 * _wma(c, int(round(n / 2))) - _wma(c, n)
    n1 = _wma(diff, int(round(np.sqrt(n))))
    n2 = n1.shift(1)
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    ok = rsi.notna()
    up = n1 > n2
    le = (ok & up & (c < fast) & (c.shift(1) > fast.shift(1))).to_numpy()
    se = (ok & ~up & (c < slow) & (c.shift(1) > fast.shift(1))).to_numpy()
    lx = ((rsi > p["rsi_hi"]) & (rsi.shift(1) <= p["rsi_hi"])).to_numpy() & ~le
    sx = ((rsi < p["rsi_lo"]) & (rsi.shift(1) >= p["rsi_lo"])).to_numpy() & ~se
    return le, lx, se, sx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = _signals(bars_df, p)
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = _signals(bars_df, p)
    frac = p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]
    return {"sl_stop": frac.where(le | se).shift(1)}


def portfolio_kwargs(**params):
    return {}
