"""A composite "outlook" index (z-score, Gaussian-sine term, EMA 20 / 50 log ratio, smoothed log magnitude) above 70
goes long, below 30 short; once it crosses 50 against the position, a stop at the latest bar's low (high) ends it,
hourly bars.
Port of FMZ strategy #482771 "基于量子谱分析的多维动量交易策略-Quantum-Spectral-Momentum-Trading-Strategy-with-Multi-Component-Analysis" (Quantum Spectral Crypto Trading).

FMZ source id: 482771

Source
    https://www.fmz.com/strategy/482771 (PineScript v6, FMZ last modified 2025-02-27 17:51:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 111-198), SMA / stdev 50, EMA 20 / 50, weights 20 / 30 / 20 / 10
    z = (close - sma) / stdev; q = exp(-z^2 / 2) (1 + sin(pi z / 2)); e = log(ema20 / ema50)
    lyap = sma(log(max(1e-10, |e + q|)), 50); index = 50 + 20 (q - 1) + 30 e + 20 z + 10 lyap
    index > 70 -> entry long; index < 30 -> entry short
    index < 50 -> exit long (stop = low); index > 50 -> exit short (stop = high), re-issued every such bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit stops sit at the latest bar's low (high) and move bar by bar while the index stays on the far side of
      50; the house bracket is fixed at the fill and cannot carry them. simulate() keeps the resting order (placed
      at a bar's close, active from the next bar, kept once placed) and emits an exit signal on the bar whose low
      (high) reaches it, filled at the next open (one bar after Pine's stop fill). Mark trailing_stop_pending.
    * An exit order placed while its entry is not open is not carried into a later trade (Pine may attach it to the
      next entry); a bar that both reaches a stop and gives a new signal keeps only the new reversal (or only the
      exit when the signal is on the stopped side).
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bar-extreme stops as exit signals (marked).
    2 generic: PASS, z-scores, EMA ratios and bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482771_composite_outlook_index_bar_extreme_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [50, 100],
    "band": [20.0, 10.0],
}
DEFAULT_PARAMS = {"sma_len": 50, "ema_fast": 20, "ema_slow": 50, "w_q": 20.0, "w_e": 30.0, "w_s": 20.0,
                  "w_l": 10.0, "band": 20.0}


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


def _index(c, p):
    n = int(p["sma_len"])
    z = (c - c.rolling(n).mean()) / c.rolling(n).std(ddof=0)
    q = np.exp(-0.5 * z * z) * (1 + np.sin((np.pi / 2) * z))
    e = np.log(c.ewm(span=int(p["ema_fast"]), adjust=False).mean() / c.ewm(span=int(p["ema_slow"]), adjust=False).mean())
    lyap = np.log(np.maximum(1e-10, (e + q).abs())).rolling(n).mean()
    return 50 + p["w_q"] * (q - 1) + p["w_e"] * e + p["w_s"] * z + p["w_l"] * lyap


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx_v = _index(bars_df["close"], p).to_numpy()
    h, lo = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    up, dn = 50 + p["band"], 50 - p["band"]
    m = len(h)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend = 0, 0
    stop_l = stop_s = np.nan
    for i in range(m):
        if pend:
            pos, pend = pend, 0                  # filled at this bar's open: a new trade
            stop_l = stop_s = np.nan
        hit = 0
        if pos == 1 and not np.isnan(stop_l) and lo[i] <= stop_l:
            hit, pos, stop_l = 1, 0, np.nan
        elif pos == -1 and not np.isnan(stop_s) and h[i] >= stop_s:
            hit, pos, stop_s = -1, 0, np.nan
        v = idx_v[i]
        go_long, go_short = v > up, v < dn
        if go_long and pos != 1 and hit != 1 and i + 1 < m:
            le[i], pend = True, 1
        elif go_short and pos != -1 and hit != -1 and i + 1 < m:
            se[i], pend = True, -1
        if hit == 1 and not se[i]:
            lx[i] = True
        if hit == -1 and not le[i]:
            sx[i] = True
        if not pend:
            if pos == 1 and v < 50:
                stop_l = lo[i]
            if pos == -1 and v > 50:
                stop_s = h[i]
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
