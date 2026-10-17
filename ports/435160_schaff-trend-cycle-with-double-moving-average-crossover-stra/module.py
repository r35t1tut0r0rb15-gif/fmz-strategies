"""Schaff Trend Cycle turns in the EMA 35 / 200 trend, 3-hour bars: the STC crossing above 25 with the EMA 35 above the EMA
200 and the close above the EMA 35 goes long; the STC crossing below 75 in the down trend goes short (reversing); each trade
carries a 400-tick target and stop, re-expressed as an ATR multiple.
Port of FMZ strategy #435160 "Schaff Trend Cycle with Double Moving Average Crossover Strategy" (STC).

FMZ source id: 435160

Source
    https://www.fmz.com/strategy/435160 (PineScript v4, FMZ last modified 2023-12-12 17:43:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 172-222), STC: MACD 23 / 50, cycle 10, %D 3 / 3; EMA 35 / 200 ("SMA" inputs); target / stop 400 ticks
    k = stoch(macd, 10) (fixnan, nz);  d = ema(k, 3);  kd = stoch(d, 10);  stc = clamp(ema(kd, 3), 0, 100)
    crossover(stc, 25) and ema35 > ema200 and close > ema35 -> entry long;  crossunder(stc, 75) and ema35 < ema200 and close < ema35 -> entry short;  exit(profit = 400, loss = 400)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 400 ticks of 0.1 on 3-hour BTC (40 USD) are about 0.11 x the Wilder ATR 14 of the
      signal bar; the port uses tp_stop = sl_stop = k_atr x ATR / close of the signal bar, shifted
      one bar inside stops() (re-based on the fill). Both sides use the entry id "Riposte", so an
      opposite signal reverses: REVERSAL INTENDED. The capital-based order size is sizing.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. FREQ
      = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital-based order size stored; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_435160_stc_ema_trend_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cycle": [10, 20],
    "k_atr": [0.11, 1.0],
}
DEFAULT_PARAMS = {"fast": 23, "slow": 50, "cycle": 10, "d1": 3, "d2": 3, "ma1": 35, "ma2": 200, "k_atr": 0.11,
                  "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _stoch_fix(x, n):
    """nz(fixnan(stoch(x, x, x, n))): a NaN or a zero range keeps the last value; 0 before any."""
    s = pd.Series(x)
    lo, hi = s.rolling(n).min().to_numpy(), s.rolling(n).max().to_numpy()
    out = np.zeros(len(x))
    last = np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        for i in range(len(x)):
            v = 100 * (x[i] - lo[i]) / (hi[i] - lo[i])
            if np.isfinite(v):
                last = v
            out[i] = 0.0 if np.isnan(last) else last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = (c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()).to_numpy()
    n = int(p["cycle"])
    k = _stoch_fix(macd, n)
    d = pd.Series(k).ewm(span=int(p["d1"]), adjust=False).mean().to_numpy()
    kd = _stoch_fix(d, n)
    stc = pd.Series(kd, index=c.index).ewm(span=int(p["d2"]), adjust=False).mean().clip(0, 100)
    e1 = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    le = ((stc > 25) & (stc.shift(1) <= 25) & (e1 > e2) & (c > e1)).astype(bool)
    se = ((stc < 75) & (stc.shift(1) >= 75) & (e1 < e2) & (c < e1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f.copy()}


def portfolio_kwargs(**params):
    return {}
