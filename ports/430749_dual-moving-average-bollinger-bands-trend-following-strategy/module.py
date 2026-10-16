"""Augmented Bollinger dip (JCGMarkets), 1-hour bars, long only from flat: a close at or under the EMA 20 of lows minus
2 standard deviations goes long, with a 3 % stop and a target at the EMA 20 of closes (fixed at the signal bar; the
source re-issues it every bar).
Port of FMZ strategy #430749 "Dual Moving Average Bollinger Bands Trend Following Strategy" (B.Bands | Augmented | Intra-range | Long-Only).

FMZ source id: 430749

Source
    https://www.fmz.com/strategy/430749 (PineScript v4, FMZ last modified 2023-11-01 14:15:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 223-387), augmented bands EMA 20 of high / low / close, 2 sd; stop 3 %; target "middle"; max spread 20,000 (price units)
    entry_long_augm = close <= ema(low, 20) - 2 stdev(close, 20) and spread_augm < 20000 -> (flat) entry long; SL = close x 0.97
    in position: exit("Target", "Entry_A", limit = ema(close, 20), stop = SL), re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: the augmented system on, the simple one off, target "middle", trailing off, sell in
      profit off.
    * The stop is fixed at the signal close (3 %); the target follows the EMA 20 every bar (a moving
      level): rule 2, mark trailing_stop_pending; the port fixes it at the signal bar's EMA 20 as a
      fraction of its close (shifted one bar, re-based on the fill).
    * Criterion 2: the 20,000 price-unit cap on the band spread never binds on the header market
      (1-hour BTC bands are far narrower): not ported.
    * Entries only from flat: "flat" follows the house bracket on bars. Long only; Opposite entries
      cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving target fixed at entry (rule 2).
    2 generic: ADAPT, the inert price-unit spread cap dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: round(equity / close) per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430749_augmented_bb_dip_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "periods": [20, 50],
    "stop_loss": [3.0, 5.0],
}
DEFAULT_PARAMS = {"periods": 20, "std": 2.0, "stop_loss": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    lo, c = bars_df["low"], bars_df["close"]
    n = int(p["periods"])
    dev = c.rolling(n).std(ddof=0) * float(p["std"])
    lower = lo.ewm(span=n, adjust=False).mean() - dev
    mid = c.ewm(span=n, adjust=False).mean()
    buy = (c <= lower).to_numpy()
    tp_f = ((mid - c) / c).to_numpy()
    sl = float(p["stop_loss"]) / 100
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + t_):
                pos = 0
        if pos == 0 and buy[i] and tp_f[i] > 0:
            le[i], pos, entry_i, t_ = True, 1, i + 1, tp_f[i]
            sl_arr[i], tp_arr[i] = sl, t_
    return le, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
