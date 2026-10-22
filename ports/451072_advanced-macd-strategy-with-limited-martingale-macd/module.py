"""MACD (15, 30, 9) signal crossings, 1-hour bars, with 1 % close tests: a cross up goes long, a cross down goes short; a close 1 % beyond the fill price either way closes the position; reversing (the
martingale only doubles the quantity).
Port of FMZ strategy #451072 "Advanced-MACD-Strategy-with-Limited-Martingale-基于有限马丁格尔的高级MACD策略" (Advanced MACD Strategy with Limited Martingale).

FMZ source id: 451072

Source
    https://www.fmz.com/strategy/451072 (PineScript v5, FMZ last modified 2024-05-11 17:24:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-150), MACD 15 / 30 / 9; take profit / stop 1 % (close tests against the average price); martingale qty 0.01 doubled up to 3 times; capital 100
    crossover -> entry Long (qty);  crossunder -> entry Short (qty);  close / avg >= 1.01 or <= 0.99 -> close Long;  avg / close >= 1.01 or <= 0.99 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are bar-close tests against the average price (the fill: the next open after the
      signal), filled at the next open; the short's tests are written as avg / close, as written. The
      martingale changes only the quantity: sizing, not ported. A near-duplicate of #453225 in the
      corpus, ported under rule 7. REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits are close tests against the fill.
    2 generic: PASS, MACD crossings with 1 % close tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the martingale quantity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG451072 (3 members, best partner #453225, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451072_macd15_30_cross_one_pct_close_tests_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "band": [0.01, 0.02],
    "fast": [15, 12],
}
DEFAULT_PARAMS = {"band": 0.01, "fast": 15, "slow": 30, "signal": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    xo = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    b = float(p["band"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fp = 0, np.nan
    for i in range(m):
        new = pos
        if xo[i] and new != 1:
            le[i], new = True, 1
        if xu[i] and new != -1:
            se[i], le[i], new = True, False, -1
        if pos == 1 and new == 1 and (cv[i] / fp >= 1 + b or cv[i] / fp <= 1 - b):
            lx[i], new = True, 0
        if pos == -1 and new == -1 and (fp / cv[i] >= 1 + b or fp / cv[i] <= 1 - b):
            sx[i], new = True, 0
        if new != pos and new != 0:
            fp = ov[i + 1] if i + 1 < m else np.nan   # the fill: the next bar's open
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
