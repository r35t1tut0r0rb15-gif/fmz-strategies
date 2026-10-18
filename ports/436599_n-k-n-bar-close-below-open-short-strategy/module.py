"""Short after a run of down closes, 30-minute bars, short only: after 4 or more consecutive bars whose close was at or under their open, the strategy is short from that close; it stays short until a price-unit take profit
(20) or stop (10) from the last run close is touched, and exits one bar after the touch.
Port of FMZ strategy #436599 "连续N根K线收阴策略N-Bar-Close-Below-Open-Short-Strategy" (N Bars Down).

FMZ source id: 436599

Source
    https://www.fmz.com/strategy/436599 (PineScript v4, FMZ last modified 2023-12-26 10:29:12).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 135-153), nLength 4, take profit 20, stop loss 10 (price units)
    nCounter = close[1] <= open[1] ? nCounter[1] + 1 : 0;  C2 = nCounter >= nLength;  posprice = C2 ? close : posprice[1];  pos = posprice > 0 ? -1 : 0;  pos == 0 -> close_all;  pos == -1 -> entry Short
    posprice = 0 when low <= posprice - 20;  posprice = 0 when high >= posprice + 10

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the take profit and stop are price units (20 and 10 "pip") tested against the last
      run close; they are re-expressed as fractions of that close, 20 pips and 10 pips of a 5-digit
      currency pair (0.0018 / 0.0009); the stop is half the target. The state machine is a set of
      bar-close tests on the bar's low and high, so it stays signals (the exit comes one bar after the
      touch, as written). While the run continues the reference close is re-set every bar. Short only.
      FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> fractions of the reference close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the take profit and stop inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434674 (2 members, best partner #434674, Jaccard 0.660); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436599_n_bars_down_short"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_length": [4, 3],
    "tp_frac": [0.0018, 0.005],
}
DEFAULT_PARAMS = {"n_length": 4, "tp_frac": 0.0018, "sl_ratio": 0.5}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n_len = int(p["n_length"])
    tp, sl = float(p["tp_frac"]), float(p["tp_frac"]) * float(p["sl_ratio"])
    m = len(c)
    short_state = np.zeros(m, dtype=bool)
    counter = 0
    posprice = 0.0
    for i in range(m):
        if i > 0 and c[i - 1] <= o[i - 1]:
            counter += 1
        elif i > 0 and c[i - 1] > o[i - 1]:
            counter = 0
        if counter >= n_len:
            posprice = c[i]
        short_state[i] = posprice > 0
        if posprice > 0 and lo[i] <= posprice * (1.0 - tp):
            posprice = 0.0
        if posprice > 0 and h[i] >= posprice * (1.0 + sl):
            posprice = 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(short_state, index=ix), pd.Series(~short_state, index=ix)


def portfolio_kwargs(**params):
    return {}
