"""Timed EMA-side trades inside a 10:30-15:00 UTC window, 3-minute bars: every 30 minutes the EMA 5 / 40 side opens a "main" long or short, and once after each main trade an EMA 5 / 10 crossing (or 29 minutes) opens the opposite side; reversing.
Port of FMZ strategy #477951 "自适应双向EMA趋势交易系统与反向交易优化策略-Adaptive-Dual-Direction-EMA-Trend-Trading-System-with-Reverse-Trade-Optimization-Strategy" (SPX EMA Strategy with Opposite Trades).

FMZ source id: 477951

Source
    https://www.fmz.com/strategy/477951 (PineScript v5, FMZ last modified 2025-01-10 15:24:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-178), interval 30 min, opposite delay 1 min; window 10:30-15:00 (exchange time); main EMA 5 / 40, opposite EMA 5 / 10
    in the window and 30 min since the last main trade: ema5 > ema40 -> entry Main Long (last long, opposite reset, time stored), else ema5 < ema40 -> entry Main Short
    in the window and no opposite yet: 29 min since the last main trade or crossover / crossunder(ema5, ema10) -> last main long ? entry Opposite Short : entry Opposite Long; opposite done

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the timers on the bar open times in UTC (the exchange time of the header's market),
      with no DST. The opposite test runs on the same bar after a main trade, so a crossing on that bar
      replaces the main entry (the later call wins, #437773); with 3-minute bars the 29-minute test falls
      on the bar where the next main trade fires first, so opposite trades come from the crossings. Before
      the first main trade the opposite side is long (na tests false). The entries reverse; nothing else
      closes. REVERSAL INTENDED. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, timed EMA-side trades with opposite crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 10:30-15:00 by UTC bar open time (fixed UTC, no DST).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477951_timed_ema5_40_side_opposite_ema5_10_cross_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "interval_min": [30, 60],
    "main_long": [40, 20],
}
DEFAULT_PARAMS = {"interval_min": 30, "main_long": 40, "main_short": 5, "opp_short": 5, "opp_long": 10,
                  "delay_min": 1, "start_min": 630, "stop_min": 900}


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


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ms, ml = _ema(c, p["main_short"]), _ema(c, p["main_long"])
    os_, ol = _ema(c, p["opp_short"]), _ema(c, p["opp_long"])
    xo = ((os_ > ol) & (os_.shift(1) <= ol.shift(1))) | ((os_ < ol) & (os_.shift(1) >= ol.shift(1)))
    t = bars_df.index.tz_convert("UTC")
    mins = np.asarray(t.hour * 60 + t.minute)
    tmin = np.asarray((t - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(minutes=1), dtype=float)
    inwin = (mins >= int(p["start_min"])) & (mins <= int(p["stop_min"]))
    up, dn, cross = (ms > ml).to_numpy(), (ms < ml).to_numpy(), xo.to_numpy()
    iv, dl = float(p["interval_min"]), float(p["delay_min"])
    m = len(mins)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_t, last_long, opp_done = np.nan, None, False
    for i in range(m):
        d = 0
        if inwin[i] and (np.isnan(last_t) or tmin[i] - last_t >= iv):
            if up[i]:
                d, last_long, opp_done, last_t = 1, True, False, tmin[i]
            elif dn[i]:
                d, last_long, opp_done, last_t = -1, False, False, tmin[i]
        if inwin[i] and not opp_done:
            late = (not np.isnan(last_t)) and tmin[i] - last_t >= iv - dl
            if late or cross[i]:
                d = -1 if last_long is True else 1
                opp_done = True
        if d == 1:
            le[i] = True
        elif d == -1:
            se[i] = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
