"""SMA 30 / 200 crossings, 1-hour bars: the SMA 30 crossing over the SMA 200 goes long, under it short, each with a stop and target 40 price units from the signal close (re-expressed as fractions);
reversing.
Port of FMZ strategy #440829 "Gold Cross Dead Cross Quantitative Trading Strategy" (Estrategia de Cruce de Medias Móviles).

FMZ source id: 440829

Source
    https://www.fmz.com/strategy/440829 (PineScript v5, FMZ last modified 2024-02-02 14:46:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-168), SMA 30 / 60 (plotted) / 200; stop and target 40.000 (price units)
    crossover(sma30, sma200) -> entry Buy, strategy.exit(stop = close - 40, limit = close + 40);  crossunder -> entry Sell (mirrored);  held long and cross down -> close Buy;  held short and cross up -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 40-unit distances are price units from the signal close; the port uses fractions
      at the BTC reading near 42000 (0.00095), fixed at the signal and re-based on the fill; the second
      grid value widens them. The opposite cross closes and reverses, as the entries do. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit bracket -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG440829 (5 members, best partner #442336, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440829_sma30_200_cross_unit_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "br_frac": [0.00095, 0.02],
    "fast": [30, 50],
}
DEFAULT_PARAMS = {"br_frac": 0.00095, "fast": 30, "slow": 200}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    lsig = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    ssig = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    b_ = float(p["br_frac"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if hv[i] >= x * (1 + b_) or lv[i] <= x * (1 - b_):
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
    b = float(p["br_frac"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
