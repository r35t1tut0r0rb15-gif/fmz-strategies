"""The close against the 20-close 95 % quantile minus the 20-bar standard deviation, hourly bars, long only: a close over it goes long, a close under it closes.
Port of FMZ strategy #482890 "Multi Band Statistical Trend Analysis Strategy" (Multi-Band Comparison Strategy with Separate Entry/Exit Confirmation).

FMZ source id: 482890

Source
    https://www.fmz.com/strategy/482890 (PineScript v6, FMZ last modified 2025-02-20 16:45:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-252), length 20; quantiles 0.95 / 0.05; Bollinger 1.0 (colour only); entry / exit confirmation 1 bar; 10 % of equity, capital 5000
    quant_upper = sorted(last 20 closes)[round(19 x 0.95)];  trigger = close > quant_upper - stdev(close, 20)
    trigger held entry_confirmBars bars and position <= 0 -> entry Long;  not trigger held exit_confirmBars bars and position > 0 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The percentile is the source's own: the sorted window's element at round((20 - 1) x 0.95), Pine's
      half-up rounding (index 18). The power-law, Bollinger and lower bands only colour the plots. The
      counters are consecutive-bar counts, as written. Long only. The 10 % of equity size and the capital
      are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against a rolling quantile less one standard deviation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_482890_close_vs_q95_20_minus_sd_state_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "upper_quantile": [0.95, 0.9],
}
DEFAULT_PARAMS = {"length": 20, "upper_quantile": 0.95, "entry_confirm": 1, "exit_confirm": 1}


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
    c = bars_df["close"]
    n = int(p["length"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    q = np.full(m, np.nan)
    if m >= n:
        win = np.sort(np.lib.stride_tricks.sliding_window_view(cv, n), axis=1)
        k = int(np.floor((n - 1) * float(p["upper_quantile"]) + 0.5))
        q[n - 1:] = win[:, k]
    trig = (cv > q - c.rolling(n).std(ddof=0).to_numpy())
    ent, ex = int(p["entry_confirm"]), int(p["exit_confirm"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ec = xc = 0
    for i in range(m):
        ec = ec + 1 if trig[i] else 0
        xc = xc + 1 if not trig[i] else 0
        le[i] = ec >= ent
        lx[i] = xc >= ex
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
