"""EMA cross JC intraday: EMA 9 crossing above EMA 15 before 15:20 goes long, crossing below goes
short; each trade has a stop 100 and a target 200 (price units) from the signal close, and any
open trade is closed from 15:20 on (intraday square-off).
Port of FMZ strategy #425773 "EMA-Cross-JC Intraday with Trailing SL".

Source
    https://www.fmz.com/strategy/425773 (PineScript v5, FMZ last modified 2023-09-04 15:39:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 67-109), EMA 15 / 9, intraday on, exit 15:20,
take profit 200, stop loss 100
    emaup and time < today 15:20 -> entry long; exit(stop = close - 100, limit = close + 200)
    emadown and time < today 15:20 -> entry short (mirrored)
    a trade open and time >= today 15:20 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 100 / 200 are price units. They become sl_atr / 2 sl_atr x ATR(14) at the signal
      bar (the source's 1:2 ratio), as sl_stop / tp_stop fractions shifted one bar in stops().
    * The square-off clock is the symbol's exchange time; for the header's Binance pair that is
      UTC, which the port uses. The session rule is logic (kept); close_all -> exit signals.
    * trailingStop is declared na and never set, so the "Trailing Stop" exit does nothing; no
      trailing mark is needed. The TSI filter is commented out.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425773_ema_cross_intraday_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "slow": [15, 26],
    "fast": [5, 9],
    "sl_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"slow": 15, "fast": 9, "sl_atr": 1.0, "exit_minute": 920}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    idx = bars_df.index
    minute = np.asarray(idx.hour * 60 + idx.minute)
    before = minute < p["exit_minute"]
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy() & before
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy() & before
    square = ~before
    return up, dn, square & ~up & ~dn


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, sq = _signals(bars_df, p)
    idx = bars_df.index
    return (pd.Series(up, index=idx), pd.Series(sq, index=idx),
            pd.Series(dn, index=idx), pd.Series(sq, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, _ = _signals(bars_df, p)
    frac = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(pd.Series(up | dn, index=bars_df.index))
    return {"sl_stop": frac.shift(1), "tp_stop": (2 * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
