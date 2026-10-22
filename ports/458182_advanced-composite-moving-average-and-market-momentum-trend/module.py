"""A Hull-style average against its previous value with Ichimoku filters, bar size from the search: the average rising with the close over it, over the close 23 bars ago and over the displaced cloud (Tenkan at or over Kijun, or the close over Kijun) goes long, the mirror goes short; a long closes when the average turns down with any of the weakness tests, a short on the mirror; reversing.
Port of FMZ strategy #458182 "Advanced Composite Moving Average and Market Momentum Trend Capture Strategy" (Private Strategy TradingView).

FMZ source id: 458182

Source
    https://www.fmz.com/strategy/458182 (PineScript v4, FMZ last modified 2024-07-30 16:27:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 237-281), double Hull 12 (WMA 6 / 12, WMA 3 of the difference); Tenkan 9, Kijun 24, Span B 51, displacement 24 (spans and Chikou at 23 bars back)
    n1 > n2 and close > n2 and close > close[23] and close > max(spanA, spanB)[23] and (tenkan >= kijun or close > kijun) -> entry Long;  the mirror -> entry Short
    closelong = n1 < n2 and (close < n2 or tenkan < kijun or close < tenkan or close < kijun or close < spanH or close < close[23]) -> close Long;  closeshort mirrored -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Version 4. n2 is n1 of the previous bar (the same calculation on close[1]). The source has no
      backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the
      bars with the house bar_sizes.build_bars with the driver's bar_size. The entries are called
      before the closes; a close acts only on a position held into the bar and not being reversed on
      that bar (#437773). Exits are bar-close tests filled at the next open. REVERSAL INTENDED. No sizing
      code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull-style turns with Ichimoku filters.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458182_double_hull_turn_ichimoku_filters_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [12, 24],
    "kijun": [24, 26],
}
DEFAULT_PARAMS = {"keh": 12, "kijun": 24, "tenkan": 9, "span_b": 51, "displacement": 24}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _wma(x, n):
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def _mid(h, lo, n):
    return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["keh"])
    diff = 2 * _wma(c, round(k / 2)) - _wma(c, k)
    n1 = _wma(diff, round(np.sqrt(k)))
    n2 = n1.shift(1)
    tk, kj = _mid(h, lo, p["tenkan"]), _mid(h, lo, p["kijun"])
    sa, sb = (tk + kj) / 2, _mid(h, lo, p["span_b"])
    d = int(p["displacement"]) - 1
    sh = np.maximum(sa.shift(d), sb.shift(d))
    sl = np.minimum(sa.shift(d), sb.shift(d))
    chik = c.shift(d)
    lc = (n1 > n2) & (c > n2) & (c > chik) & (c > sh) & ((tk >= kj) | (c > kj))
    sc = (n1 < n2) & (c < n2) & (c < chik) & (c < sl) & ((tk <= kj) | (c < kj))
    cl = (n1 < n2) & ((c < n2) | (tk < kj) | (c < tk) | (c < kj) | (c < sh) | (c < chik))
    cs = (n1 > n2) & ((c > n2) | (tk > kj) | (c > tk) | (c > kj) | (c > sl) | (c > chik))
    lc, sc, cl, cs = (x.to_numpy() for x in (lc, sc, cl, cs))
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if lc[i]:
            cur = 1
        if sc[i]:
            cur = -1
        if cl[i] and pos == 1 and cur == 1:
            cur = 0                              # the close acts only on a long held, not reversed
        if cs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
