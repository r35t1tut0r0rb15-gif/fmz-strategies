"""EMA 200 / 500 trend from the last crossing, 2-minute bars, at most two signals a UTC day: a close within 0.2 % of the EMA 200 in an up-trend goes long, in a down-trend goes short, each with a 0.5 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #491506 "双均线回调反转交易策略基于EMA穿越与回测容差的趋势跟踪系统-Dual-EMA-Retest-Reversal-Strategy-A-Trend-Following-System-Based-on-EMA-Crossovers-and-Retest-Tolerance" (200/500 EMA Retest Strategy).

FMZ source id: 491506

Source
    https://www.fmz.com/strategy/491506 (PineScript v6, FMZ last modified 2025-04-21 15:58:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 168-235), EMA 200 / 500; retest 0.2 %; SL 0.5 %; RR 4; max 2 trades a day; 1 % of equity
    crossover -> bullish trend;  crossunder -> bearish trend;  new day (time("D") changes) -> count := 0
    bullish and |close - ema200| / ema200 <= 0.2 % and count < 2 -> entry Long + exit(stop = close x 0.995, limit = close x 1.02), count += 1;  mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * time("D") on the Binance header changes at 00:00 UTC; the day's signal count (held or not) and the
      trend flags are followed in a loop. The bracket is set on the signal bar and sent as fractions of the
      fill open (a level at or through it is marketable and closed one bar late, as #458256). A second
      same-side signal while held re-sends the bracket; the port keeps the opening levels, mark
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA retests in an EMA-cross trend with a daily signal cap.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 1 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC days (00:00) for the signal count.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491506_ema200_500_trend_retest_daily2_pct_bracket_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "retest_tolerance": [0.002, 0.001],
    "stop_loss_perc": [0.005, 0.01],
}
DEFAULT_PARAMS = {"retest_tolerance": 0.002, "stop_loss_perc": 0.005, "risk_reward_ratio": 4.0,
                  "max_trades_per_day": 2, "ema_fast_length": 200, "ema_slow_length": 500}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow_length"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    near = ((c - f).abs() / f <= float(p["retest_tolerance"])).to_numpy()
    day = np.asarray(c.index.tz_convert("UTC").normalize())
    cap = int(p["max_trades_per_day"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bull = bear = False
    tt = 0
    for i in range(m):
        if i >= 1 and day[i] != day[i - 1]:
            tt = 0
        if up[i]:
            bull, bear = True, False
        if dn[i]:
            bull, bear = False, True
        if bull and near[i] and tt < cap:
            le[i] = True
            tt += 1
        if bear and near[i] and tt < cap:
            se[i] = True
            tt += 1
    q = float(p["stop_loss_perc"])
    t = q * float(p["risk_reward_ratio"])
    lvl = {"l_sl": c * (1 - q), "l_tp": c * (1 + t), "s_sl": c * (1 + q), "s_tp": c * (1 - t)}
    return pd.Series(le, index=c.index), pd.Series(se, index=c.index), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
