"""Bollinger 20 / 2 breakouts gated by an "outside" flag, 2-hour bars: the flag is set when the close is 3.5 % or more from the basis and cleared when a close is back inside the bands; with the flag clear, a close above the upper band goes long and a close below the lower band goes short; reversing.
Port of FMZ strategy #477583 "Mean Reversion Bollinger Bands Trading Strategy with Rational Return Signal" (Estratégia com Bandas de Bollinger e Sinal de Retorno).

FMZ source id: 477583

Source
    https://www.fmz.com/strategy/477583 (PineScript v5, FMZ last modified 2025-01-06 15:33:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-175), BB 20 / 2; distance threshold 3.5 %; 200 % of equity
    |close - basis| / basis >= 3.5 % -> is_outside := true;  is_outside and lower <= close <= upper -> is_outside := false
    not is_outside and close > upper -> entry Buy;  not is_outside and close < lower -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop keeps the flag as written: it is set and cleared in that order on each bar, so a close 3.5 %
      away but inside the bands clears it on the same bar. The entries are states and repeat; a repeat on
      the held side is ignored. REVERSAL INTENDED. The 200 % of equity size is sizing. FREQ = "2h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts gated by a distance flag.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_477583_bb20_break_distance_flag_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "threshold": [0.035, 0.05],
}
DEFAULT_PARAMS = {"length": 20, "threshold": 0.035, "mult": 2.0}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    trig = ((c - basis).abs() / basis >= float(p["threshold"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    out = np.zeros(m, dtype=bool)
    flag = False
    for i in range(m):
        if trig[i]:
            flag = True
        if flag and cv[i] <= up[i] and cv[i] >= dn[i]:
            flag = False
        out[i] = flag
    clear = pd.Series(~out, index=c.index)
    false = pd.Series(False, index=c.index)
    return clear & (c > basis + dev), false, clear & (c < basis - dev), false.copy()


def portfolio_kwargs(**params):
    return {}
