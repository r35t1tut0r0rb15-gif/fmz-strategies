"""RSI 14 recoveries from 20 into 20-30, or a MACD cross up under all three SMAs after an RSI above 30, 1-hour bars, long only, from flat: stop 0.5 % and target one ATR(14) from the signal close; an RSI at
50 or more moves the stop to the bar's high (closing at the next open), and a MACD cross down closes.
Port of FMZ strategy #446761 "多指标BTC交易策略-Multi-indicator-BTC-Trading-Strategy" (1M Advanced Strat (Advanced Strategy)).

FMZ source id: 446761

Source
    https://www.fmz.com/strategy/446761 (PineScript v4, FMZ last modified 2024-04-01 11:26:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-171), RSI 14, bounds 20 / 30; MACD 12 / 26 / 9; SMA 20 / 50 / 200; ATR 14; risk 0.005
    long = (rsi > 20 and rsi < 30 and rsi(close[1]) < 20) or (rsi(close[1]) > 30 and crossover(macd, signal) and close < sma20, sma50, sma200)  ("and" binds before "or")
    long and flat -> entry Long, exit(stop = close x 0.995, limit = close + atr);  long and rsi >= 50 -> exit("Update SL", stop = high);  crossunder(macd, signal) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or", so the condition is two alternatives, as ported; rsi(close[1]) is the
      previous bar's RSI. The bracket is set on the signal bar from its close: sl_stop 0.005 and tp_stop
      = ATR / close, shifted one bar inside stops() and re-based on the fill (entries only from flat).
      The "Update SL" exit puts a sell stop at the bar's high, above the price, so it fills at the next
      open: the port closes the long on that bar's signal (a gap above the high would leave it
      waiting, as written). The signals run without a state loop, since the bracket can end a trade
      the signals cannot see. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar; the wrong-side stop read as a close.
    2 generic: PASS, RSI recovery or MACD cross entries, bracket and RSI / MACD exits.
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

NAME = "fmz_446761_rsi_recovery_or_macd_cross_bracket_rsi50_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_low": [20.0, 25.0],
    "sl": [0.005, 0.01],
}
DEFAULT_PARAMS = {"rsi_low": 20.0, "sl": 0.005, "rsi_high": 30.0, "rsi_len": 14, "atr_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["rsi_len"])
    r = _rsi(c, n)
    r_prev = _rsi(c.shift(1), n)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    xo = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    below = (c < c.rolling(20).mean()) & (c < c.rolling(50).mean()) & (c < c.rolling(200).mean())
    lo_, hi_ = float(p["rsi_low"]), float(p["rsi_high"])
    go = (((r > lo_) & (r < hi_) & (r_prev < lo_)) | ((r_prev > hi_) & xo & below)).to_numpy()
    r50 = (r >= 50).to_numpy()
    # no state loop: the bracket can end a trade the signals cannot see; an entry while long is
    # ignored by the engine, and a same-bar exit test gives way to an entry taken from flat
    out = (r50 | xu) & ~go                           # stop at the high (above the price) or the MACD close
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(go, index=ix), pd.Series(out, index=ix), false, false.copy()


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": float(p["sl"]), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
