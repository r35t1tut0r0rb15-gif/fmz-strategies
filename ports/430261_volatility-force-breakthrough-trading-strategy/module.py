"""EMA 3 / 20 of the cumulative force (volume x close change) with ATR 20 above ATR 50, hourly bars: the fast force EMA above the slow one in a rising-volatility regime, newly so (either just crossed or volatility just rose) on an up bar, goes long; the mirror on a down bar goes short; reversing.
Port of FMZ strategy #430261 "Volatility Force Breakthrough Trading Strategy" (yuthavithi volatility based force trade scalper strategy).

FMZ source id: 430261

Source
    https://www.fmz.com/strategy/430261 (PineScript v2, FMZ last modified 2023-10-26 16:17:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 175-210), force EMAs 3 / 20; ATR 20 / 50; BB 20 x 2 only plotted
    xforce = cum(volume x (close - nz(close[1])));  bullish = ema(xforce, 3) > ema(xforce, 20) and atr(20) > atr(50) and (the EMAs were the other way or the ATRs were) one bar back and close > open -> entry Buy
    bearish mirror and close < open -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first bar's force uses nz(close[1]) = 0 (volume x close), an offset carried by the running sum; it
      shifts both EMAs alike once they settle. ATR is Pine's atr (Wilder). The Bollinger bands only feed
      plots. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cumulative force EMA cross in rising volatility.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the cumulative force volume x close change; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430261_cumulative_force_ema3_20_rising_atr_reversal"
FAMILY = "force_index"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 20, "atr_fast": 20, "atr_slow": 50}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    af, asl = _rma(tr, int(p["atr_fast"])), _rma(tr, int(p["atr_slow"]))
    xf = (v * (c - pc.fillna(0.0))).cumsum()
    ff = xf.ewm(span=int(p["fast"]), adjust=False).mean()
    fs = xf.ewm(span=int(p["slow"]), adjust=False).mean()
    vol_up = af > asl
    was_vol = af.shift(1) < asl.shift(1)
    le = (ff > fs) & vol_up & ((ff.shift(1) < fs.shift(1)) | was_vol) & (c > o)
    se = (ff < fs) & vol_up & ((ff.shift(1) > fs.shift(1)) | was_vol) & (c < o)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
