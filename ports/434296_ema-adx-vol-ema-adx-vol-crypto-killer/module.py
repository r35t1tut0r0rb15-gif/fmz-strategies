"""Broker days: Masanakamura ADX 21 over 20 with DI+ over DI-, a range filter (15 x 2.6 of the open) breakout with an up-run, the close above EMAs 8 / 13 / 21 / 34 / 55 and volume over 3.2 x its SMA 20 or 1.9 x its SMA 22 go long; the mirror set goes short; each trade has a 0.9 % target and a 4.2 % stop; reversing.
Port of FMZ strategy #434296 "EMA-ADX-VOL-加密货币杀手EMA-ADX-VOL-CRYPTO-KILLER" (EMA/ADX/VOL-CRYPTO KILLER [15M] (BabehDyo)).

FMZ source id: 434296

Source
    https://www.fmz.com/strategy/434296 (PineScript v4, FMZ last modified 2023-12-05 11:03:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 154-434), src open; ADX MASANAKAMURA 21, threshold 20; EMA 8 / 13 / 21 / 34 / 55; range filter 15 x 2.6; volume 3.2 x SMA 20, 1.9 x SMA 22; TP 0.9 %, SL 4.2 %
    L_basic = (L_adx and Volume_condt and L_RF and L_ema) or (L_adx and L_RF and L_ema and Volume_condt1) -> entry LONG;  S_basic mirror -> entry SHORT
    exit("TP_L", "LONG", profit = last_open x 0.9 % / mintick, limit = nLongs >= 1 ? avg x 1.009, loss = last_open x 4.2 % / mintick);  mirror for SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same BabehDyo template as #376261: the entries are the raw condition sets; the script's
      CondIni / nLongs machinery only sets the exit distances. nLongs never exceeds 1 (a second long
      condition needs a reset or a short in between), so the target is 0.9 % and the stop min(4.2, 4.2 x
      100 / 99) = 4.2 %. The target (limit at the average price x 1.009, priority over profit) is a scalar
      fraction of the fill; the stop is 4.2 % of the signal close from the entry, fixed at the signal close
      as a fraction of the fill (the script re-sends it each bar from its own anchor: mark
      trailing_stop_pending), as #376261. A bar with both sets takes the short (the later call). The title
      says 15M; the backtest header says 1d and is used (weird case). REVERSAL INTENDED. 100 % of equity
      and the commission are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, ADX, range filter, EMA stack and volume-spike confluence.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 10000, pyramiding 1, commission 0.03 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 3.2 x sma(volume, 20) or > 1.9 x sma(volume, 22); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_434296_adx_range_filter_ema_stack_volume_spike_pct_bracket_reversal"
FAMILY = "adx_volume_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "volume_f": [3.2, 2.0],
    "adx_th": [20.0, 25.0],
}
DEFAULT_PARAMS = {"volume_f": 3.2, "vol_len": 20, "volume_f1": 1.9, "vol_len1": 22, "adx_len": 21, "adx_th": 20.0,
                  "rf_per": 15, "rf_mult": 2.6, "tp": 0.009, "sl": 0.042}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _nz(v):
    return 0.0 if np.isnan(v) else v


def _adx_masanakamura(b, n):
    """The source's calcADX_Masanakamura: Wilder running sums with nz(), DX averaged by an SMA."""
    h, lo, c = (b[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    dip, dim = np.full(m, np.nan), np.full(m, np.nan)
    s_tr = s_p = s_m = 0.0
    for i in range(m):
        c1 = c[i - 1] if i else 0.0
        h1 = h[i - 1] if i else 0.0
        l1 = lo[i - 1] if i else 0.0
        tr = max(h[i] - lo[i], abs(h[i] - c1), abs(lo[i] - c1))
        dmp = max(h[i] - h1, 0.0) if h[i] - h1 > l1 - lo[i] else 0.0
        dmm = max(l1 - lo[i], 0.0) if l1 - lo[i] > h[i] - h1 else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        if s_tr != 0:
            dip[i], dim[i] = s_p / s_tr * 100, s_m / s_tr * 100
    dip_s, dim_s = pd.Series(dip, index=b.index), pd.Series(dim, index=b.index)
    dx = (dip_s - dim_s).abs() / (dip_s + dim_s) * 100
    return dip_s, dim_s, dx.rolling(n).mean()


def _range_filter(src, per, mult):
    """The source's Range_filter: smoothed range, ratcheting filter, up / down run counts (nz as written)."""
    avrng = (src - src.shift(1)).abs().ewm(span=per, adjust=False).mean()
    smr = (avrng.ewm(span=per * 2 - 1, adjust=False).mean() * mult).to_numpy(dtype=float)
    s = src.to_numpy(dtype=float)
    m = len(s)
    filt, up, dn = np.full(m, np.nan), np.zeros(m), np.zeros(m)
    fp, up_p, dn_p = np.nan, 0.0, 0.0
    for i in range(m):
        prev = _nz(fp)
        if s[i] > prev:
            f = prev if (s[i] - smr[i]) < prev else s[i] - smr[i]
        else:
            f = prev if (s[i] + smr[i]) > prev else s[i] + smr[i]
        u = up_p + 1 if f > fp else (0.0 if f < fp else up_p)
        d = dn_p + 1 if f < fp else (0.0 if f > fp else dn_p)
        filt[i], up[i], dn[i] = f, u, d
        fp, up_p, dn_p = f, u, d
    return smr, filt, up, dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    th = float(p["adx_th"])
    l_adx, s_adx = (dip > dim) & (adx > th), (dip < dim) & (adx > th)
    emas = [c.ewm(span=n, adjust=False).mean() for n in (8, 13, 21, 34, 55)]
    l_ema = np.logical_and.reduce([(e < c).to_numpy() for e in emas])
    s_ema = np.logical_and.reduce([(e > c).to_numpy() for e in emas])
    smr, filt, up, dn = _range_filter(o, int(p["rf_per"]), float(p["rf_mult"]))
    l_rf = (h.to_numpy() > filt + smr) & (up > 0)
    s_rf = (lo.to_numpy() < filt - smr) & (dn > 0)
    vc = (v > v.rolling(int(p["vol_len"])).mean() * float(p["volume_f"])).to_numpy()
    vc1 = (v > v.rolling(int(p["vol_len1"])).mean() * float(p["volume_f1"])).to_numpy()
    lb = l_adx.to_numpy() & l_rf & l_ema & (vc | vc1)
    sb = s_adx.to_numpy() & s_rf & s_ema & (vc | vc1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lb & ~sb, index=ix), false, pd.Series(sb, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    sl_f = float(p["sl"]) * c.shift(1) / o   # 4.2 % of the signal close from the entry
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
