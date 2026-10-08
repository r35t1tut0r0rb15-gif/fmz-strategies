"""EMA 110 / 40 cross with a fixed stop: EMA 110 crossing above EMA 40 goes long, crossing below
goes short; each entry carries a stop (500 ticks in the source).
Port of FMZ strategy #426506 "Fast and Slow EMA Cross Intraday Trading Strategy".

Source
    https://www.fmz.com/strategy/426506 (PineScript v2/v3 syntax, FMZ last modified 2023-09-12 16:28:09).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 105-119), "fast" 110, "slow" 40
    crossover(ema(close, 110), ema(close, 40))  -> entry long,  exit(loss = 500)
    crossunder(ema(close, 110), ema(close, 40)) -> entry short, exit(loss = 500)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the "fast" length (110) is longer than the "slow" one (40); kept.
    * Criterion 2: 500 ticks is instrument-specific (BTC: 50 USDT, a fraction of an hourly ATR).
      It becomes sl_atr x ATR(14) at the signal bar, an sl_stop fraction shifted one bar.
    * Crosses alternate, so after a stop the next entry is the opposite cross: no mirroring.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426506_ema_110_40_cross_stop"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "sl_atr": [0.25, 1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 110, "slow": 40, "sl_atr": 0.25}


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


def _crosses(bars_df, p):
    c = bars_df["close"]
    d = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    d1 = d.shift(1)
    return (d > 0) & (d1 <= 0), (d < 0) & (d1 >= 0)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _crosses(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _crosses(bars_df, p)
    frac = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(up | dn)
    return {"sl_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
