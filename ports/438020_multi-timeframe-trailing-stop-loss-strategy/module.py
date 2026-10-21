"""Four-timeframe ATR trailing-stop agreement, broker days: the trailing-stop state of the daily bars and of the day's last 2-, 3- and 4-hour bars, all long goes long, all short goes short; a long closes when the
sum turns zero or negative, a short when it turns zero or positive.
Port of FMZ strategy #438020 "Multi Timeframe Trailing Stop Loss Strategy" (MTF TrailingSL [QN]).

FMZ source id: 438020

Source
    https://www.fmz.com/strategy/438020 (PineScript v4, FMZ last modified 2024-01-08 11:24:24).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 149-238), ATR 14 x 2; TF2 "120", TF3 "180", TF4 "240" (on a 1-day chart); date window 2016-2100
    tsl(): long_signal = pos[1] != 1 and high > tsl[1];  short_signal = pos[1] != -1 and low < tsl[1];  tsl = high + 2 ATR on a short signal, low - 2 ATR on a long one, else ratcheted (max / min) by side
    tsl_k = tsl() on the chart and security(tickerid, "120" / "180" / "240", tsl());  pos_k = -1 if low <= tsl_k, 1 if high >= tsl_k, else pos_k[1] (daily high / low)
    total == 4 -> entry long;  total == -4 -> entry short;  total <= 0 -> close long;  total >= 0 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2-, 3- and 4-hour values requested from a daily chart are the day's LAST bar of that size (a
      lower time frame returns its last bar inside the chart bar, as #436765), counted from the broker
      day's start (17:00 America/New_York): 12, 8 and 6 per day; tsl() and its ATR(14) run on each such
      series. The nz() seeds of the source (a first trailing value of 0) are kept; a na ATR gives na
      levels, as in Pine. The daily high and low are compared with each level. The close of the opposite
      side acts on the position held at the bar close; on a bar where the sum is 4 (-4) a short (long) is
      reversed. REVERSAL INTENDED. The 100 % of equity size is sizing. The date window covers all data.
      Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing levels on four bar sizes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_438020_mtf_atr_trailing_agreement"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [2.0, 3.0],
    "atr_length": [14, 28],
}
DEFAULT_PARAMS = {"atr_mult": 2.0, "atr_length": 14, "tf2_minutes": 120, "tf3_minutes": 180,
                  "tf4_minutes": 240}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _tr(h, lo, c):
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _tsl(h, lo, c, mult, n):
    """The script's tsl(): ATR trailing level with its own position state (nz() seeds kept)."""
    slv = (mult * _rma(_tr(h, lo, c), n)).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    out = np.full(m, np.nan)
    pos = 0
    for i in range(m):
        t1 = out[i - 1] if i > 0 and not np.isnan(out[i - 1]) else 0.0
        ls = pos != 1 and hv[i] > t1
        ss = pos != -1 and lv[i] < t1
        if ss:
            out[i] = hv[i] + slv[i]
        elif ls:
            out[i] = lv[i] - slv[i]
        elif pos == 1:
            out[i] = _nmax(lv[i] - slv[i], t1)
        elif pos == -1:
            out[i] = _nmin(hv[i] + slv[i], t1)
        else:
            out[i] = t1
        pos = 1 if ls else (-1 if ss else pos)
    return pd.Series(out, index=h.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    since = ny - ny.normalize()
    for k in (2, 3, 4):
        # k-th time frame bars counted from each broker day's start (17:00 America/New_York)
        mos = since // pd.Timedelta(minutes=int(p["tf%d_minutes" % k]))
        bk = df.groupby([lab, np.asarray(mos)]).agg({"high": "max", "low": "min", "close": "last"})
        lv = _tsl(bk["high"], bk["low"], bk["close"], float(p["atr_mult"]), int(p["atr_length"]))
        day = lv.index.get_level_values(0)
        lv = lv[~day.duplicated(keep="last")]            # the day's last bar of that size
        lv.index = lv.index.get_level_values(0)
        bars["tsl%d" % k] = lv
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    levels = [_tsl(h, lo, c, float(p["atr_mult"]), int(p["atr_length"])).to_numpy()]
    levels += [bars_df["tsl%d" % k].to_numpy(dtype=float) for k in (2, 3, 4)]
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    total = np.zeros(m)
    for t in levels:
        st = 0.0
        for i in range(m):
            st = -1.0 if lv[i] <= t[i] else (1.0 if hv[i] >= t[i] else st)
            total[i] += st
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if total[i] == 4 and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif total[i] == -4 and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
        elif pos == 1 and total[i] <= 0:
            lx[i], pos = True, 0
        elif pos == -1 and total[i] >= 0:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
