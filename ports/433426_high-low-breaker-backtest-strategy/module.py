"""Fresh 50-bar high / low breaks, 1-minute bars: a high above the highest high of the previous 51 bars, when that high
was set at least 30 bars earlier, goes long; the mirror low break goes short. Each trade carries a 0.15 % stop and a
0.1 % target.
Port of FMZ strategy #433426 "High Low Breaker Backtest Strategy" (High/Low Breaker Backtest 1.0).

FMZ source id: 433426

Source
    https://www.fmz.com/strategy/433426 (PineScript v3, FMZ last modified 2023-11-27 15:37:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-225), candles back 50, ignore last 30, highs and lows on; TP 0.1 %, SL 0.15 % both sides
    idx = bars back to the highest high in [0, 50] (ties -> the oldest);  max = high[idx]
    isNewHigh = high > max[1] and idx[1] + 1 > 30 -> entry long, exit(stop = avg (1 - 0.15 %), limit = avg (1 + 0.1 %));  lows mirror -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "if high > max" updates can never fire (max already includes the current bar) and are
      dropped. The window of the previous bar covers its 50 earlier bars and itself.
    * The bracket is symmetric: sl_stop 0.0015, tp_stop 0.001 of the fill. A new high while long is
      ignored (pyramiding 1); a low break while long reverses, and a bar breaking both sides ends
      short (the short entry is issued last): REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, channel breaks and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
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

NAME = "fmz_433426_high_low_breaker_bracket"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.0015, 0.005],
    "tp_pct": [0.001, 0.005],
}
DEFAULT_PARAMS = {"back": 50, "ignore": 30, "sl_pct": 0.0015, "tp_pct": 0.001}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ext(v, n, hi):
    """Value and bars-back of the extreme over the last n + 1 values (ties -> the oldest)."""
    m = len(v)
    val, back = np.full(m, np.nan), np.full(m, np.nan)
    if m > n:
        win = np.lib.stride_tricks.sliding_window_view(v, n + 1)
        j = np.argmax(win, axis=1) if hi else np.argmin(win, axis=1)   # first occurrence = oldest
        val[n:] = win[np.arange(len(j)), j]
        back[n:] = n - j
    return val, back


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    n, ig = int(p["back"]), int(p["ignore"])
    mx, bh = _ext(h, n, True)
    mn, bl = _ext(lo, n, False)
    mx1, bh1 = np.concatenate(([np.nan], mx[:-1])), np.concatenate(([np.nan], bh[:-1]))
    mn1, bl1 = np.concatenate(([np.nan], mn[:-1])), np.concatenate(([np.nan], bl[:-1]))
    with np.errstate(invalid="ignore"):
        le = (h > mx1) & (bh1 + 1 > ig)
        se = (lo < mn1) & (bl1 + 1 > ig)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    # both breaks on one bar: the short order is issued last and ends the bar's net position short
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
