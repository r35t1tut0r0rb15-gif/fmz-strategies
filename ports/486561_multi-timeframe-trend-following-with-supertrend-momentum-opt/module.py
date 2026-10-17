"""EMA 200 side with SuperTrend (10, 3) direction, first bar of each agreement, with a SuperTrend stop and a 2 R target,
1-hour bars: the first bar closing above EMA 200 in a SuperTrend up-trend goes long with the stop at the SuperTrend
line and a target twice as far; the first bar below EMA 200 in a down-trend goes short likewise.
Port of FMZ strategy #486561 "多时间框架趋势跟踪与超级趋势动量优化策略-Multi-Timeframe-Trend-Following-with-Supertrend-Momentum-Optimization-Strategy" (1H EMA 200 + 15M Supertrend Strategy ).

FMZ source id: 486561

Source
    https://www.fmz.com/strategy/486561 (PineScript v6, FMZ last modified 2025-03-14 09:17:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 186-226), SuperTrend 10 / 3, EMA 200 via request.security("60")
    buySignal = close > ema200 (60) and direction < 0;  on its first bar: close_all if in a position, SL = supertrend,
    TP = close + 2 x (close - SL), entry long (sellSignal mirrored)
    in a position: exit(stop = SL, limit = TP) every bar (the levels change only on a new signal)

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(syminfo.tickerid, "60", ...) on the 1-hour header chart is the bar's own value (house rule).
      "15M" in the title is a label.
    * The bracket is fixed at the signal bar, picked by the signal's side: sl_stop = |close - supertrend| / close,
      tp_stop = 2 x that, shifted one bar inside stops() and re-based on the fill (house rule).
    * close_all + entry is the reversal (REVERSAL INTENDED). A new same-side signal edge while held (close_all and
      re-entry) re-places the bracket: mark trailing_stop_pending; the port keeps the entry's bracket.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, an EMA and SuperTrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_486561_ema200_supertrend_edge_bracket"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "atr_period": [10, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 10, "ema_len": 200, "rr": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pine_supertrend(bars_df, factor, n):
    """ta.supertrend: (line, direction), direction 1 = down-trend, -1 = up-trend; 0 / na before the ATR exists."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    d_out = np.zeros(m, dtype=np.int8)
    st_out = np.full(m, np.nan)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        prev_st = lw if d == -1 else up
        pu, pl = up, lw
        d_out[i], st_out[i] = d, prev_st
    return st_out, d_out


def _signals(bars_df, p):
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    st, d = _pine_supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))
    buy = (c > ema).to_numpy() & (d < 0)
    sell = (c < ema).to_numpy() & (d > 0)
    buy_e = buy & ~np.concatenate(([False], buy[:-1]))
    sell_e = sell & ~np.concatenate(([False], sell[:-1]))
    return pd.Series(buy_e, index=c.index), pd.Series(sell_e, index=c.index), pd.Series(st, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, st = _signals(bars_df, p)
    c = bars_df["close"]
    sl = ((c - st).abs() / c).where(long_e | short_e).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
