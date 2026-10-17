"""Three closes in a row outside a Bollinger band entered from flat, with the stop at the first bar's far extreme and
a 1 R target, 1-hour bars: three closes above the upper band(20, 2) go long (stop the low two bars back, target close +
(close - stop)); three closes below the lower band go short (mirrored with the high).
Port of FMZ strategy #482878 "三重布林带标准差趋势跟踪策略-Triple-Bollinger-Band-Standard-Deviation-Trend-Following-Strategy" (Bollinger Band Buy and Sell Strategy (Entry at Close of 3rd Candle)).

FMZ source id: 482878

Source
    https://www.fmz.com/strategy/482878 (PineScript v6, FMZ last modified 2025-02-20 16:16:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-147), BB 20 x 2
    buy = close, close[1], close[2] above their upper bands, from flat: stop = low[2], target = close + (close - low[2])
    sell mirrored with high[2]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: sl = (close - low[2]) / close, tp = sl (short:
      (high[2] - close) / close), picked by the signal's side, shifted one bar inside stops() and re-based on the fill
      (house rule). A signal whose stop is not beyond the close emits no entry (as #490798).
    * Entries only from flat: simulate() mirrors the house bracket on bars from the fill bar (as #430254 _run); an entry
      is allowed on the bar a stop or target is hit. Opposite entries cannot occur. ta.stdev population.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, Bollinger bands and the setup's own extremes.
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

NAME = "fmz_482878_three_closes_outside_band_flat_1r"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [2.0, 1.5],
    "rr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rr": 1.0}


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
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    above, below = c > up, c < dn
    buy = above & above.shift(1, fill_value=False) & above.shift(2, fill_value=False)
    sell = below & below.shift(1, fill_value=False) & below.shift(2, fill_value=False)
    d_long, d_short = ((c - lo.shift(2)) / c).to_numpy(), ((h.shift(2) - c) / c).to_numpy()
    return buy.to_numpy() & (d_long > 0), sell.to_numpy() & (d_short > 0), d_long, d_short


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    buy, sell, d_long, d_short = _inputs(bars_df, p)
    rr = p["rr"]
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + rr * s_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - rr * s_)):
                pos = 0
        if pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pos, entry_i, s_ = True, 1, i + 1, d_long[i]
            elif sell[i]:
                se[i], pos, entry_i, s_ = True, -1, i + 1, d_short[i]
            if pos != 0:
                sl[i] = s_
    return le, se, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _run(bars_df, p)
    s = pd.Series(sl, index=bars_df.index).shift(1)
    return {"sl_stop": s, "tp_stop": p["rr"] * s}


def portfolio_kwargs(**params):
    return {}
