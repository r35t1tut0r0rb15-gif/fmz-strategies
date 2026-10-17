"""Twin EMA ribbons with a trade-state engine (JustUncleL template), 1-hour bars: the fast (EMA 5 / 25), slow (EMA 28 / 72)
and fast-minus-slow spreads all widening for two bars goes long from flat (mirror short); a 3 % pull-back of the bar body
from the best body high since entry, or a 1 % pull-back once 3 % was gained, closes it.
Port of FMZ strategy #431272 "多重MA带动量交易策略Multi-Timeframe-Moving-Average-Momentum-Trading-Strategy" ([WAI GUA] / [EOS] 1.0).

FMZ source id: 431272

Source
    https://www.fmz.com/strategy/431272 (PineScript v3, FMZ last modified 2023-11-06 16:04:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 164-629), ribbons EMA 5 / 25 and 28 / 72, Renko body on, trailing 3 %, TP 3 % / trailing profit 1 %
    xup / fup / sup = consecutive bars with the spread positive and widening; buy = xup >= 2 and sup >= 2 and fup >= 2 (first bar)
    tradeState 0 -> 1 on buy == 1 (not right after a close), 0 -> -1 on sell == 1; longCondition = change to 1 -> entry
    high_ = max(open, close), low_ = min(open, close) (Renko option on); last_high = the best high_ while long
    long_ts = low_ <= last_high x 0.97;  long_tp = last_high >= entry close x 1.03 and low_ <= last_high x 0.99
    longClose = (long_tp or long_ts) and not longCondition -> close; tradeState := 0 (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state engine is ported line for line, including the reset of the extremes after a close and
      the one-bar block on a new state right after a close (longClose / shortClose of the previous
      bar). The pull-backs are tested on the bar's body (the Renko option is on by default) and
      closed with strategy.close at the next open: close-checked exits, not stop orders (no mark).
    * The stop loss is off by default; the "opposite trade as a close" option is off; the RSI, PSAR
      and Keltner blocks are not used by the orders. The 2018 start is dropped. States move only
      through flat: Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked trailing exits.
    2 generic: PASS, EMA ribbons and percentage pull-backs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG431272 (2 members, best partner #433073, Jaccard 0.991); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431272_ema_ribbons_state_engine"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ts_pct": [3.0, 1.5],
    "tp_pct": [3.0, 6.0],
}
DEFAULT_PARAMS = {"f1": 5, "f2": 25, "s1": 28, "s2": 72, "ts_pct": 3.0, "tp_pct": 3.0, "ttp_pct": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _count(d, up):
    """Consecutive bars with the spread d positive (negative) and widening, as the source's counters."""
    m = len(d)
    out = np.zeros(m)
    for i in range(1, m):
        ok = (d[i] > 0 and d[i] > d[i - 1]) if up else (d[i] < 0 and d[i] < d[i - 1])
        out[i] = out[i - 1] + 1 if ok else 0
    return out


def _first(cond):
    m = len(cond)
    out = np.zeros(m)
    for i in range(m):
        out[i] = (out[i - 1] + 1 if i and out[i - 1] > 0 else 1) if cond[i] else 0
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    ema = {k: c.ewm(span=int(p[k]), adjust=False).mean().to_numpy() for k in ("f1", "f2", "s1", "s2")}
    fast, slow = (ema["f1"] + ema["f2"]) / 2, (ema["s1"] + ema["s2"]) / 2
    x_d, f_d, s_d = fast - slow, ema["f1"] - ema["f2"], ema["s1"] - ema["s2"]
    buy = _first((_count(x_d, True) >= 2) & (_count(s_d, True) >= 2) & (_count(f_d, True) >= 2))
    sell = _first((_count(x_d, False) >= 2) & (_count(s_d, False) >= 2) & (_count(f_d, False) >= 2))
    hi_ = np.maximum(o.to_numpy(dtype=float), c.to_numpy(dtype=float))
    lo_ = np.minimum(o.to_numpy(dtype=float), c.to_numpy(dtype=float))
    cv = c.to_numpy(dtype=float)
    ts, tp, ttp = float(p["ts_pct"]) / 100, float(p["tp_pct"]) / 100, float(p["ttp_pct"]) / 100
    ttp = min(ttp, tp)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    state, l_close, s_close = 0, False, False
    last_high = last_low = np.nan
    open_l = open_s = 0.0
    for i in range(m):
        prev_state = state
        if state == 0:
            if buy[i] == 1 and not l_close and not s_close:
                state = 1
            elif sell[i] == 1 and not l_close and not s_close:
                state = -1
        long_c = state != prev_state and state == 1
        short_c = state != prev_state and state == -1
        if long_c:
            open_l = cv[i]
        if short_c:
            open_s = cv[i]
        if state == 1:
            last_high = hi_[i] if (np.isnan(last_high) or hi_[i] > last_high) else last_high
        else:
            last_high = np.nan
        if state == -1:
            last_low = lo_[i] if (np.isnan(last_low) or lo_[i] < last_low) else last_low
        else:
            last_low = np.nan
        l_ts = state == 1 and not np.isnan(last_high) and lo_[i] <= last_high * (1 - ts)
        s_ts = state == -1 and not np.isnan(last_low) and hi_[i] >= last_low * (1 + ts)
        l_tp = state == 1 and last_high >= open_l * (1 + tp) and lo_[i] <= last_high * (1 - ttp)
        s_tp = state == -1 and last_low <= open_s * (1 - tp) and hi_[i] >= last_low * (1 + ttp)
        l_close = (l_tp or l_ts) and not long_c
        s_close = (s_tp or s_ts) and not short_c
        if l_close or state != 1:
            last_high = np.nan
        if s_close or state != -1:
            last_low = np.nan
        if l_close or s_close:
            state = 0
        tgt[i] = state
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
