"""Broker days, long only: with every multi-timeframe filter switched off the buy condition is always true, so the tradeState engine goes long whenever it is flat; a bar whose running high since the signal bar reaches the signal close + 1 %, or whose low reaches the signal close - 3 %, closes it; it re-enters two bars later.
Port of FMZ strategy #439199 "Multi Timeframe Trend Tracking Strategy" (Intellitrader - Buy - BACKTESTER).

FMZ source id: 439199

Source
    https://www.fmz.com/strategy/439199 (PineScript v3, FMZ last modified 2024-01-18 12:01:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 285-1131), all RSI / stochastic / CCI / percent-change filters off; take profit 1 %, trailing profit 0, stop loss 3 %, trailing stop off; LongsOnly
    bool_1m := rsi7_1m_logic and ... (all true);  if not rsi7_Use_1m and ... : bool_1m = false (a new local);  buy = bool_1m and ... and bool_1d and pc_logic
    tradeState := INACTIVE and buy and not longClose ? ACTIVELONG : ...;  longCondition = change(tradeState) and tradeState == ACTIVELONG;  longClose := (long_tp or long_sl) and not longCondition;  entry Long / close Long;  if longClose: tradeState := INACTIVE

Interpretation choices (Pine rules in SURVEY_README.md)
    * In Pine v3 "bool_1m = false" inside the if block declares a new local variable, so the global
      bool_* keep the value true and buy is true on every bar (weird case): the 1-minute .. 1-day
      security() reads feed nothing. The engine as written: the reference price is the signal bar's
      close; the running high includes the signal bar (before the fill: weird case); trailing profit 0
      makes the take-profit a test of that running high against the close + 1 %; the stop is the bar's
      low against the close - 3 %; a close is never on the signal bar; after a close the engine waits one
      bar (longClose[1] blocks it) and re-enters on the next. The first bar of the data cannot enter
      (change() is na there). The S/R fractal lines only plot: volume is not used. Long only. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits at the next open after a bar that reached the levels.
    2 generic: PASS, always-in long with signal-close take profit and stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439199_intellitrader_always_buy_tp1_sl3_engine_long_only"
FAMILY = "always_long_bracket"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp": [0.01, 0.02],
    "sl": [0.03, 0.05],
}
DEFAULT_PARAMS = {"tp": 0.01, "sl": 0.03}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state, close_prev, ref = 0, False, 0.0
    run_h = np.nan
    for i in range(m):
        prev_state = state
        if state == 0 and not close_prev:
            state = 1
        long_cond = i > 0 and state == 1 and prev_state != 1
        if long_cond:
            ref = cv[i]
        if state == 1:
            run_h = hv[i] if np.isnan(run_h) or hv[i] > run_h else run_h
            hit_tp = run_h >= ref * (1 + tp)
            hit_sl = lv[i] <= ref * (1 - sl)
        else:
            run_h, hit_tp, hit_sl = np.nan, False, False
        closing = (hit_tp or hit_sl) and not long_cond
        le[i], lx[i] = long_cond, closing
        if closing:
            state, run_h = 0, np.nan
        close_prev = closing
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
