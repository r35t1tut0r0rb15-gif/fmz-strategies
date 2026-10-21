"""Polarized Fractal Efficiency state, 3-minute bars: the EMA 5 of the 9-bar PFE above 50 holds a long, under -50 holds a short; reversing; the price-unit constants become fractions of the close.
Port of FMZ strategy #438792 "极化分形效率PFE交易策略Polarized-Fractal-Efficiency-PFE-Trading-Strategy" (PFE (Polarized Fractal Efficiency)).

FMZ source id: 438792

Source
    https://www.fmz.com/strategy/438792 (PineScript v2, FMZ last modified 2024-01-15 14:01:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 202-220), Length 9, EMA 5, bands 50 / -50; reverse off
    PFE = sqrt((close - close[9])^2 + 100);  C2C = sum(sqrt((close - close[1])^2 + 1), 9);  eff = round(+/- PFE / C2C x 100) by the sign of close - close[9];  pos = -1 if ema(eff, 5) < -50, 1 if > 50, else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the constants 100 and 1 inside the roots are squared PRICE units (10 and 1 price
      units), so the index changes with the quote's scale; the port uses (10 x unit x close)^2 and
      (unit x close)^2: 2.4e-05 is the reading (1 on BTC near 42000), 0 the pure efficiency ratio. Pine's
      round is half away from zero. The state is a level, so the entry is sent on every bar of the state.
      reverse is off. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "3min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit constants -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438792_polarized_fractal_efficiency_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "unit": [2.4e-05, 0.0],
    "length": [9, 18],
}
DEFAULT_PARAMS = {"unit": 2.4e-05, "length": 9, "length_ema": 5, "buy_band": 50.0, "sell_band": -50.0,
                  "reverse": False}


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
    u = float(p["unit"]) * c
    mv = c - c.shift(n)
    pfe = np.sqrt(mv ** 2 + (10 * u) ** 2)
    c2c = np.sqrt(c.diff() ** 2 + u ** 2).rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (pfe / c2c * 100).to_numpy()
    eff = np.floor(r + 0.5)
    eff = np.where(mv.to_numpy() > 0, eff, -eff)
    ema = pd.Series(eff, index=c.index).ewm(span=int(p["length_ema"]), adjust=False).mean().to_numpy()
    bb, sb = float(p["buy_band"]), float(p["sell_band"])
    m = len(ema)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = -1.0 if ema[i] < sb else (1.0 if ema[i] > bb else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
