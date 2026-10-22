"""Williams %R 21 re-entries, 4-hour bars: %R crossing back over -80 goes long, back under -20 goes short; a 60-tick stop and target (0.015 ATR at the 4-hour reading); reversing.
Port of FMZ strategy #453661 "Williams-R-动态调整止盈止损策略-Williams-R-Dynamic-TP-SL-Adjustment-Strategy" (Williams %R Strategy defined buy/sell criteria with TP / SL).

FMZ source id: 453661

Source
    https://www.fmz.com/strategy/453661 (PineScript v5, FMZ last modified 2024-06-07 15:52:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-158), %R 21 (its EMA 13 plotted only); levels -80 / -20; TP / SL 60 ticks; top-of-hour window +- 10 min; direction Both
    crossover(%R, -80) and top-of-hour window -> entry Buy;  crossunder(%R, -20) and window -> entry Sell;  open trades -> exit(profit = 60, loss = 60) ticks

Interpretation choices (Pine rules in SURVEY_README.md)
    * The minute window around the top of the hour always holds on 4-hour bars (their minute is 0);
      the specific-hours filter is off. The 60-tick distances are 6 at the 0.1 tick, ported as ATR
      multiples at the 4-hour reading (~400): 0.015 ATR 14, from the bar before the fill, active from
      the fill bar (#440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 4-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "4h" from the backtest header
      (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, %R re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: top-of-hour window always true on 4-hour bars.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_453661_williams_r_reentry_tick_bracket_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [21, 14],
    "k_atr": [0.015, 1.0],
}
DEFAULT_PARAMS = {"length": 21, "k_atr": 0.015, "atr_len": 14, "buy_lvl": -80.0, "sell_lvl": -20.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    w = 100 * (c - hh) / (hh - ll)
    b, s = float(p["buy_lvl"]), float(p["sell_lvl"])
    le = (w > b) & (w.shift(1) <= b)
    se = (w < s) & (w.shift(1) >= s)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
