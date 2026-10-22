"""Close crossing its SMA 20, 1-hour bars: the cross up goes long with a 1 % stop (its target, 3.03 x the close, is out of reach); the cross down goes short, whose target sits on the wrong side of the market,
so the short closes after its first bar; reversing.
Port of FMZ strategy #444011 "Moving Average Breakout Trading Strategy" (Nifty Breakout Strategy).

FMZ source id: 444011

Source
    https://www.fmz.com/strategy/444011 (PineScript v4, FMZ last modified 2024-03-08 15:33:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 153-186), SMA 20; stop 1 %; take profit written as close x (3 +- 0.03)
    crossover(close, sma) -> entry Long, exit(stop = close x 0.99, limit = close x 3.03);  crossunder -> entry Short, exit(stop = close x 1.01, limit = close x 2.97)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The targets multiply the close by 3 +- 0.03, as written: the long's is out of reach (kept as tp
      2.03 of the fill), the short's is a buy limit far above the price, on the wrong side of the
      market, so the short closes at the first open after its fill bar (as #439872: the port closes it
      on that bar's signal). The long stop is a fixed fraction 0.01 of the fill (#437751).
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed at entry; the short's wrong-side target read as a close.
    2 generic: PASS, SMA crossings.
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

NAME = "fmz_444011_sma20_cross_long_stop_short_one_bar"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [20, 50],
    "stop_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"period": 20, "stop_pct": 0.01, "tp_mult": 3.03}


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


def _run(bars_df, p):
    c = bars_df["close"]
    s = c.rolling(int(p["period"])).mean()
    buy = ((c > s) & (c.shift(1) <= s.shift(1))).to_numpy()
    sell = ((c < s) & (c.shift(1) >= s.shift(1))).to_numpy()
    sl, tp = float(p["stop_pct"]), float(p["tp_mult"]) - 1
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se, sx = (np.zeros(m, dtype=bool) for _ in range(3))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - sl) or hv[i] >= ov[entry_i] * (1 + tp)):
            pos = 0
        if i + 1 >= m:
            continue
        if buy[i] and pos != 1:
            le[i], pos, entry_i = True, 1, i + 1
        elif sell[i] and pos != -1:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == -1 and i == entry_i:
            sx[i], pos = True, 0          # the wrong-side short target fills at the next open
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["stop_pct"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp_mult"]) - 1, index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
