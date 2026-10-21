"""RSI-3 dips above the SMA 200, broker days, long only: from flat, a close above the SMA 200 but under the SMA 10 with the RSI 3 under 30 buys; a 20 % stop from the entry protects it, and a close above the
SMA 10 that is under the previous low closes it.
Port of FMZ strategy #437774 "Golden Ratio Moving Average Trading Strategy" (聖杯).

FMZ source id: 437774

Source
    https://www.fmz.com/strategy/437774 (PineScript v5, FMZ last modified 2024-01-05 14:21:52).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 163-195), SMA 200 / 10, stop 20 %, profit 5 % (unused); date filter true
    close > sma 200 and close < sma 10 and position_size == 0 and rsi(close, 3) < 30 -> entry long;  while long: exit(stop = (1 - 20 %) x avg price);  close > sma 10 and close < low[1] -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed at entry: sl_stop = 0.20 (a scalar fraction of the fill). The profit input is not
      used by any order. "Flat" follows the house bracket (the loop marks the trade closed when a bar's low
      reaches the stop from the fill price, or the close rule fires). Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. The 100 % of equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ
      = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, SMA sides and RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the unused profit input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_437774_rsi3_dip_above_sma200_long"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop": [0.2, 0.1],
    "mashort": [10, 5],
}
DEFAULT_PARAMS = {"stop": 0.2, "mashort": 10, "malong": 200}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    ml = c.rolling(int(p["malong"])).mean()
    ms = c.rolling(int(p["mashort"])).mean()
    r = _rsi(c, 3)
    ent = ((c > ml) & (c < ms) & (r < 30)).to_numpy()
    ext = ((c > ms) & (c < lo.shift(1))).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl = float(p["stop"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    pend = False
    for i in range(m):
        if pend and pos == 1:                            # the close fills at this bar's open
            pos = 0
        pend = False
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - sl):
            pos = 0
        if pos == 1 and i >= entry_i and ext[i]:
            lx[i] = True
            pend = True
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i] = True
            pos, entry_i = 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"])}


def portfolio_kwargs(**params):
    return {}
