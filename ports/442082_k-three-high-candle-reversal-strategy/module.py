"""Three green candles with a modest combined rise, 1-hour bars, long only: after three green bars whose span (lowest open to highest close) is 0.2-0.5 %, go long; the close 1 % above the fill, 0.4 %
under it, or a red bar with a small open profit closes.
Port of FMZ strategy #442082 "三高K线反转策略Three-High-Candle-Reversal-Strategy" (3 high candle test).

FMZ source id: 442082

Source
    https://www.fmz.com/strategy/442082 (PineScript v5, FMZ last modified 2024-02-19 10:51:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-154), qty 1; target 1 % (close test), stop 0.4 % (close test); reduce-risk exit on a red bar with openprofit > 0.47
    three green bars and 0.2 < 100 - min(open[1..3]) / max(close[1..3]) x 100 < 0.5 -> entry Enter Long (qty 1)
    close <= avg 0.996 -> close;  (close[1] < open[1] and openprofit > 0.47) or close >= avg 1.01 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are bar-close tests of the close against the fill price, sent at the next open. With a
      fixed quantity of 1 the openprofit test is a price gain of 0.47 units: as a fraction of the close at
      the BTC 42000 reading, close - fill > 1.119e-05 of the close. The default pyramiding refuses a second
      entry while long. Long only. The qty of 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, openprofit in price units -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442082_three_green_modest_rise_close_tests_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "target": [0.01, 0.02],
    "stop": [0.004, 0.01],
}
DEFAULT_PARAMS = {"target": 0.01, "stop": 0.004, "gain_frac": 1.119e-05, "span_lo": 0.2, "span_hi": 0.5}


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
    o, c = bars_df["open"], bars_df["close"]
    g = c > o
    g1, g2, g3 = g.shift(1, fill_value=False), g.shift(2, fill_value=False), g.shift(3, fill_value=False)
    mo = pd.concat([o.shift(1), o.shift(2), o.shift(3)], axis=1).min(axis=1, skipna=False)
    mc = pd.concat([c.shift(1), c.shift(2), c.shift(3)], axis=1).max(axis=1, skipna=False)
    span = 100 - mo / mc * 100
    go = (g1 & g2 & g3 & (span > float(p["span_lo"])) & (span < float(p["span_hi"]))).to_numpy()
    red1 = (c.shift(1) < o.shift(1)).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    tg, st, gf = float(p["target"]), float(p["stop"]), float(p["gain_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, entry_i = 0, -1
    for i in range(m):
        if held == 1 and i >= entry_i:
            fill = ov[entry_i]
            if (cv[i] <= fill * (1 - st) or (red1[i] and cv[i] - fill > gf * cv[i])
                    or cv[i] >= fill * (1 + tg)):
                lx[i], held = True, 0
                continue
        if held == 0 and go[i] and i + 1 < m:
            le[i], held, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
