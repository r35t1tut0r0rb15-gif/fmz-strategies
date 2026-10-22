"""MACD 8 / 26 / 5 crossings against the EMA 30, 3-hour bars: the MACD crossing up with the close under the EMA goes long, crossing down with the close over it goes short, each with a 10 ATR stop from the signal close; reversing.
Port of FMZ strategy #471687 "Multi Indicator Fusion Mean Reversion Trend Following Strategy" (Mean Reversion Strategy with ATR, MACD and MA).

FMZ source id: 471687

Source
    https://www.fmz.com/strategy/471687 (PineScript v5, FMZ last modified 2024-11-12 14:30:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-153), EMA 30 (SMA option); MACD 8 / 26 / 5; ATR 10 x 10 stop
    crossover(macd, signal) and close < ema30 -> entry Buy + exit(stop = close - 10 atr);  crossunder and close > ema30 -> entry Sell + exit(stop = close + 10 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent once on the signal bar: ported as ATR 10 / close of the signal bar shifted into the
      fill. There is no target. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header
      (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at entry.
    2 generic: PASS, MACD crossings against the EMA with a wide ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_471687_macd8_26_5_cross_against_ema30_atr10_stop_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_length": [30, 50],
    "atr_mult": [10.0, 3.0],
}
DEFAULT_PARAMS = {"ma_length": 30, "atr_mult": 10.0, "atr_len": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.ewm(span=int(p["ma_length"]), adjust=False).mean()
    macd = c.ewm(span=8, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=5, adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c < ma)
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (c > ma)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
