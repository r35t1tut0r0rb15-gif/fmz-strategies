"""ASCTrend state flips, hourly bars: a Williams %R (3, 4 or 3 + 2 x RISK, picked by counts of large bodies and 3-bar moves against the 10-bar average range) over 67 + RISK sets an up state, under 33 - RISK a down state; the flip to up goes long, the flip to down goes short; reversing.
Port of FMZ strategy #473271 "Adaptive Range Volatility Trend Following Trading Strategy" (ASCTrend).

FMZ source id: 473271

Source
    https://www.fmz.com/strategy/473271 (PineScript v5, FMZ last modified 2024-11-28 17:24:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-129), ASC length 10, RISK 3, eternal off; 100 % of equity
    WprAbs = 100 + (TrueCount2 > 0 ? wpr4 : TrueCount > 0 ? wpr3 : wpr(3 + 2 RISK));  trend := WprAbs < 33 - RISK ? -1 : WprAbs > 67 + RISK ? 1 : trend[1];  crossover(trend, 0) -> entry Long;  crossunder(trend, 0) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Range = highest(high, 10) - lowest(low, 10) (the one-argument forms), its SMA 10; TrueCount counts
      bodies of at least 2 x that average over 10 bars, TrueCount2 3-bar moves of at least 4.6 x over 7
      bars (a test with na counts 0; a sum reaching before the first bar is na and fails "> 0", as
      Pine). The state starts at 0 and is
      kept in a loop when %R is na or between the levels. eternal off (offset 0). There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. The equity share is not ported. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Williams %R state flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_473271_asctrend_wpr_state_flip_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "asc_length": [10, 20],
    "risk": [3, 6],
}
DEFAULT_PARAMS = {"asc_length": 10, "risk": 3}


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


def _wpr(bars_df, n):
    hh = bars_df["high"].rolling(n).max()
    ll = bars_df["low"].rolling(n).min()
    return 100 * (bars_df["close"] - hh) / (hh - ll)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n, risk = int(p["asc_length"]), int(p["risk"])
    x1, x2 = 67 + risk, 33 - risk
    rng = h.rolling(n).max() - lo.rolling(n).min()
    avg = rng.rolling(n).mean()
    cnt1 = ((o - c).abs() >= avg * 2.0).astype(float)          # a test with na is false: 0
    cnt2 = ((c.shift(3) - c).abs() >= avg * 4.6).astype(float)
    tc1 = cnt1.rolling(n).sum()
    tc2 = cnt2.rolling(n - 3).sum()
    w = 100 + _wpr(bars_df, 3 + 2 * risk).where(~(tc1 > 0), _wpr(bars_df, 3)).where(~(tc2 > 0), _wpr(bars_df, 4))
    wv = w.to_numpy(dtype=float)
    tr = np.zeros(len(wv))
    prev = 0.0
    for i in range(len(wv)):
        if wv[i] < x2:
            prev = -1.0
        elif wv[i] > x1:
            prev = 1.0
        tr[i] = prev
    t = pd.Series(tr, index=bars_df.index)
    le = (t > 0) & (t.shift(1) <= 0)
    se = (t < 0) & (t.shift(1) >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
