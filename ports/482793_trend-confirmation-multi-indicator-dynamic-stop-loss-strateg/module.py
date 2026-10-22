"""Close above the SMA 30 with MACD 9 / 18 / 9 over its signal and over zero and ADX 14 over 25, broker days, long only: the state buys from flat; once two swing-low values have been recorded during the trade and a close falls under the SMA, a stop at the second-last one works (followed in the loop).
Port of FMZ strategy #482793 "Trend Confirmation Multi Indicator Dynamic Stop Loss Strategy" (Invest SMA|MACD|ADX Long Weekly Strategy (BtTL)).

FMZ source id: 482793

Source
    https://www.fmz.com/strategy/482793 (PineScript v5, FMZ last modified 2025-02-20 11:19:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-153), SMA 30; MACD 9 / 18 / 9; DMI 14 / 14, ADX > 25; 5-bar swing lows
    close > sma and macd > signal and macd > 0 and adx > 25 -> entry Long
    isSwingLow[1] -> secondLast := last, last := low[1];  close < sma and secondLast exists -> exit(stop = secondLast);  position <= 0 -> both reset to na

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing test marks bar t - 2 as the low, but the stored value is low[1] read one bar later (the
      bar after the swing low), as written. The values reset on every flat bar, so two must be recorded
      during the trade before a stop can be placed; once placed, the stop works on later bars and moves
      when re-sent. stops() cannot express a level placed and moved after entry, so it is kept pending
      (mark trailing_stop_pending); because it is the only exit, the loop follows the working level on
      each bar's low (as #449508) and sends the close at that bar's close (one bar late, not at the level);
      a new entry signal on that bar keeps the position. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing-low stop followed in the loop (pending).
    2 generic: PASS, SMA / MACD / ADX trend state with a swing-low stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482793_sma30_macd_adx25_state_swing_low_stop_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [30, 50],
    "adx_min": [25, 20],
}
DEFAULT_PARAMS = {"sma_length": 30, "adx_min": 25, "macd_fast": 9, "macd_slow": 18, "macd_signal": 9,
                  "adx_length": 14}


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
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["sma_length"])).mean()

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["macd_fast"]) - ema(c, p["macd_slow"])
    sig = ema(macd, p["macd_signal"])
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    cond = ((c > sma) & (macd > sig) & (macd > 0) & (adx > float(p["adx_min"]))).to_numpy()
    below = (c < sma).to_numpy()
    l1 = lo.shift(1)
    sw = ((lo.shift(2) > l1) & (lo.shift(3) > l1) & (l1 < lo) & (l1 < lo.shift(4))).to_numpy()
    lv = lo.to_numpy(dtype=float)
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    last = second = stop = np.nan
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        hit = pos == 1 and not np.isnan(stop) and lv[i] <= stop     # the working stop is touched
        eff = 0 if hit else pos
        if i > 0 and sw[i - 1]:
            second, last = last, lv[i - 1]
        new = cond[i] and eff == 0
        if eff == 1 and below[i] and not np.isnan(second):
            stop = second
        if eff <= 0:
            last = second = stop = np.nan
        if hit and new:
            continue                              # stopped and bought again: the position is kept
        if hit:
            lx[i], pend = True, 2                 # closed at this bar's close (one bar late)
        elif new:
            le[i], pend = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
