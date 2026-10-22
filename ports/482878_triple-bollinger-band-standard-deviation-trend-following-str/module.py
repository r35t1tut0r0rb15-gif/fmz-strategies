"""Three closes in a row beyond a Bollinger 20 / 2 band, hourly bars, from flat: three over the upper band go long with the stop at the first candle's low and a 1R target, three under the lower band go short with the mirror.
Port of FMZ strategy #482878 "Triple Bollinger Band Standard Deviation Trend Following Strategy" (Bollinger Band Buy and Sell Strategy (Entry at Close of 3rd Candle)).

FMZ source id: 482878

Source
    https://www.fmz.com/strategy/482878 (PineScript v6, FMZ last modified 2025-02-20 16:16:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-158), Bollinger 20 x 2.0; stop low[2] / high[2]; target 1R from the signal close; pyramiding 0; 10 % of equity
    close[2] > upper[2] and close[1] > upper[1] and close > upper and flat -> entry Buy + exit(stop = low[2], limit = close + (close - low[2]))
    close[2] < lower[2] and close[1] < lower[1] and close < lower and flat -> entry Sell + exit(stop = high[2], limit = close - (high[2] - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar and sent as fractions of the fill open (a level at or through
      it is marketable and closed one bar late, as #458256). The flat gate is followed in the signal loop
      with the bracket checked on each bar's high / low (as 449508), so a bracket exit inside a bar frees
      that bar's close for a new entry. Entries only from flat: Opposite entries cannot occur. Stop
      module: portfolio_kwargs {} (driver D4). The labels and plots are drawing only. The 10 % of equity
      size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; three-bar bracket as fractions of the fill.
    2 generic: PASS, three closes beyond a Bollinger band with a 1R bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482878_three_closes_beyond_bb20_2_first_bar_stop_1r_flat"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 40],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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


def _plan(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    above, below = c > up, c < dn
    buy = (above & above.shift(1, fill_value=False) & above.shift(2, fill_value=False)).to_numpy()
    sell = (below & below.shift(1, fill_value=False) & below.shift(2, fill_value=False)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    l2, h2 = lo.shift(2).to_numpy(dtype=float), h.shift(2).to_numpy(dtype=float)
    m = len(cv)
    le, se, lx, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_lv, tp_lv = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, out_pend = 0, 0, False
    sl = tp = np.nan
    for i in range(m):
        if out_pend:
            pos, out_pend = 0, False
        if pend != 0:
            pos, pend = pend, 0
            sl, tp = sl_lv[i - 1], tp_lv[i - 1]
            hit_open = (sl >= ov[i] or tp <= ov[i]) if pos > 0 else (sl <= ov[i] or tp >= ov[i])
            if hit_open:                      # marketable at the fill: closed one bar late
                if pos > 0:
                    lx[i] = True
                else:
                    sx[i] = True
                out_pend = True
        if pos != 0 and not out_pend:
            if (pos > 0 and (lv[i] <= sl or hv[i] >= tp)) or (pos < 0 and (hv[i] >= sl or lv[i] <= tp)):
                pos = 0                       # the bracket closes it inside the bar
        if pos == 0 and not out_pend:
            if buy[i]:
                le[i], pend = True, 1
                sl_lv[i], tp_lv[i] = l2[i], cv[i] + (cv[i] - l2[i])
            elif sell[i]:
                se[i], pend = True, -1
                sl_lv[i], tp_lv[i] = h2[i], cv[i] - (h2[i] - cv[i])
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx), S(sl_lv), S(tp_lv)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _, _ = _plan(bars_df, p)
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, sl_lv, tp_lv = _plan(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - sl_lv.shift(1) / o, tp_lv.shift(1) / o - 1
    s_sl, s_tp = sl_lv.shift(1) / o - 1, 1 - tp_lv.shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
