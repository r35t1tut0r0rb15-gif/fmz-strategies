"""SuperTrend 3 / 10 direction with the close against the EMA 200, hourly bars: the first bar of an up-trend above the EMA goes long with the SuperTrend line as stop and a 2R target, the first bar of a down-trend below it goes short with the mirror; reversing.
Port of FMZ strategy #486561 "Multi Timeframe Trend Following with Supertrend Momentum Optimization Strategy" (1H EMA 200 + 15M Supertrend Strategy).

FMZ source id: 486561

Source
    https://www.fmz.com/strategy/486561 (PineScript v6, FMZ last modified 2025-03-14 09:17:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-232), SuperTrend factor 3, ATR 10; EMA 200 via security("60") on the hourly chart; target 2R; 10 % of equity
    buy = close > ema200 and direction < 0;  buy and not buy[1] -> close_all, stop := supertrend, tp := close + 2 (close - stop), entry Buy
    sell = close < ema200 and direction > 0;  sell and not sell[1] -> close_all, stop := supertrend, tp := close - 2 (stop - close), entry Sell
    long -> exit(stop, limit);  short -> exit(stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("60") on the hourly header chart is the chart's own EMA 200 and close. The levels are stored
      at the signal and re-sent every bar unchanged; they are sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A new same-side signal while
      held closes and re-opens the trade with new levels (close_all then entry); the port keeps the first
      trade and marks the re-sent levels trailing_stop_pending (as #434428). An entry on the other side
      reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size
      is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; SuperTrend stop and 2R target as fractions of the fill.
    2 generic: PASS, SuperTrend turns on the EMA 200 side.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_486561_supertrend3_10_turn_ema200_side_line_stop_2r_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "atr_period": [10, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 10, "ema_length": 200, "rr": 2.0}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def _signals(bars_df, p):
    c = bars_df["close"]
    st, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    buy = (c > e) & (d < 0)
    sell = (c < e) & (d > 0)
    le = buy & ~buy.shift(1, fill_value=False)
    se = sell & ~sell.shift(1, fill_value=False)
    rr = float(p["rr"])
    lvl = {"l_sl": st, "l_tp": c + rr * (c - st), "s_sl": st, "s_tp": c - rr * (st - c)}
    return le & ~se, se, lvl


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
