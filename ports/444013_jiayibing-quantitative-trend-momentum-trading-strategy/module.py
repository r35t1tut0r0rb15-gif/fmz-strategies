"""Close crossing an SMA 23 outside the Bollinger bands, 2-hour bars: from flat, the cross up above the upper band (20, 2) goes long, the cross down below the lower band short; a 0.5 % stop and a trailing
take-profit that starts 0.5 % in profit; the per-bar close stop is kept pending.
Port of FMZ strategy #444013 "JiaYiBing Quantitative Trend Momentum Trading Strategy" (JiaYiBing (Trend Momentum)).

FMZ source id: 444013

Source
    https://www.fmz.com/strategy/444013 (PineScript v5, FMZ last modified 2024-03-08 15:40:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 184-267), SMA 23 / 50; BB 20 / 2; take profit 0.5 %; stop 0.5 %; trailing on: take-profit step 0.01 %, trailing stop 0.5 %; position 20 % (equity-based quantity); beast mode off
    flat: entry on buy / sell, exit(loss = close x 0.5 % / mintick, trail_price = close x (1 +- 0.5 %), trail_offset = TP x 0.01 % / mintick)
    in position: exit(stop = close x (1 -+ 0.5 %)) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flat-time exit is a stop 0.5 % from the fill and a trail that starts once the price reaches
      the take-profit price (0.5 % from the signal close) and trails 0.01 % behind the best price: the
      house trail {"type": "percent", "pct": 0.0001, "anchor": "high_low", "activate_after": 0.005} with
      sl_stop 0.005 from the fill (stated approximation; mark trailing_stop). The in-position stop is
      re-sent every bar at 0.5 % from that bar's close, a moving level the house stops cannot express:
      kept pending (mark trailing_stop_pending). Entries come only from flat. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. The equity-based
      quantity and cap are sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the flat-time bracket as house stops, the per-bar stop pending.
    2 generic: PASS, SMA crossings beyond the bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based quantity and cap stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop, trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_444013_sma23_cross_outside_band_trail_take_profit"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_ma": [23, 50],
    "stop_pct": [0.005, 0.01],
}
DEFAULT_PARAMS = {"fast_ma": 23, "stop_pct": 0.005, "tp_pct": 0.005, "trail_step": 0.0001, "bb_period": 20,
                  "bb_dev": 2.0}


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
    f = c.rolling(int(p["fast_ma"])).mean()
    n = int(p["bb_period"])
    mid = c.rolling(n).mean()
    dev = float(p["bb_dev"]) * c.rolling(n).std(ddof=0)
    lsig = ((c > f) & (c.shift(1) <= f.shift(1)) & (c > mid + dev)).to_numpy()
    ssig = ((c < f) & (c.shift(1) >= f.shift(1)) & (c < mid - dev)).to_numpy()
    s_, act, step = float(p["stop_pct"]), float(p["tp_pct"]), float(p["trail_step"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, best = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1:
                armed = not np.isnan(best) and best >= x * (1 + act)
                if lv[i] <= x * (1 - s_) or (armed and lv[i] <= best * (1 - step)):
                    pos = 0
                else:
                    best = hv[i] if np.isnan(best) else max(best, hv[i])
            else:
                armed = not np.isnan(best) and best <= x * (1 - act)
                if hv[i] >= x * (1 + s_) or (armed and hv[i] >= best * (1 + step)):
                    pos = 0
                else:
                    best = lv[i] if np.isnan(best) else min(best, lv[i])
        if pos == 0 and i + 1 < m:
            if lsig[i]:
                le[i], pos, entry_i, best = True, 1, i + 1, np.nan
            elif ssig[i]:
                se[i], pos, entry_i, best = True, -1, i + 1, np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"]),
            "trail": {"type": "percent", "pct": float(p["trail_step"]), "anchor": "high_low",
                      "activate_after": float(p["tp_pct"])}}


def portfolio_kwargs(**params):
    return {}
