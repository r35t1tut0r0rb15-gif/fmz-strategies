"""EMA 20 / 50 crossings, 1-hour bars, long only: the cross up buys; the cross down, or a close 2.5 % under or 4 % over the signal close, sells.
Port of FMZ strategy #471729 "Dual Moving Average Crossover with Dynamic Risk Management Strategy" (Estrategia STX - Medias Móviles con Riesgo Medio).

FMZ source id: 471729

Source
    https://www.fmz.com/strategy/471729 (PineScript v5, FMZ last modified 2024-11-12 17:29:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-140), EMA 20 / 50; stop 2.5 %, target 4 % of the signal close (close tests; the levels persist after the trade)
    crossover(ema20, ema50) -> entry = close, sl = close x 0.975, tp = close x 1.04, entry Compra
    crossunder(ema20, ema50) or close <= sl or close >= tp -> close Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are set on each signal bar and kept after the trade, so they act only on a long held
      into the bar (the close acts only on a held long). The tests are bar-close tests filled at the next
      open. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop and target are close tests.
    2 generic: PASS, EMA crossings with percent close tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471729_ema20_50_cross_pct_close_tests_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
    "sl_pct": [0.025, 0.05],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "sl_pct": 0.025, "tp_pct": 0.04}


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
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    xo = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    xu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sl, tg = 0, np.nan, np.nan
    for i in range(m):
        if xo[i]:
            sl, tg = cv[i] * (1 - sp), cv[i] * (1 + tp)
        out = xu[i] or cv[i] <= sl or cv[i] >= tg
        if xo[i] and pos == 0:
            le[i], pos = True, 1
        elif out and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
