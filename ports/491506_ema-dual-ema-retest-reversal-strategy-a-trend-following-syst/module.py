"""EMA 200 retests after an EMA 200 / 500 cross, at most two signals a day, with a 0.5 % / 2 % bracket, 2-minute
bars: after EMA 200 crosses above EMA 500, a close within 0.2 % of EMA 200 goes long; after the bearish cross, the
same retest goes short; each trade has a 0.5 % stop and a target four times as far.
Port of FMZ strategy #491506 "双均线回调反转交易策略基于EMA穿越与回测容差的趋势跟踪系统-Dual-EMA-Retest-Reversal-Strategy-A-Trend-Following-System-Based-on-EMA-Crossovers-and-Retest-Tolerance" (200/500 EMA Retest Strategy).

FMZ source id: 491506

Source
    https://www.fmz.com/strategy/491506 (PineScript v6, FMZ last modified 2025-04-21 15:58:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 172-223), EMA 200 / 500, tolerance 0.2 %, SL 0.5 %, RR 4, 2 trades a day
    trend = side of the last EMA 200 / 500 cross;  retest = in trend and |close - ema200| / ema200 <= 0.002
    retest and trades_today < 2 -> entry on the trend side + exit(stop = close x (1 -+ 0.5 %), limit = close x
    (1 +- 2 %)); trades_today += 1 (also when the entry is ignored because the position is already open)
    trades_today = 0 on the first bar of each day (ta.change(time("D")))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day is the chart's exchange day: 00:00 UTC on the author's Binance market (decision owed: broker day?).
    * Every counted retest bar is an entry signal (an entry while already on that side is ignored by Pine and the
      engine alike, but still counts towards the two a day, as written).
    * The bracket is placed with the entry from the signal bar's close: sl_stop 0.5 %, tp_stop 2 % of the fill
      (scalars, re-based on the fill: house rule). As written a later retest bar while in the trade re-places the
      bracket at that bar's close (a moving level): mark trailing_stop_pending; the port keeps the first bracket.
    * The trend flips only on a cross, so a short retest while long reverses (REVERSAL INTENDED); the two retests
      cannot fall on one bar. Stop module: portfolio_kwargs {} (D4). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-placed bracket fixed at entry (mark).
    2 generic: PASS, EMAs and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: day boundary 00:00 UTC (the author's exchange day) for the two-a-day counter; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491506_ema_200_500_retest_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "retest_tolerance": [0.002, 0.001],
    "risk_reward": [4.0, 2.0],
}
DEFAULT_PARAMS = {"ema_fast": 200, "ema_slow": 500, "retest_tolerance": 0.002, "risk_reward": 4.0,
                  "stop_loss": 0.005, "max_trades_per_day": 2}


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
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    bull_x = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
    bear_x = ((ef < es) & (ef.shift(1) >= es.shift(1))).to_numpy()
    near = ((c - ef).abs() / ef <= p["retest_tolerance"]).to_numpy()
    day = bars_df.index.tz_convert("UTC").normalize()
    new_day = np.concatenate(([True], day[1:] != day[:-1]))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_bull = in_bear = False
    count = 0
    for i in range(m):
        if new_day[i]:
            count = 0
        if bull_x[i]:
            in_bull, in_bear = True, False
        if bear_x[i]:
            in_bull, in_bear = False, True
        if in_bull and near[i] and count < p["max_trades_per_day"]:
            le[i] = True
            count += 1
        if in_bear and near[i] and count < p["max_trades_per_day"]:
            se[i] = True
            count += 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"]), "tp_stop": float(p["stop_loss"] * p["risk_reward"])}


def portfolio_kwargs(**params):
    return {}
