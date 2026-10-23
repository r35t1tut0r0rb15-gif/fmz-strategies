"""Three-minute bars: with the Hull MA 55 falling against two bars ago, the LSMA 25 crossing over it goes long; with the Hull rising, the LSMA crossing under it goes short; a 100 % target from the entry; reversing.
Port of FMZ strategy #441063 "基于Hull指标和LSMA指标的趋势跟踪量化策略Trend-Following-Quant-Strategy-Based-on-Hull-and-LSMA-Indicators" (Strategy Myth-Busting #9 - HullSuite+LSMA - [MYN]).

FMZ source id: 441063

Source
    https://www.fmz.com/strategy/441063 (PineScript v5, FMZ last modified 2024-02-05 11:58:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-416), LSMA 25; Hull variation Hma, length 55, multiplier 1; ADX filter off; TP1 .. TP4 at 100 % (each 100 % of the position); stop 999 %
    longEntry = hullColor == red (HULL <= HULL[2]) and crossover(lsma, MHULL);  shortEntry = green and crossunder(lsma, MHULL)
    not in a long -> entry Long;  not in a short -> entry Short;  exit TP1 .. TP4 (profit = 100 % of avg in ticks);  close on a 999 % stop

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every take-profit is 100 % away (qty 100 % each, so the first takes the whole position) and the
      stop 999 %: in practice the positions end by the reversal (a 100 % target is kept as a tp_stop of
      1.0; for a short it can never be reached). HMA = wma(2 x wma(n / 2) - wma(n), round(sqrt(n))) with
      n / 2 truncated. The ADX filter is off and volume only enters an alert text: volume is not used.
      REVERSAL INTENDED. 1 % of equity and leverage are sizing. Stop module: portfolio_kwargs {} (driver
      D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 100 % target from the fill.
    2 generic: PASS, LSMA crossings of the Hull MA against its slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity, contracts = equity / close x leverage, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441063_lsma25_cross_hull55_counter_slope_3m_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hull_len": [55, 100],
    "lsma_len": [25, 50],
}
DEFAULT_PARAMS = {"hull_len": 55, "lsma_len": 25, "tp": 1.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["hull_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    lsma = _linreg(c, int(p["lsma_len"]))
    rising = hull > hull.shift(2)
    red = ~rising & hull.notna() & hull.shift(2).notna()
    up = (lsma > hull) & (lsma.shift(1) <= hull.shift(1))
    dn = (lsma < hull) & (lsma.shift(1) >= hull.shift(1))
    le = (red & up).to_numpy()
    se = (rising & dn).to_numpy()
    m = len(le)
    l_s, s_s = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if le[i] and pos != 1:
            l_s[i], pos = True, 1
        elif se[i] and pos != -1:
            s_s[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(l_s, index=ix), false, pd.Series(s_s, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
