"""Dips 1 % under a 30-minute SMA 14, 2-hour bars, long only: the close under 0.99 x the 30-minute SMA (its last value inside the bar) goes long with a stop 20 and a target 120 price units from the signal
close (re-expressed as fractions).
Port of FMZ strategy #442820 "Moving Average Trading Strategy" (Estrategia MA - mejor).

FMZ source id: 442820

Source
    https://www.fmz.com/strategy/442820 (PineScript v5, FMZ last modified 2024-02-26 11:36:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-164), SMA 14 on 30 minutes; 1 % dip; stop 10 x 2, target 60 x 2 price units; size 1
    ma = security("30", sma(close, 14));  close < ma x 0.99 -> entry Long (qty 1), exit(stop = close - 10 x pipValue, limit = close + 60 x pipValue), pipValue = 2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30-minute request from a 2-hour chart is a lower time frame: its value is the last 30-minute
      bar inside the 2-hour bar (as #436765), built from minutes in precompute. Criterion 2: the 20 /
      120-unit distances are price units from the signal close; the port uses fractions of the close at
      the BTC reading of 42000 (0.000476 / 0.002857), re-based on the fill; a new signal while long moves
      the script's levels, which the port does not follow (as #439608). The capital, risk and leverage
      constants are unused; the quantity 1 is sizing. Long only. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; the 30-minute value ends with the bar.
    2 generic: ADAPT, price-unit bracket -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442820_dip_under_30m_sma_unit_bracket_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "dip": [0.99, 0.98],
    "tp_frac": [0.002857, 0.01],
}
DEFAULT_PARAMS = {"dip": 0.99, "tp_frac": 0.002857, "sl_frac": 0.000476, "length_ma": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    b30 = _resample(raw_1m_df, "30min")
    ma = b30["close"].rolling(int(p["length_ma"])).mean()
    last = ma.groupby(b30.index.floor(FREQ)).last()           # the last 30-minute bar inside the 2-hour bar
    bars["ma30"] = last.reindex(bars.index).to_numpy()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    go = (c < bars_df["ma30"] * float(p["dip"])).to_numpy()
    s_, t_ = float(p["sl_frac"]), float(p["tp_frac"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
