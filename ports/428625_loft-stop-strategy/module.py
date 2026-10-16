"""Loft stop on a Kalman line, 2-hour bars: a Kalman-smoothed close carries a stop that starts 2 % away
and tightens by 0.005 % each time it ratchets (to at least 0.5 %); the line crossing its stop flips the
side. Each flip opens a position the other way, closed early at a 1.5 % take-profit.
Port of FMZ strategy #428625 "Loft Stop Strategy".

FMZ source id: 428625

Source
    https://www.fmz.com/strategy/428625 (PineScript v5, FMZ last modified 2023-10-07 16:11:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 181-336), gain 1, approach 2 % -> 0.5 % by 0.005, TP 1.5 %, SL 0
    kf: dk = close - kf[1]; kf = kf[1] + dk sqrt(2 g / 10000) + velo; velo += g / 10000 dk
    long side: stop = kf (1 - pct); kept if not higher, else pct -= step (>= min); kf < stop -> short side
    short side mirrors; entry LONG on the first bar of a long phase, SHORT on the first of a short phase
    exit(limit = avg x (1 +- 1.5 %)) (the stop-loss input is 0: no stop)

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The "loft stop" is a signal line on the Kalman value (bar closes), not an order: flips are
      entries (reversals). The take-profit is percent-of-entry: tp_stop 0.015. After a take-profit
      the next entry waits for the next flip (the stopped-out flags), as the house does.
    * The date window is open. Both sides enabled (defaults).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; take-profit fixed at entry.
    2 generic: PASS, percentages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the exit settings quoted in original_sizing.txt.
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

NAME = "fmz_428625_kalman_loft_stop_flip"
FAMILY = "kalman_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_max": [2.0, 4.0],
    "tp": [1.5, 3.0],
}
DEFAULT_PARAMS = {"gain": 1.0, "stop_max": 2.0, "stop_min": 0.5, "down_step": 0.005, "tp": 1.5}


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


def _phases(bars_df, p):
    src = bars_df["close"].to_numpy(dtype=float)
    g = float(p["gain"]) / 10000
    smax, smin, step = float(p["stop_max"]), float(p["stop_min"]), float(p["down_step"])
    m = len(src)
    side = np.ones(m, dtype=bool)
    kf, velo = np.nan, np.nan
    long, prev_long = True, None
    pct = smax
    stop = np.nan
    for i in range(m):
        base = src[i] if np.isnan(kf) else kf
        dk = src[i] - base
        velo = (0.0 if np.isnan(velo) else velo) + g * dk
        kf = base + dk * np.sqrt(g * 2) + velo
        if np.isnan(stop):
            stop = kf - kf * (pct / 100)               # var initial value on the first bar
        if long:
            new = kf - kf * (pct / 100)
            if prev_long is True and new <= stop:
                new = stop
            elif prev_long is True:
                pct = max(pct - step, smin)
            stop = new
            if kf < stop:
                long, pct = False, smax
                stop = kf + kf * (pct / 100)
        else:
            new = kf + kf * (pct / 100)
            if prev_long is False and new >= stop:
                new = stop
            elif prev_long is False:
                pct = max(pct - step, smin)
            stop = new
            if kf > stop:
                long, pct = True, smax
                stop = kf - kf * (pct / 100)
        side[i] = long
        prev_long = long
    return side


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    side = _phases(bars_df, p)
    prev = np.concatenate(([None], side[:-1]))
    le = np.array([s and (q is None or not q) for s, q in zip(side, prev)])
    se = np.array([(not s) and (q is None or q) for s, q in zip(side, prev)])
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"]) / 100}


def portfolio_kwargs(**params):
    return {}
