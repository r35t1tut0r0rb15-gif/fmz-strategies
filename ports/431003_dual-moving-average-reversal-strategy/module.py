"""HPotter combo, broker days: the 2/20 EMA state (the two-bar extreme beyond the EMA 14 against the previous close) and
Vervoort's ATR trailing-stop state (ATR 5 x 3.5, the close crossing the stop line) must agree; both long holds a long,
both short holds a short, any disagreement closes everything.
Port of FMZ strategy #431003 "Dual Moving Average Reversal Strategy" (Combo 2/20 EMA & Average True Range Reversed).

FMZ source id: 431003

Source
    https://www.fmz.com/strategy/431003 (PineScript v5, FMZ last modified 2023-11-03 16:51:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 187-255), EMA 14; ATR 5 x 3.5
    EMA20: nXS = (min(low, low[1]) > ema or max(high, high[1]) < ema) ? min(low, low[1]) : max(high, high[1])
           pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    ATRR: stop = ATR trailing stop of close (Vervoort); pos = close crosses above stop[1] -> 1, below -> -1, else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR stop line is the indicator's state only (no order is placed at it). nz(stop[1], 0) as
      written. "Trade reverse" defaults to false and the 2005 start is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA and ATR states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431003_combo_2_20_ema_atr_reversed"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "atr_mult": [3.5, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "atr_len": 5, "atr_mult": 3.5}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = np.maximum(h, h.shift(1))
    ll = np.minimum(lo, lo.shift(1))
    nxs = ll.where((ll > ema) | (hh < ema), hh)
    c1 = c.shift(1)
    pos1 = _hold((nxs < c1).to_numpy() & ~(nxs > c1).to_numpy(), (nxs > c1).to_numpy())
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    loss = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    pos2 = np.zeros(m, dtype=np.int8)
    stop_p, q = 0.0, 0
    for i in range(m):
        cp = cv[i - 1] if i else np.nan
        if cv[i] > stop_p and cp > stop_p:
            st = max(stop_p, cv[i] - loss[i])
        elif cv[i] < stop_p and cp < stop_p:
            st = min(stop_p, cv[i] + loss[i])
        else:
            st = cv[i] - loss[i] if cv[i] > stop_p else cv[i] + loss[i]
        if cp < stop_p and cv[i] > stop_p:
            q = 1
        elif cp > stop_p and cv[i] < stop_p:
            q = -1
        pos2[i] = q
        stop_p = 0.0 if np.isnan(st) else st
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
