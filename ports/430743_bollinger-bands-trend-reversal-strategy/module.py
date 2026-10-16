"""Bollinger touch reversals in the EMA 200 trend, 10-minute bars, from flat: two bars touching the lower band above the
EMA 200 with a bullish reversal candle go long, the target at the upper band and a stop 1.5 times the target distance
below; the mirror goes short (stop at the target distance / 1.5, as written).
Port of FMZ strategy #430743 "Bollinger Bands Trend Reversal Strategy" (Bollinger Bands Trending Reverse Strategy).

FMZ source id: 430743

Source
    https://www.fmz.com/strategy/430743 (PineScript v4, FMZ last modified 2023-11-01 11:29:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 147-203), BB 20 / 2, EMA 200, risk / reward 1.5
    entryLong = low[1] <= lower[1] and low <= lower and low > ema200; reversal candle (green after red); flat
    stopLong = ((close / upper - 1) x 1.5 + 1) x close -> entry long; exit(limit = upper, stop = stopLong) every bar
    entryShort mirrored; stopShort = ((close / lower - 1) / 1.5 + 1) x close; exit(limit = lower, stop = stopShort)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed at the signal; the target is re-issued every bar at the current opposite band
      (a moving level): rule 2, mark trailing_stop_pending. The port fixes the target at the signal
      bar's band; both as fractions of the signal close, shifted one bar (re-based on the fill).
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot occur.
      The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving target fixed at entry (rule 2).
    2 generic: PASS, Bollinger bands, an EMA and a reward ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out cash order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430743_bb_trend_touch_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "riskreward": [1.5, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "ema_len": 200, "riskreward": 1.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = basis + p["mult"] * sd, basis - p["mult"] * sd
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rr = float(p["riskreward"])
    rev_l = (c > o) & (c.shift(1) < o.shift(1))
    rev_s = (c < o) & (c.shift(1) > o.shift(1))
    buy = (rev_l & (lo.shift(1) <= dn.shift(1)) & (lo <= dn) & (lo > ema)).to_numpy()
    sell = (rev_s & (h.shift(1) >= up.shift(1)) & (h >= up) & (h < ema)).to_numpy()
    tp_l = ((up - c) / c).to_numpy()
    sl_l = (-(c / up - 1) * rr).to_numpy()            # 1 - stopLong / close
    tp_s = ((c - dn) / c).to_numpy()
    sl_s = ((c / dn - 1) / rr).to_numpy()
    return buy, sell, sl_l, tp_l, sl_s, tp_s


def _run(bars_df, p):
    buy, sell, sl_l, tp_l, sl_s, tp_s = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and buy[i] and sl_l[i] > 0 and tp_l[i] > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_l[i], tp_l[i]
            sl_arr[i], tp_arr[i] = s_, t_
        elif pos == 0 and sell[i] and sl_s[i] > 0 and tp_s[i] > 0:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl_s[i], tp_s[i]
            sl_arr[i], tp_arr[i] = s_, t_
    return le, se, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
