"""Key reversal up longs, 1-hour bars, long only: a bar making a low below the previous low with a higher close starts a long state at that close; the state ends when a bar's low reaches the stop or its high
the target distance from that price (fixed price amounts, re-expressed as fractions); the long is held while the state lasts.
Port of FMZ strategy #440103 "Key Reversal Backtest Strategy" (KRU Backtest).

FMZ source id: 440103

Source
    https://www.fmz.com/strategy/440103 (PineScript v4, FMZ last modified 2024-01-26 16:11:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-165), take profit 20, stop loss 10 (price units, "pip"); look-back 1
    C1 = low < lowest(low[1], 1) and close > close[1];  posprice := C1 ? close : posprice[1];  pos = posprice > 0 ? 1 : 0;  pos 0 -> close_all, pos 1 -> entry Long
    posprice := 0 when low <= posprice - 10, then when high >= posprice + 20 (tested on the same bar, after the orders)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a close test of the bar's own low / high against the signal close, not an order:
      posprice resets on the bar the range reaches it (often the signal bar itself), and the position
      follows the state at the next bar (as written; the mirror of #439036).
    * Criterion 2: the amounts are price units; the port uses fractions of the signal close: 0.00048 /
      0.00024 are the reading (20 / 10 on BTC near 42000), 0.02 / 0.01 a wider pair. Long only. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested state.
    2 generic: ADAPT, price-unit target / stop -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439036 (2 members, best partner #439036, Jaccard 0.653); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440103_key_reversal_up_state"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
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
    ll = lo.shift(1).rolling(int(p["n_length"])).min()
    c1 = ((lo < ll) & (c > c.shift(1))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp_frac"]), float(p["sl_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pp = 0.0
    for i in range(m):
        if c1[i]:
            pp = cv[i]
        tgt[i] = 1 if pp > 0 else 0
        if pp > 0 and lv[i] <= pp * (1 - sl):
            pp = 0.0
        if pp > 0 and hv[i] >= pp * (1 + tp):
            pp = 0.0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
