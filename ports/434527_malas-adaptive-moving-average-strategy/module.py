"""Ehlers MAMA / FAMA in this author's transcription, broker days: long while FAMA is under MAMA, short while it is above;
always in the market once the lines differ.
Port of FMZ strategy #434527 "Malas Adaptive Moving Average Strategy" (自适应移动平均的MESA系统 (MESA adaptive moving average system)).

FMZ source id: 434527

Source
    https://www.fmz.com/strategy/434527 (PineScript v4, FMZ last modified 2023-12-07 11:08:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-249), fast limit 0.5, slow limit 0.05; price hl2; calculation from bar_index 6
    Hilbert-transform period and phase from smoothed hl2 (this script's own lines, incl. Im = I2 Q2[1] + Q2 I2[1]);  alpha = max(0.5 / max(phase[1] - phase, 1), 0.05)
    MAMA = alpha price + (1 - alpha) MAMA[1];  FAMA = .5 alpha MAMA + (1 - .5 alpha) FAMA[1];  FAMA < MAMA -> entry long;  FAMA > MAMA -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Transcribed line by line, as written: every variable restarts at 0 on each bar and is set
      only from bar_index 6 on (so a period without a phase reading is 0 before the clamps, and a
      phase without I1 is 0); the "+" in Im is kept (Ehlers' original has "-"). atan is the
      one-argument arctangent.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive averages of hl2.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434527_mesa_mama_fama_side"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_limit": [0.5, 0.25],
    "slow_limit": [0.05, 0.02],
}
DEFAULT_PARAMS = {"fast_limit": 0.5, "slow_limit": 0.05}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _mesa(price, fl, sl):
    m = len(price)
    z = lambda: np.zeros(m)  # noqa: E731
    sm, det, q1, i1, ji, jq, i2, q2, re, im, per, ph, mama, fama = (z() for _ in range(14))
    g = lambda a, j: a[j] if j >= 0 else 0.0  # noqa: E731
    k = lambda a, j: .0962 * g(a, j) + .5769 * g(a, j - 2) - .5769 * g(a, j - 4) - .0962 * g(a, j - 6)  # noqa: E731
    for t in range(6, m):
        sm[t] = (4 * price[t] + 3 * price[t - 1] + 2 * price[t - 2] + price[t - 3]) / 10
        f = .075 * per[t - 1] + .54
        det[t] = k(sm, t) * f
        q1[t] = k(det, t) * f
        i1[t] = det[t - 3]
        ji[t] = k(i1, t) * f
        jq[t] = k(q1, t) * f
        a2, b2 = i1[t] - jq[t], q1[t] + ji[t]
        i2[t] = .2 * a2 + .8 * i2[t - 1]
        q2[t] = .2 * b2 + .8 * q2[t - 1]
        r_ = i2[t] * i2[t - 1] + q2[t] * q2[t - 1]
        m_ = i2[t] * q2[t - 1] + q2[t] * i2[t - 1]
        re[t] = .2 * r_ + .8 * re[t - 1]
        im[t] = .2 * m_ + .8 * im[t - 1]
        pr = 0.0
        if im[t] != 0 and re[t] != 0:
            pr = 2 * np.pi / np.arctan(im[t] / re[t])
        if pr > 1.5 * per[t - 1]:
            pr = 1.5 * per[t - 1]
        if pr < .67 * per[t - 1]:
            pr = .67 * per[t - 1]
        if pr < 6:
            pr = 6.0
        if pr > 50:
            pr = 50.0
        per[t] = .2 * pr + .8 * per[t - 1]
        if i1[t] != 0:
            ph[t] = (180 / np.pi) * np.arctan(q1[t] / i1[t])
        dp = ph[t - 1] - ph[t]
        if dp < 1:
            dp = 1.0
        al = fl / dp
        if al < sl:
            al = sl
        mama[t] = al * price[t] + (1 - al) * mama[t - 1]
        fama[t] = .5 * al * mama[t] + (1 - .5 * al) * fama[t - 1]
    return mama, fama


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    price = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    mama, fama = _mesa(price, float(p["fast_limit"]), float(p["slow_limit"]))
    m = len(price)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for t in range(6, m):
        if fama[t] < mama[t]:
            q = 1
        elif fama[t] > mama[t]:
            q = -1
        tgt[t] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
