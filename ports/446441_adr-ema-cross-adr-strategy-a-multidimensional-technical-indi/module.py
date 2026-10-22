"""EMA 10 / 50 crossings with a minimum average range, 2-hour bars, with a bracket from the signal bar: a cross up goes long with the stop at the 10-bar average low and a target twice that distance above,
a cross down goes short mirrored (average high); reversing.
Port of FMZ strategy #446441 "ADR均线交叉策略-融合多维度技术指标和严格止盈止损的交易方法EMA-Cross-ADR-Strategy-A-Multidimensional-Technical-Indicator-Based-Trading-Method-with-Strict-Risk-Management" (EMA Cross ADR Strategy with Stats).

FMZ source id: 446441

Source
    https://www.fmz.com/strategy/446441 (PineScript v5, FMZ last modified 2024-03-28 16:46:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-305), EMA 10 / 50; ADR = sma(tr, 14) > 10; risk / reward 2; stop lookback 10; break-even 1.0 / 1.0; close at 15:59; daily loss limit -2000 (tracked, unused)
    crossover(ema10, ema50) and adr > 10 -> entry Long, exit(stop = sma(low, 10), limit = close + 2 (close - sma(low, 10)));  short mirrored with sma(high, 10)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ADR floor of 10 price units is a fraction of the close, 0.000238 (10 against BTC
      near 42000). The bracket is set on the signal bar: sl_stop = (close - average low) / close and
      tp_stop = 2 sl_stop (short: the average high), shifted one bar inside stops() and re-based on the
      fill; a signal whose stop sits at or beyond the close places no trade. The break-even step only
      changes a local variable and the exit is re-sent only on a new signal, so it never acts; a
      repeated signal inside the trade re-issues the levels: not expressible (mark
      trailing_stop_pending). The 15:59 close never fires on 2-hour bars; the entry flags are reset on
      the signal bar itself (still flat), so they never block. The daily loss is tracked, never used.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar (re-sent levels marked).
    2 generic: PASS, EMA crossings with a range floor, swing-average bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 15:59 close never fires on 2-hour bars).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446441_ema10_50_cross_adr_floor_avg_swing_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 1.5],
    "lookback": [10, 20],
}
DEFAULT_PARAMS = {"rr": 2.0, "lookback": 10, "fast": 10, "slow": 50, "adr_len": 14, "adr_frac": 0.000238}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    adr = tr.rolling(int(p["adr_len"])).mean()
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    ok = adr > float(p["adr_frac"]) * c
    n = int(p["lookback"])
    sl_l = (c - lo.rolling(n).mean()) / c
    sl_s = (h.rolling(n).mean() - c) / c
    le = (f > s) & (f.shift(1) <= s.shift(1)) & ok & (sl_l > 0)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & ok & (sl_s > 0)
    sl = sl_l.where(le, sl_s.where(se))
    return le, se, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": (sl * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
