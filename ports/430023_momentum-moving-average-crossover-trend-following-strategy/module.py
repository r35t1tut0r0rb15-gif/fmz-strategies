"""HMA crossover with turning-point exits, 4-hour bars: with ADX 14 above 20, an HMA 5 of the open above an HMA 7 of the
open holds a long (below: a short); the HMA 5 turning down (its one-bar ROC crossing below -0.02 % after an up turn)
closes a long, turning up closes a short.
Port of FMZ strategy #430023 "Momentum Moving Average Crossover Trend Following Strategy" (MA Crossover Strategy with MA Turning Point Exits).

FMZ source id: 430023

Source
    https://www.fmz.com/strategy/430023 (PineScript v3, FMZ last modified 2023-10-24 12:31:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-282), HMA 5 / 7 of open, ADX 14 / 14 above 20, lookback 1, minimum slope 2 x 0.01
    price1 = hma(open, 5); price2 = hma(open, 7); sig = ADX(14, 14)
    price1 > price2 and sig > 20 -> entry long;  price1 < price2 and sig > 20 -> entry short
    roc1 = roc(price1, 1): crossover(roc1, 0.02) -> up state; crossunder(roc1, -0.02) -> down state
    up and down[1] and sig > 20 -> close "Short";  down and up[1] and sig > 20 -> close "Long"

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(syminfo.tickerid, timeframe.period, open) is the chart's own open (known at the
      bar's open; the signal still waits for the bar's close).
    * The entries are written first, the closes after: a close acts only on the position held at the
      start of the bar and only when the bar's entry does not reverse it (then the bar ends flat); a
      fresh entry from flat, or a reversal, stands. A closed position re-enters on the next bar whose
      entry condition holds, as written.
    * The slope threshold is 0.02 % per bar (0.01 x the input, against a percent ROC), as written.
      HMA half length int(n / 2), root round(sqrt(n)). ADX as the source's dirmov (Wilder averages);
      fixnan carries the last DI value over a zero true range.
    * The MA type options (SMA, EMA) are not ported: the default HMA only.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages of the open, ADX and a percentage slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_430023_hma_cross_turning_exits"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [5, 9],
    "adx_threshold": [20, 25],
}
DEFAULT_PARAMS = {"ma1": 5, "ma_gap": 2, "adx_len": 14, "di_len": 14, "adx_threshold": 20, "strength": 2.0,
                  "lookback": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def _rma(x, n):
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(h, lo, c, di_len, adx_len):
    up, down = h.diff(), -lo.diff()
    plus_dm = ((up > down) & (up > 0)).astype(float) * up
    minus_dm = ((down > up) & (down > 0)).astype(float) * down
    plus_dm, minus_dm = plus_dm.where(up.notna()), minus_dm.where(down.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, di_len)
    plus = _fixnan(100 * _rma(plus_dm, di_len) / atr.replace(0.0, np.nan))
    minus = _fixnan(100 * _rma(minus_dm, di_len) / atr.replace(0.0, np.nan))
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n1 = int(p["ma1"])
    p1, p2 = _hma(o, n1), _hma(o, n1 + int(p["ma_gap"]))
    strong = (_adx(h, lo, c, int(p["di_len"]), int(p["adx_len"])) > p["adx_threshold"]).to_numpy()
    lc = (p1 > p2).to_numpy() & strong
    sc = (p1 < p2).to_numpy() & strong
    k = int(p["lookback"])
    roc = 100 * (p1 - p1.shift(k)) / p1.shift(k)
    s = float(p["strength"]) * 0.01
    xu = ((roc > s) & (roc.shift(1) <= s)).to_numpy()
    xd = ((roc < -s) & (roc.shift(1) >= -s)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    up = dn = False
    pos = 0
    for i in range(m):
        up1, dn1 = up, dn
        if xu[i]:
            up, dn = True, False
        if xd[i]:
            up, dn = False, True
        start = pos
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        short_exit = up and dn1 and strong[i]
        long_exit = dn and up1 and strong[i]
        if short_exit and pos == -1 and start == -1:
            pos = 0
        if long_exit and pos == 1 and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
