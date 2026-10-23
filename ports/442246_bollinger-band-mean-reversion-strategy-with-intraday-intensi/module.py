"""Two-hour bars: the close coming back above the lower Bollinger band (20, 2) with a positive 21-bar intraday intensity sum goes long; the close coming back under the upper band with a negative sum goes short; a long closes above the middle band, 10 bars after a buy signal, or in profit once 4 bars pass without a buy signal (shorts mirrored); reversing.
Port of FMZ strategy #442246 "Bollinger Band Mean Reversion Strategy with Intraday Intensity Index" (Bollinger Bands Strategy with Intraday Intensity Index (SparkyFlary)).

FMZ source id: 442246

Source
    https://www.fmz.com/strategy/442246 (PineScript v4, FMZ last modified 2024-02-20 15:07:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 124-176), BB 20 x 2 (SMA); time stop 10 bars; III 21 on
    buy = close[1] < lower[1] and close > lower and sum((2 close - high - low) x volume / (high - low), 21) > 0;  sell = close > basis or buy[10] or (openprofit > 0 and no buy on this or the last 3 bars)
    short = close[1] > upper[1] and close < upper and iSum < 0;  cover = close < basis or short[10] or (openprofit > 0 and no short on this or the last 3 bars)

Interpretation choices (Pine rules in SURVEY_README.md)
    * openprofit > 0 only asks whether the open position is in profit (close beyond the average fill
      price), which does not depend on its size; it is the open position's profit whichever side, as
      written. buy[10] is any buy signal 10 bars ago. A close acts only on a position the bar's entries
      leave unchanged. Pine's stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ =
      "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger re-entries confirmed by the intraday intensity index, time and profit exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the intraday intensity sum; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442246_bollinger_reentry_iii_time_profit_exit_2h_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "time_stop": [10, 20],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0, "time_stop": 10, "iii_len": 21}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    rng = (h - lo).where(h != lo, 1.0)
    isum = ((2 * c - h - lo) * v / rng).rolling(int(p["iii_len"])).sum()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    buy = ((c.shift(1) < lower.shift(1)) & (c > lower) & (isum > 0)).to_numpy()
    short = ((c.shift(1) > upper.shift(1)) & (c < upper) & (isum < 0)).to_numpy()
    k = int(p["time_stop"])
    m = len(buy)
    ov, cv, bv = o.to_numpy(dtype=float), c.to_numpy(dtype=float), basis.to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, px = 0, np.nan
    for i in range(m):
        if i > 0 and (le[i - 1] or se[i - 1]):
            px = ov[i]                                   # the fill = the average price
        held = tgt
        prof = (held == 1 and cv[i] > px) or (held == -1 and cv[i] < px)
        quiet_b = not buy[max(i - 3, 0):i + 1].any()
        quiet_s = not short[max(i - 3, 0):i + 1].any()
        sell = cv[i] > bv[i] or (i >= k and buy[i - k]) or (prof and quiet_b)
        cover = cv[i] < bv[i] or (i >= k and short[i - k]) or (prof and quiet_s)
        new = tgt
        if buy[i] and new != 1:
            new = 1
        if short[i] and new != -1:
            new = -1
        if new == held:
            if held == 1 and sell:
                new = 0
            elif held == -1 and cover:
                new = 0
        if new != tgt and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif tgt == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
