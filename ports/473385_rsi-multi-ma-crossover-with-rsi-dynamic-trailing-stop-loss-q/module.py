"""SMA 9 / 21 crossings with RSI 14 filters, daily bars: the cross up with RSI over 55 goes long, the cross down with RSI under 45 goes short; reversing. Close tests end a long on RSI over 80, a close 1 % under the signal bar's low, or a close under a 1 % close-based ratchet; the short mirrors (RSI under 22).
Port of FMZ strategy #473385 "多重均线交叉与RSI动态追踪止损量化交易策略-Multi-MA-Crossover-with-RSI-Dynamic-Trailing-Stop-Loss-Quantitative-Trading-Strategy" (ojha's Intraday MA Crossover + RSI Strategy with Trailing Stop).

FMZ source id: 473385

Source
    https://www.fmz.com/strategy/473385 (PineScript v5, FMZ last modified 2024-11-29 16:10:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-178), SMA 9 / 21, RSI 14 (constants); ratchet 1 % of the close; stop 1 % beyond the signal bar's low / high
    cross up and rsi > 55 -> entry Long, entryLow := low, trail := close x 0.99;  long: trail := max(trail, close x 0.99);  rsi > 80 or close < entryLow x 0.99 or close < trail -> close Long, entryLow := na, trail := na;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * All exits are bar-close tests, so a loop follows the levels as written: they are set on every
      signal bar (also a repeat inside a trade), the ratchet moves only while the side is held, and a
      passing exit test resets them even when no long is held (math.max with na stays na, so a trade
      whose levels were reset keeps only the RSI exit). A close acts only on the side held into the bar
      and not reversed on it (#437773). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days; the title's "Intraday" is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with RSI filters and close-based stops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473385_sma9_21_cross_rsi_close_ratchet_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a, b = c.rolling(9).mean(), c.rolling(21).mean()
    r = _rsi(c, 14)
    lc = ((a > b) & (a.shift(1) <= b.shift(1)) & (r > 55)).to_numpy()
    sc = ((a < b) & (a.shift(1) >= b.shift(1)) & (r < 45)).to_numpy()
    rv, hv, lv, cv = (x.to_numpy(dtype=float) for x in (r, h, lo, c))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    el, lt, eh, st = np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        pos = nxt
        if lc[i]:
            if pos != 1:
                le[i], nxt = True, 1
            el, lt = lv[i], cv[i] * 0.99
        if sc[i]:
            if pos != -1:
                se[i], nxt = True, -1
            eh, st = hv[i], cv[i] * 1.01
        if pos == 1 and not np.isnan(lt):
            lt = max(lt, cv[i] * 0.99)
        if pos == -1 and not np.isnan(st):
            st = min(st, cv[i] * 1.01)
        if rv[i] > 80 or (el > 0 and cv[i] < el * 0.99) or cv[i] < lt:
            if pos == 1 and nxt == 1:
                lx[i], nxt = True, 0
            el, lt = np.nan, np.nan
        if rv[i] < 22 or (eh > 0 and cv[i] > eh * 1.01) or cv[i] > st:
            if pos == -1 and nxt == -1:
                sx[i], nxt = True, 0
            eh, st = np.nan, np.nan
    ix = bars_df.index
    return tuple(pd.Series(x, index=ix) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
