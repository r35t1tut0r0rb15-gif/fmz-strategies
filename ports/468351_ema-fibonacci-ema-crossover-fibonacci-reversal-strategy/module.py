"""EMA 50 crossings, 50-61.8 % retracement closes and RSI lows, 1-hour bars: above the EMA 50, a close crossing over it, a close inside the 20-bar range's 50-61.8 % zone or an RSI under 30 at a 14-bar closing low goes long; under it, an upper-wick rejection of the EMA, the zone or the RSI low goes short; reversing. The 2 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #468351 "EMA交叉Fibonacci反转策略-EMA-Crossover-Fibonacci-Reversal-Strategy" (Counter Trend Trading Strategy).

FMZ source id: 468351

Source
    https://www.fmz.com/strategy/468351 (PineScript v5, FMZ last modified 2024-09-26 17:33:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-214), EMA 50; RSI 14; 20-bar high / low updated every bar; zone 0.5-0.618 of the range from the low; 20-bar breakouts (never true, current bar included); target / stop 2 % of the current close
    (crossover(close, ema50) or rejection or zone or rsi < 30 and close == lowest(close, 14) or close > highest(high, 20)) and close > ema50 -> entry Long
    (the same with close < lowest(low, 20)) and close < ema50 -> entry Short;  every bar: exit(limit / stop = close x (1 +- 0.02))

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.change(time) holds on every bar, so the range is the current 20-bar range. Some parts can never
      hold, as written: the EMA rejection (a close under the EMA) on the long side, the cross-up on the
      short side, and both breakouts (the current bar is inside its own 20-bar range). The bracket is
      re-sent on every bar from that bar's close, so its levels move after entry: stops() cannot
      express a level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA, retracement-zone and RSI-low entries; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
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

NAME = "fmz_468351_ema50_side_zone_rsi_low_entries_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [50, 100],
    "lookback": [20, 50],
}
DEFAULT_PARAMS = {"ema_len": 50, "lookback": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    z5, z618 = ll + (hh - ll) * 0.5, ll + (hh - ll) * 0.618
    xo = (c > e) & (c.shift(1) <= e.shift(1))
    rej = (h > e) & (c < e)
    zone = (c <= z618) & (c >= z5)
    rdiv = (r < 30) & (c == c.rolling(14).min())
    le = (xo | rej | zone | rdiv | (c > hh)) & (c > e)
    se = (xo | rej | zone | rdiv | (c < ll)) & (c < e)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
