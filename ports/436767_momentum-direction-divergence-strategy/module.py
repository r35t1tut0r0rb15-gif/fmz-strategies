"""Blau's commodity selection index zones, broker days: the 5-bar average of the CSI (ADXR x true range over the close, scaled by 1 / sqrt(32)) above 0.024 is long, at or under 0.004 short, the earlier state
holding in between; an optional switch trades the reverse; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #436767 "Momentum Direction Divergence Strategy" (Ergodic CSI Backtest).

FMZ source id: 436767

Source
    https://www.fmz.com/strategy/436767 (PineScript v2, FMZ last modified 2023-12-27 15:37:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 157-191), r 32, length 1, big point value 1, smoothing 5, zones 0.004 / 0.024, reverse off
    fADX(1) from rma(tr, 1) and the directional moves (fixnan);  K = 100 (BigPointValue / sqrt(r) / 155);  nRes = K x ADXR x atr(1) / Length;  xCSI = nRes / close;  xSMA_CSI = sma(xCSI, 5)
    pos = 1 if xSMA_CSI > 0.024, -1 if <= 0.004, else pos[1];  possig = -pos when reverse;  entry Long / Short on possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The CSI is a true range over the close times a 0-100 index: dimensionless, so the zones need no
      re-expression. With length 1 every rma is the value itself; the DI lines carry their last value
      where the true range is zero (fixnan). The state is a level, so the entry is sent on every bar of
      the state; a same-side entry while in the position is ignored (pyramiding 0). REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dimensionless index zones.
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

NAME = "fmz_436767_ergodic_csi_zone_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r": [32, 20],
    "smth_len": [5, 10],
}
DEFAULT_PARAMS = {"r": 32, "smth_len": 5, "length": 1, "big_point_value": 1.0, "sell_zone": 0.004,
                  "buy_zone": 0.024, "reverse": False}


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


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    parts = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1)
    tr_na = parts.max(axis=1, skipna=False)              # tr: na on the first bar
    tr_true = parts.max(axis=1)                          # tr(true): high - low on the first bar
    up = h.diff()
    down = -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=c.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=c.index)
    trur = _rma(tr_na, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(100.0 * _rma(plus_dm, n) / trur)
        minus = _fixnan(100.0 * _rma(minus_dm, n) / trur)
        s = plus + minus
        adx = 100.0 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    adxr = (adx + adx.shift(1)) * 0.5
    xtr = _rma(tr_true, 1)
    k = 100.0 * (float(p["big_point_value"]) / np.sqrt(float(p["r"])) / (150 + 5))
    nres = (k * adxr * xtr / n).where(n + xtr > 0, 0.0)
    csi = (nres / c).where(c > 0, 0.0)
    sm = csi.rolling(int(p["smth_len"])).mean().to_numpy()
    m = len(sm)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if sm[i] > float(p["buy_zone"]):
                prev = 1.0
            elif sm[i] <= float(p["sell_zone"]):
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
