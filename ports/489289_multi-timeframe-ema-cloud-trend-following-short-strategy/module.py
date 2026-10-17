"""EMA 21 / 50 cloud cross-downs, short only, with a 1 % / 2 % bracket, 2-hour bars: EMA 21 crossing below EMA 50 goes
short; each trade has a 1 % stop and a 2 % target from the entry price.
Port of FMZ strategy #489289 "多周期指数移动平均云趋势跟踪做空策略-Multi-Timeframe-EMA-Cloud-Trend-Following-Short-Strategy" (Short-Only MTF EMA Cloud Strategy).

FMZ source id: 489289

Source
    https://www.fmz.com/strategy/489289 (PineScript v6, FMZ last modified 2025-04-03 10:55:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 201-241), EMA 21 / 50 on the chart timeframe (resolution blank), SL 1 %, TP 2 %
    short_entry = crossunder(ema21, ema50) -> entry short + exit(stop = avg price x 1.01, limit = avg price x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The resolution input is blank: the chart's own timeframe (no higher timeframe is read).
    * The bracket: as written it is placed on the signal bar from strategy.position_avg_price, which is na while
      flat, so a short opened from flat gets no stop or target until a later cross-down re-issues the exit (the entry
      itself is then ignored). The port applies the bracket from the fill (sl_stop 1 %, tp_stop 2 %; the evident
      intent); stated deviation, decision owed.
    * Short only: Opposite entries cannot occur. Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the
      backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (deviation stated).
    2 generic: PASS, EMAs and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489289_ema_cloud_cross_down_short_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"ma_len1": 21, "ma_len2": 50, "sl_pct": 1.0, "tp_pct": 2.0}


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
    e1 = c.ewm(span=int(p["ma_len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ma_len2"]), adjust=False).mean()
    short_e = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
