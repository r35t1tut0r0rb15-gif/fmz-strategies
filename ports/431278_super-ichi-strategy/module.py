"""LuxAlgo SuperIchi pull-back entries, broker days: Tenkan over Kijun, the close over the Tenkan and the Kijun over the
displaced span A, with a green cloud and a pull-back under both lines within 5 bars, goes long (mirror short); the stop
is the 15-bar swing low or 1 ATR under the close, whichever is lower, and the target twice that distance.
Port of FMZ strategy #431278 "Super Ichi Strategy" (SuperIchi Strategy).

FMZ source id: 431278

Source
    https://www.fmz.com/strategy/431278 (PineScript v5, FMZ last modified 2023-11-06 16:32:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 275-439), SuperIchi 9 x 2 / 26 x 4 / 52 x 6, displacement 26; swing 15, ATR 14 x 1, R:R 2, pull-back 5
    avg(src, len, mult): SuperTrend bands of hl2 +- mult x ATR(len); the mean of the running max / min of src per trend
    tenkan = avg(close, 9, 2); kijun = avg(close, 26, 4); senkouA = (kijun + tenkan) / 2; senkouB = avg(close, 52, 6)
    long = tenkan > kijun and close > tenkan and kijun > senkouA[25] and senkouA[25] > senkouB[25]
           and barssince(close < kijun and close < tenkan) <= 5 and not long -> entry long, exit(stop, limit) (mirror short)
    longSl = min(close - ATR(14), lowest(low, 15));  longTp = close + 2 (close - longSl)

Interpretation choices (Pine rules in SURVEY_README.md)
    * avg() is ported line for line; math.max / math.min with an na argument give na, as in Pine.
      The span values are read 25 bars back (offset - 1), as the strategy reads them.
    * The stop and target are set at the signal and kept (strategy.exit on the entry bar only); as
      fractions of the signal close, shifted one bar. An entry needs no position on its own side and
      may reverse the other: REVERSAL INTENDED. "Long" / "short" state follows the house bracket on
      bars. The date range (2022 only) is the author's window: dropped.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR-banded averages, swing extremes and a reward ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 2 % account-risk quantity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431278_superichi_pullback"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing_len": [15, 30],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"swing_len": 15, "rr": 2.0, "atr_len": 14, "atr_mult": 1.0, "pullback": 5, "tenkan": 9,
                  "tenkan_mult": 2.0, "kijun": 26, "kijun_mult": 4.0, "span_b": 52, "span_b_mult": 6.0, "offset": 26}


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
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = np.asarray(x, dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _pmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _pmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _avg(src, hl2, tr, n, mult):
    """The source's avg(): SuperTrend-style bands and the running max / min of src per trend."""
    atr = _rma(tr, n) * mult
    m = len(src)
    out = np.full(m, np.nan)
    upper = lower = 0.0
    os_, mx, mn = 0, np.nan, np.nan
    spt_p = np.nan
    for i in range(m):
        up, dn = hl2[i] + atr[i], hl2[i] - atr[i]
        s1 = src[i - 1] if i else np.nan
        upper = _pmin(up, upper) if s1 < upper else up
        lower = _pmax(dn, lower) if s1 > lower else dn
        os_ = 1 if src[i] > upper else (0 if src[i] < lower else os_)
        spt = lower if os_ == 1 else upper
        cross = i > 0 and ((src[i] > spt and s1 <= spt_p) or (src[i] < spt and s1 >= spt_p))
        mx_n = _pmax(src[i], mx) if cross else (_pmax(src[i], mx) if os_ == 1 else spt)
        mn_n = _pmin(src[i], mn) if cross else (_pmin(src[i], mn) if os_ == 0 else spt)
        mx, mn, spt_p = mx_n, mn_n, spt
        out[i] = (mx + mn) / 2
    return out


def _barssince_le(cond, k):
    m = len(cond)
    out = np.zeros(m, dtype=bool)
    last = -1
    for i in range(m):
        if cond[i]:
            last = i
        out[i] = last >= 0 and i - last <= k
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    tr = tr.to_numpy()
    cv = c.to_numpy(dtype=float)
    hl2 = ((h + lo) / 2).to_numpy()
    ten = _avg(cv, hl2, tr, int(p["tenkan"]), float(p["tenkan_mult"]))
    kij = _avg(cv, hl2, tr, int(p["kijun"]), float(p["kijun_mult"]))
    spb = _avg(cv, hl2, tr, int(p["span_b"]), float(p["span_b_mult"]))
    spa = (kij + ten) / 2
    off = int(p["offset"]) - 1
    m = len(cv)
    spa_d = np.concatenate((np.full(off, np.nan), spa[:m - off])) if off > 0 else spa
    spb_d = np.concatenate((np.full(off, np.nan), spb[:m - off])) if off > 0 else spb
    long_sen = (ten > kij) & (cv > ten) & (kij > spa_d)
    short_sen = (ten < kij) & (cv < ten) & (kij < spa_d)
    pb_l = _barssince_le((cv < kij) & (cv < ten), int(p["pullback"]))
    pb_s = _barssince_le((cv > kij) & (cv > ten), int(p["pullback"]))
    lc = long_sen & (spa_d > spb_d) & pb_l
    sc = short_sen & (spa_d < spb_d) & pb_s
    atr = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    sw = int(p["swing_len"])
    sw_lo, sw_hi = lo.rolling(sw).min().to_numpy(), h.rolling(sw).max().to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    rr = float(p["rr"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if lc[i] and pos != 1:
            d = (cv[i] - min(cv[i] - atr[i], sw_lo[i])) / cv[i]
            if d > 0:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, d, d * rr
                sl_arr[i], tp_arr[i] = s_, t_
        if sc[i] and pos != -1:
            d = (max(cv[i] + atr[i], sw_hi[i]) - cv[i]) / cv[i]
            if d > 0:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, d, d * rr
                sl_arr[i], tp_arr[i] = s_, t_
    le &= ~se
    return le, se, sl_arr, tp_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
