"""SuperTrend (10, 3) direction changes, 5-minute bars: a turn up goes long, a turn down goes short; reversing; each trade has a stop beyond the signal bar's low (high) and a target beyond its high (low) by
fixed price amounts, re-expressed as fractions of the close.
Port of FMZ strategy #438506 "Trend Following Strategy with Stop Loss" (Supertrend Strategy).

FMZ source id: 438506

Source
    https://www.fmz.com/strategy/438506 (PineScript v5, FMZ last modified 2024-01-12 14:55:40).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 158-187), stop amount 300, profit amount 800 (price units); SuperTrend ATR 10, factor 3
    change(direction) < 0 -> entry Long;  > 0 -> entry Short;  in position: exit(stop = valuewhen(signal, low - 300), limit = valuewhen(signal, high + 800)) (shorts mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop and profit amounts are price units; the port adds stop_frac (profit_frac) x
      the close to the signal bar's distance from the close to its low or high: 0.0068 / 0.018 are the
      reading (300 / 800 on BTC near 44000), 0.02 a wider stop. The levels are fixed at the signal bar and
      re-based on the fill (sl_stop / tp_stop shifted one bar inside stops(), as #438054); the exit is sent
      from the first bar close inside the trade: the port starts it at the fill. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The percent-of-equity size is
      sizing. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit stop and profit amounts -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_438506_supertrend_turn_amount_bracket_5m"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.0068, 0.02],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"stop_frac": 0.0068, "factor": 3.0, "profit_frac": 0.018, "atr_period": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's ta.supertrend(factor, atrPeriod): -1 up, 1 down, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return pd.Series(d, index=c.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend_dir(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    ch = d - d.shift(1)
    return ch < 0, ch > 0


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, _ = _signals(bars_df, p)
    on_long = up.to_numpy()
    sf, pf = float(p["stop_frac"]), float(p["profit_frac"])
    sl = np.where(on_long, ((c - lo) / c).to_numpy() + sf, ((h - c) / c).to_numpy() + sf)
    tp = np.where(on_long, ((h - c) / c).to_numpy() + pf, ((c - lo) / c).to_numpy() + pf)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
