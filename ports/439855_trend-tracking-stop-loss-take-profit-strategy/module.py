"""Follow Line flips, 1-hour bars: a close outside the Bollinger band (21, 1) moves an ATR(5) trend line, and its turn up goes long, its turn down goes short; a long is closed at the open after its fill bar
(its stop is placed far above the market); a short has a 10 % target; reversing.
Port of FMZ strategy #439855 "Trend Tracking Stop Loss Take Profit Strategy" (Follow Line Indicator).

FMZ source id: 439855

Source
    https://www.fmz.com/strategy/439855 (PineScript v4, FMZ last modified 2024-01-24 14:17:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-185), BB 21 x 1; ATR filter on, ATR 5; labels shown
    BBSignal = close > BBUpper ? 1 : close < BBLower ? -1 : 0;  TrendLine = low - atr (ratchets up) on 1, high + atr (ratchets down) on -1, else held;  iTrend = line rising 1 / falling -1
    buy = iTrend turns 1 -> entry Buy;  sell = turns -1 -> entry Sell;  long: exit(stop = avg x 100, limit = avg x 1.1);  short: exit(stop = avg x 100, limit = avg x 0.9)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's stop is a sell stop at 100 times the average price, on the wrong side of the market, so
      it fills at the first open after it is placed (sent at the fill bar's close): the port closes each
      long on its fill bar's signal (one-bar trades, as the house rule for such stops). The short's stop
      at 100 times the price can never fill; its target is a fixed 10 % of the fill (tp_stop 0.10 for
      shorts only). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the wrong-side stop read as a close signal.
    2 generic: PASS, Bollinger signal and an ATR trend line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND368736 (2 members, best partner #368736, Jaccard 0.781); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439855_follow_line_flip_one_bar_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_period": [21, 50],
    "atr_period": [5, 14],
}
DEFAULT_PARAMS = {"bb_period": 21, "atr_period": 5, "bb_dev": 1.0, "tp_short": 0.10}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_period"])
    sd = c.rolling(n).std(ddof=0) * float(p["bb_dev"])
    ub, lb = (c.rolling(n).mean() + sd).to_numpy(), (c.rolling(n).mean() - sd).to_numpy()
    a = _atr(bars_df, p["atr_period"]).to_numpy()
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cv)
    tl = np.zeros(m)
    it = np.zeros(m)
    for i in range(m):
        prev = tl[i - 1] if i > 0 else 0.0
        if cv[i] > ub[i]:
            x = lv[i] - a[i]
            tl[i] = prev if x < prev else x
        elif cv[i] < lb[i]:
            x = hv[i] + a[i]
            tl[i] = prev if x > prev else x
        else:
            tl[i] = prev
        if np.isnan(tl[i]):
            tl[i] = prev
        pit = it[i - 1] if i > 0 else 0.0
        it[i] = 1 if tl[i] > prev else (-1 if tl[i] < prev else pit)
    pit = np.concatenate(([0.0], it[:-1]))
    return (pit == -1) & (it == 1), (pit == 1) & (it == -1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    m = len(buy)
    le, lx, se = buy.copy(), np.zeros(m, dtype=bool), sell.copy()
    for i in range(m - 1):
        if le[i] and not se[i + 1] and not le[i + 1]:
            lx[i + 1] = True                              # the wrong-side stop fills after the fill bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), false


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sell = _signals(bars_df, p)
    ix = bars_df.index
    tp = pd.Series(float(p["tp_short"]), index=ix).where(pd.Series(sell, index=ix))
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
