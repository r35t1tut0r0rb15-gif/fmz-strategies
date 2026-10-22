"""Volatility-stop flips, daily bars: when the close-based volatility stop (ATR 20 x 2) turns up it goes long, when it turns down it goes short; a long closes on a low under the stop, a short on a high over it; reversing.
Port of FMZ strategy #474849 "Dynamic Timing and Position Management Strategy Based on Volatility" (BNF FUT 5 min Volatility Strategy).

FMZ source id: 474849

Source
    https://www.fmz.com/strategy/474849 (PineScript v5, FMZ last modified 2024-12-12 15:19:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-150), length 20; multiplier 2.0; risk-based size; close_all at 15:15
    [vStop, up] = volStop(close, 20, 2.0);  up and not up[1] -> close Short, entry Long;  not up and up[1] -> close Long, entry Short;  long and low < vStop -> close Long;  short and high > vStop -> close Short;  hour == 15 and minute == 15 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volatility stop is the source's var recursion (a loop): max / min of the close since the last
      flip, the stop ratcheting by max - ATR x 2 (min + ATR x 2), restarting at the close when it is na
      (math.max with na is na), the ATR replaced by the true range while it is na. The stop-hit closes
      are bar-close tests on the bar's low / high; a close acts only on the side held into the bar and
      not reversed on it (#437773); a loop follows the position. The 15:15 close_all is a clock test,
      which on daily bars (stamped at the session start) never fires. The risk-based size is not
      ported. REVERSAL INTENDED. FREQ = "1D" from the backtest header (broker days; the title's "5 min"
      is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility-stop flips with stop-hit closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size from a typed capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock close 15:15 never fires on daily bars.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474849_volatility_stop_atr20x2_flip_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
    "factor": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "factor": 2.0}


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


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _volstop(bars_df, n, factor):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    a = (_rma(tr, n) * factor).to_numpy(dtype=float)
    trv = tr.to_numpy(dtype=float)
    atrm = np.where(np.isnan(a), trv, a)         # nz(atr x factor, ta.tr)
    s = c.to_numpy(dtype=float)
    m = len(s)
    stop_out, up_out = np.full(m, np.nan), np.zeros(m, dtype=bool)
    mx = mn = s[0] if m else np.nan
    up, stop = True, np.nan
    for i in range(m):
        mx, mn = max(mx, s[i]), min(mn, s[i])
        cand = _nmax(stop, mx - atrm[i]) if up else _nmin(stop, mn + atrm[i])
        stop = s[i] if np.isnan(cand) else cand
        up_new = bool(s[i] - stop >= 0.0)
        if up_new != up:
            mx = mn = s[i]
            stop = (mx - atrm[i]) if up_new else (mn + atrm[i])
        up = up_new
        stop_out[i], up_out[i] = stop, up
    return stop_out, up_out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    vs, up = _volstop(bars_df, int(p["length"]), float(p["factor"]))
    up1 = np.concatenate([[True], up[:-1]])
    tu = up & ~up1
    td = ~up & up1
    td[0] = False                                # uptrend[1] is na on the first bar
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(vs)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if not np.isnan(vs[i]):
            if tu[i] and nxt != 1:
                le[i], nxt = True, 1
            if td[i] and nxt != -1:
                se[i], nxt = True, -1
        if pos == 1 and nxt == 1 and lv[i] < vs[i]:
            lx[i], nxt = True, 0
        if pos == -1 and nxt == -1 and hv[i] > vs[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
