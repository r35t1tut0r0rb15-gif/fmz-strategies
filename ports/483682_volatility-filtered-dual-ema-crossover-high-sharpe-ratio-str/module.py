"""EMA 10 / 30 crossings while ATR 14 is over its 20-bar mean plus one standard deviation, 1-minute bars: the up-cross goes long, the down-cross goes short; reversing (the per-bar ATR bracket from the current close is pending).
Port of FMZ strategy #483682 "Volatility Filtered Dual EMA Crossover High Sharpe Ratio Strategy" (Aggressive Strategy for High IV Market).

FMZ source id: 483682

Source
    https://www.fmz.com/strategy/483682 (PineScript v6, FMZ last modified 2025-02-25 11:23:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-209), EMA 10 / 30; ATR 14; ATR mean 20, sd 20; bracket 2 / 4 ATR; risk 1 % sizing; slippage input 0.001
    crossover(ema10, ema30) and atr > sma(atr, 20) + stdev(atr, 20) -> entry Long;  crossunder and same filter -> entry Short
    every bar: exit Long (stop = close - 2 atr, limit = close + 4 atr);  exit Short (stop = close + 2 atr, limit = close - 4 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. An
      entry on the other side reverses (REVERSAL INTENDED). The risk-sized quantity is sizing; the
      slippage input feeds nothing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close bracket pending.
    2 generic: PASS, EMA crossings in high ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-sized quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483682_ema10_30_cross_atr_over_mean_plus_sd_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast_length": [10, 5],
    "ema_slow_length": [30, 60],
}
DEFAULT_PARAMS = {"ema_fast_length": 10, "ema_slow_length": 30, "atr_length": 14, "atr_mean_length": 20,
                  "atr_std_length": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["ema_fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow_length"]), adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    hot = atr > atr.rolling(int(p["atr_mean_length"])).mean() + atr.rolling(int(p["atr_std_length"])).std(ddof=0)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & hot
    se = (f < s) & (f.shift(1) >= s.shift(1)) & hot
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
