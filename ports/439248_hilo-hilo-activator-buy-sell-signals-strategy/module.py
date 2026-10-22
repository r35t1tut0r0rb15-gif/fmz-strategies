"""Hilo activator, 10-minute bars: the line is the 8-bar SMA of the previous highs while the close is under the SMA of the previous lows, and the SMA of the lows while the close is over the SMA of the highs; the
close crossing over the line goes long, crossing under goes short; reversing.
Port of FMZ strategy #439248 "Hilo激活器买卖信号策略Hilo-Activator-Buy-Sell-Signals-Strategy" (Hilo Activator com Sinais de Compra e Venda).

FMZ source id: 439248

Source
    https://www.fmz.com/strategy/439248 (PineScript v4, FMZ last modified 2024-01-18 15:56:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-140), period 8; shift 1; EMA off (SMA)
    max = sma(high[1], 8);  min = sma(low[1], 8);  pos = close > max ? -1 : close < min ? 1 : previous pos (0 at the start);  hilo = pos == 1 ? max : min
    crossover(close, hilo) -> entry Buy;  crossunder(close, hilo) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages run on the previous bar's high and low (shift 1). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / activator line crossings.
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

NAME = "fmz_439248_hilo_activator_close_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [8, 13],
    "shift": [1, 2],
}
DEFAULT_PARAMS = {"period": 8, "shift": 1}


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
    n, k = int(p["period"]), int(p["shift"])
    mx = h.shift(k).rolling(n).mean().to_numpy()
    mn = lo.shift(k).rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    hilo = np.full(m, np.nan)
    pos = 0
    for i in range(m):
        if cv[i] > mx[i]:
            pos = -1
        elif cv[i] < mn[i]:
            pos = 1
        hilo[i] = mx[i] if pos == 1 else mn[i]
    hl = pd.Series(hilo, index=c.index)
    up = (c > hl) & (c.shift(1) <= hl.shift(1))
    dn = (c < hl) & (c.shift(1) >= hl.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
