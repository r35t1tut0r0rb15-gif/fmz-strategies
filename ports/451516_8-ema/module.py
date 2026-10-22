"""The EMA 12 against the EMA 169 on completed 8-hour bars, long only: while flat, the EMA 12 above the EMA 169 buys with the balance; while long, the EMA 12 below it sells.
Port of FMZ strategy #451516 "8小时-ema" (8小时-ema (8-hour EMA 12 / 169)).

FMZ source id: 451516

Source
    https://www.fmz.com/strategy/451516 (javascript, FMZ last modified 2024-05-15 21:44:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 26-68), 8-hour records (PERIOD_H1 x 8); talib EMA 12 / 169 (EMA 676 plotted only); buy 0.99 x balance
    new 8-hour bar -> drop the forming bar;  cross = _Cross(ema12, ema169)
    not bought and cross > 0 -> Buy(last, 0.99 x balance / last), bought;  bought and cross < 0 -> Sell(all stocks), not bought

Interpretation choices (rules in SURVEY_README.md)
    * The script acts once per new 8-hour record, on the records up to the last completed bar (the
      forming one is spliced off), and trades at the last price when the new bar opens: the house
      next-open fill. _Cross returns a positive count while the EMA 12 has been above the EMA 169 since
      its last cross and a negative one while below, so the tests are states, not single-bar crosses:
      the first completed bar with the EMA 12 above buys, the first with it below sells. talib's EMA is
      seeded with the SMA of its first n values; the port computes it over the full history (the
      number of records FMZ returns is not stated; SetMaxBarLen is assigned, not called). Spot
      account: Long only. The 0.99 x balance is sizing. FREQ = "8h" from the records' period
      (UTC-aligned 8-hour bars; the header's 4h is only the chart period).

Admission criteria
    1 fits the interface: PASS, completed-bar signals, orders at the next bar's open.
    2 generic: PASS, EMA 12 / 169 trend state.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: the 0.99 x balance quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451516_ema12_169_state_8h_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "8h"  # GetRecords(PERIOD_H1 * 8): 8-hour records
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 21],
    "slow": [169, 100],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 169}


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


def _talib_ema(x, n):
    """talib EMA: SMA seed over the first n values, then alpha 2 / (n + 1)."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    if len(v) >= n:
        a = 2.0 / (n + 1)
        out[n - 1] = v[:n].mean()
        for i in range(n, len(v)):
            out[i] = a * v[i] + (1 - a) * out[i - 1]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = _talib_ema(c, int(p["fast"]))
    s = _talib_ema(c, int(p["slow"]))
    le = f > s
    lx = f < s
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
