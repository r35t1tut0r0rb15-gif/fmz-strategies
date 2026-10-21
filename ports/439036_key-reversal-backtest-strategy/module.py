"""Key reversal down shorts, 3-hour bars, short only: a bar making a high above the previous high with a lower close starts a short state at that close; the state ends when a bar's low reaches the target or
its high the stop distance from that price (fixed price amounts, re-expressed as fractions); the short is held while the state lasts.
Port of FMZ strategy #439036 "Key Reversal Backtest Strategy" (KRD Backtest).

FMZ source id: 439036

Source
    https://www.fmz.com/strategy/439036 (PineScript v4, FMZ last modified 2024-01-17 10:56:52).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 201-217), take profit 20, stop loss 10 (price units, "pip"); look-back 1
    C1 = high > highest(high[1], 1) and close < close[1];  posprice := C1 ? close : posprice[1];  pos = posprice > 0 ? -1 : 0;  pos 0 -> close_all, pos -1 -> entry Short
    posprice := 0 when low <= posprice - 20, then when high >= posprice + 10 (tested on the same bar, after the orders)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a close test of the bar's own low / high against the signal close, not an order:
      posprice resets on the bar the range reaches it (often the signal bar itself), and the position
      follows the state at the next bar (as written).
    * Criterion 2: the amounts are price units; the port uses fractions of the signal close: 0.00048 /
      0.00024 are the reading (20 / 10 on BTC near 42000), 0.02 / 0.01 a wider pair. Short only: Opposite
      entries cannot occur. No sizing code. FREQ = "3h" from the backtest header (bars on UTC multiples of
      3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested state.
    2 generic: ADAPT, price-unit target / stop -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439036 (2 members, best partner #440103, Jaccard 0.653); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439036_key_reversal_down_state"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_frac": [0.00048, 0.02],
    "sl_frac": [0.00024, 0.01],
}
DEFAULT_PARAMS = {"tp_frac": 0.00048, "sl_frac": 0.00024, "n_length": 1}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hh = h.shift(1).rolling(int(p["n_length"])).max()
    c1 = ((h > hh) & (c < c.shift(1))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp_frac"]), float(p["sl_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pp = 0.0
    for i in range(m):
        if c1[i]:
            pp = cv[i]
        tgt[i] = -1 if pp > 0 else 0
        if pp > 0 and lv[i] <= pp * (1 - tp):
            pp = 0.0
        if pp > 0 and hv[i] >= pp * (1 + sl):
            pp = 0.0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix)


def portfolio_kwargs(**params):
    return {}
