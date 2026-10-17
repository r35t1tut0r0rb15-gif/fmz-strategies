"""EMA 13 / 21 crosses on the right side of SMA 120 (or SMA 120 crosses after five bars clear of it), entered from
flat with a stop at the fast EMA (at least 0.2 %) and a 5 R target, closed once the trade is 0.8 % up or on the
opposite EMA cross, 1-minute bars.
Port of FMZ strategy #483509 "动态均线交叉趋势跟踪组合策略-Dynamic-Moving-Average-Crossover-Trend-Following-Strategy" (交易策略（自定义EMA/SMA参数）).

FMZ source id: 483509

Source
    https://www.fmz.com/strategy/483509 (PineScript v5, FMZ last modified 2025-02-24 09:46:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 94-180), SMA 120, EMA 13 / 21
    long = (close > sma and crossover(ema13, ema21)) or (crossover(close, sma) and low[1..5] > sma[1..5])
    from flat: stopPerc = max(0.002, (close - ema13) / close); exit(stop = close x (1 - stopPerc),
    limit = close x (1 + 5 stopPerc)) (short mirrored)
    while long and high >= entry x 1.008: exit(stop = highest x 0.997, limit = entry x (1 + 5 newPerc)), with
    newPerc = (entry - newStop) / entry
    while long and crossunder(ema13, ema21): close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: fractions of the signal close, picked by the signal's
      side, shifted one bar inside stops() and re-based on the fill (house rule).
    * The 0.8 % re-placement: once high >= signal close x 1.008 the new stop (highest x 0.997) is above the entry, so
      newPerc < 0 and the new limit (entry x (1 + 5 newPerc)) lies BELOW the market: a sell limit below the price,
      which fills at the next open. Ported as an exit signal on that bar (rule 3), as is the EMA cross close.
    * Entries only from flat: simulate() mirrors the house bracket on bars from the fill bar (as #430254 _run); an
      entry is allowed on the bar a stop is hit, and on the bar after an exit signal. A long and a short condition on
      one bar: the long is taken. Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-placed bracket acts as a next-open exit.
    2 generic: PASS, moving averages and distances relative to price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483509_ema13_21_sma120_flat_bracket_lock"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_len": [120, 240],
    "lock_pct": [0.8, 1.6],
}
DEFAULT_PARAMS = {"sma_len": 120, "fast": 13, "slow": 21, "min_stop": 0.002, "rr": 5.0, "lock_pct": 0.8}


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


def _inputs(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    x_up = (ef > es) & (ef.shift(1) <= es.shift(1))
    x_dn = (ef < es) & (ef.shift(1) >= es.shift(1))
    clear_above = pd.concat([lo.shift(k) > sma.shift(k) for k in range(1, 6)], axis=1).all(axis=1)
    clear_below = pd.concat([h.shift(k) < sma.shift(k) for k in range(1, 6)], axis=1).all(axis=1)
    long_c = ((c > sma) & x_up) | ((c > sma) & (c.shift(1) <= sma.shift(1)) & clear_above)
    short_c = ((c < sma) & x_dn) | ((c < sma) & (c.shift(1) >= sma.shift(1)) & clear_below)
    sl_l = np.maximum(p["min_stop"], ((c - ef) / c).to_numpy())
    sl_s = np.maximum(p["min_stop"], ((ef - c) / c).to_numpy())
    return long_c.to_numpy(), short_c.to_numpy(), x_up.to_numpy(), x_dn.to_numpy(), sl_l, sl_s


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    long_c, short_c, x_up, x_dn, sl_l, sl_s = _inputs(bars_df, p)
    rr, lock = p["rr"], 1 + p["lock_pct"] / 100
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_, t_, sig_c = 0, -1, 0.0, 0.0, np.nan
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - t_)):
                pos = 0
        start = pos
        if start == 0 and i + 1 < m:
            if long_c[i] and not np.isnan(sl_l[i]):
                le[i], pos, entry_i, s_, sig_c = True, 1, i + 1, sl_l[i], c[i]
                t_ = rr * s_
            elif short_c[i] and not np.isnan(sl_s[i]):
                se[i], pos, entry_i, s_, sig_c = True, -1, i + 1, sl_s[i], c[i]
                t_ = rr * s_
        if start == 1 and entry_i <= i and (h[i] >= sig_c * lock or x_dn[i]):
            lx[i], pos = True, 0
        if start == -1 and entry_i <= i and (lo[i] <= sig_c * (2 - lock) or x_up[i]):
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = _run(bars_df, p)
    _, _, _, _, sl_l, sl_s = _inputs(bars_df, p)
    sl = pd.Series(np.where(le, sl_l, sl_s), index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
