"""DMI direction above the EMA 34, broker days: a close above the EMA 34 with +DI over 17 and the ADX above -DI holds a long; the mirror holds a short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439991 "三EMA配合DMI和MACD的趋势跟踪策略Trend-Following-Strategy-with-3-EMAs-DMI-and-MACD" (2 EMA di+ Buy Sell, strategy).

FMZ source id: 439991

Source
    https://www.fmz.com/strategy/439991 (PineScript v5, FMZ last modified 2024-01-25 15:48:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-208), EMA 34 / 89 / 200 (89 / 200 plot only); DI 14; MACD 12 / 26 / 9 (unused)
    buy = close > ema34 and plusDI > 17 and adx > minusDI;  sell = close < ema34 and minusDI > 17 and adx > plusDI;  entry Buy / entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DI and ADX use Wilder smoothing of the true range (undefined on the first bar). The MACD and the
      EMA 89 / 200 feed no order. A bar meeting both tests sends both entries and the later sell wins
      (as #437773). A same-side entry while in the position is ignored. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA side and DMI levels.
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

NAME = "fmz_439991_ema34_dmi17_adx_state"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_len": [14, 21],
    "di_level": [17, 25],
}
DEFAULT_PARAMS = {"di_len": 14, "di_level": 17, "ema_len": 34}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["di_len"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > dn) & (up > 0), up, 0.0))
    mdm = dn.where(dn.isna(), np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = 100 * _rma(pdm, n) / trr
        mdi = 100 * _rma(mdm, n) / trr
    s = pdi + mdi
    adx = 100 * _rma((pdi - mdi).abs() / s.where(s != 0, 1.0), n)
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    lv = float(p["di_level"])
    buy = ((c > e) & (pdi > lv) & (adx > mdi)).to_numpy()
    sell = ((c < e) & (mdi > lv) & (adx > pdi)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if sell[i]:
            pos = -1
        elif buy[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
