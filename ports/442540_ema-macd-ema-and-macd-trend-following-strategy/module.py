"""Close crossing an EMA 20 with a MACD(12, 26, 9) confirmation, 1-hour bars: the close crossing over the EMA with the MACD above zero or crossing over its signal goes long, the mirror short; a stop and
target 10 price units from the signal close (re-expressed as fractions); reversing.
Port of FMZ strategy #442540 "基于EMA和MACD的趋势跟踪策略EMA-and-MACD-Trend-Following-Strategy" (EMA and MACD Trading Strategy).

FMZ source id: 442540

Source
    https://www.fmz.com/strategy/442540 (PineScript v4, FMZ last modified 2024-02-22 16:28:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-167), EMA 20; MACD 12 / 26 / 9; risk amount 10 ("pips", price units)
    crossover(close, ema) and (macd > 0 or crossover(macd, signal)) -> entry Long, exit(stop = close - 10, limit = close + 10)
    crossunder(close, ema) and (macd < 0 or crossunder(macd, signal)) -> entry Short, exit(stop = close + 10, limit = close - 10)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 10-unit distances are price units from the signal close; the port uses fractions
      of the close at the BTC reading of 42000 (10 / 42000 = 0.000238), re-based on the fill. A new
      same-side signal while held moves the script's levels, which the port does not follow (as
      #439608). Both exits share the id "Exit"; each entry's call re-binds it to the new position.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit bracket -> fractions of the close.
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

NAME = "fmz_442540_ema20_cross_macd_confirm_unit_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_period": [20, 50],
    "risk_frac": [0.000238, 0.0024],
}
DEFAULT_PARAMS = {"ema_period": 20, "risk_frac": 0.000238, "fast": 12, "slow": 26, "signal": 9}


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
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    m_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    m_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    lsig = ((c > e) & (c.shift(1) <= e.shift(1)) & ((macd > 0) | m_up)).to_numpy()
    ssig = ((c < e) & (c.shift(1) >= e.shift(1)) & ((macd < 0) | m_dn)).to_numpy()
    f = float(p["risk_frac"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - f) or hv[i] >= x * (1 + f):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["risk_frac"])
    return {"sl_stop": f, "tp_stop": f}


def portfolio_kwargs(**params):
    return {}
