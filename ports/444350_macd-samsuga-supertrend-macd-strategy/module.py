"""SuperTrend (factor 1, ATR 7) flips confirmed by the 30-minute MACD (3, 10, 6) histogram, 1-hour bars: a flip to an uptrend with the histogram above zero goes long, a flip to a downtrend with it below
zero goes short; reversing.
Port of FMZ strategy #444350 "基于超级趋势和MACD的风险控制策略Samsuga-SuperTrend-MACD-Strategy" (Samsuga supertrend).

FMZ source id: 444350

Source
    https://www.fmz.com/strategy/444350 (PineScript v5, FMZ last modified 2024-03-11 11:24:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-172), SuperTrend factor 1, ATR 7; MACD 3 / 10 / 6 from the 30-minute time frame (lookahead on); 100 % of equity
    [st, direction] = supertrend(1, 7);  longcondition = direction[1] > direction;  shortCondition = direction[1] < direction
    hist = security("30", macd(close, 3, 10, 6), lookahead_on);  long and hist > 0 -> close Short, entry Long;  else short and hist < 0 -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30-minute histogram requested from a 1-hour chart is the hour's LAST 30-minute bar (a lower
      time frame returns its last bar inside the chart bar; lookahead does not change it, as #436765),
      so it ends with the hourly bar. The 30-minute bars are left-labelled from the minutes, gaps kept.
      ta.supertrend's direction is -1 in an uptrend, so direction[1] > direction is a flip up. A close
      and the opposite entry on one bar is one reversal. REVERSAL INTENDED. The 100 % of equity size is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 30-minute values end with the hourly bar.
    2 generic: PASS, SuperTrend flips with a MACD histogram filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored.
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

NAME = "fmz_444350_supertrend_flip_30m_macd_hist_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [1.0, 3.0],
    "atr_period": [7, 14],
}
DEFAULT_PARAMS = {"factor": 1.0, "atr_period": 7, "fast": 3, "slow": 10, "signal": 6}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    m30 = _resample(raw_1m_df, "30min")
    c = m30["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    last = hist.groupby(m30.index.floor("1h")).last()      # the hour's last 30-minute bar
    bars["hist30"] = last.reindex(bars.index).to_numpy()
    return bars


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's supertrend(factor, atrPeriod): -1 uptrend, 1 downtrend, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    d = np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
            continue
        if i == 0 or np.isnan(atr[i - 1]):
            up_dir = False
        elif st[i - 1] == ub[i - 1]:
            up_dir = cv[i] > ub[i]
        else:
            up_dir = not (cv[i] < lb[i])
        st[i] = lb[i] if up_dir else ub[i]
        d[i] = -1.0 if up_dir else 1.0
    return pd.Series(d, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend_dir(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    d1 = d.shift(1)
    hist = bars_df["hist30"]
    lc = d1 > d
    sc = d1 < d
    le = lc & (hist > 0)
    se = ~lc & sc & (hist < 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
