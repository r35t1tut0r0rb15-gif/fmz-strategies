"""An eight-vote score (MACD 12 / 29 / 9 state and histogram, smoothed RSI 14, EMA 5 / 26, an ADX-like trend strength with the close against its EMA 3, smoothed %R 14, a volume close-location flow 14 and an ATR 5 x 2 trailing state) sets a level at 1.005 x the high when it turns positive and 0.995 x the low when it turns negative; the high above an up level goes long, the low under a down level closes; broker days, long only.
Port of FMZ strategy #432754 "Multi timeframe Adaptive Tracking Stop Loss Strategy" (Jigga - Survival Level (jigneshjc)).

FMZ source id: 432754

Source
    https://www.fmz.com/strategy/432754 (PineScript v5, FMZ last modified 2023-11-21 11:07:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 134-259), MACD 12 / 29 / 9; RSI 14 (EMA 3), levels 58 / 42; EMA 5 / 26; DMI / ADX 14 with EMA 5; %R 14 (EMA 3); flow 14, +-0.1; ATR 5 x 2.0 trailing state
    p = fitur + mitur + ritur + circuits + trialPoints + virar + chikar + sitar;  currentPNew = 0 on a sign change, else p
    LTN = currentPNew[1] < 0 and currentPNew >= 0 ? high x 1.005 : currentPNew[1] > 0 and currentPNew <= 0 ? low x 0.995 : LTN[1] (colour green / red alike)
    high > LTN and colour green -> entry Buy;  low < LTN and colour red -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The obfuscated names are read as written: kahachale = DMI 14 (rma of the true range, fixnan on the
      DI lines), trial = 100 x rma(|DI+ - DI-| / sum, 14), _pr = %R of the close against highest(high, 14)
      / lowest(low, 14), the last block is an ATR 5 x 2 trailing state from hl2. "LTN := nz(LTN) ? 0 : ..."
      tests the 0.0 just assigned, so the level always takes the second branch. The level and its colour
      are na until the first sign change, so no entry comes before it. tradeRunning feeds plots only.
      Comparisons with na are false, as Pine's. The close comes after the entry; the two cannot hold on one
      bar (opposite colours). Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, multi-indicator score with a breakout level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the close-location flow sum(ad, 14) / sum(volume, 14) (one of the eight votes); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432754_eight_vote_score_flip_level_breakout_long"
FAMILY = "indicator_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "macd_slow": [29, 26],
    "level_pct": [0.005, 0.01],
}
DEFAULT_PARAMS = {"macd_slow": 29, "level_pct": 0.005}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


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


def _vote3(x, hi, lo):
    return np.where(x > hi, 1, np.where(x < lo, -1, 0))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    # DMI 14 and the trend-strength line
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    atr14 = _rma(tr, 14)
    dip = _fixnan(100 * _rma(pdm, 14) / atr14)
    dim = _fixnan(100 * _rma(mdm, 14) / atr14)
    s = dip + dim
    sig = 100 * _rma((dip - dim).abs() / s.where(s != 0, 1.0), 14)
    trial_inc = (sig > _ema(sig, 5)).to_numpy()
    # MACD 12 / 29 / 9
    mac = _ema(c, 12) - _ema(c, int(p["macd_slow"]))
    msig = _ema(mac, 9)
    hist = mac - msig
    fitur = np.where(mac > 0, np.where(mac > msig, 1, 0), np.where(mac > msig, 0, -1))
    mitur = np.where(hist >= 0, np.where(hist > hist.shift(1), 1, 0), np.where(hist > hist.shift(1), 0, -1))
    # RSI 14 smoothed by EMA 3
    d = c.diff()
    ru, rd = _rma(d.clip(lower=0), 14), _rma((-d).clip(lower=0), 14)
    rsi = (100 - 100 / (1 + ru / rd.where(rd != 0))).where(ru != 0, 0.0).where(rd != 0, 100.0).where(ru.notna() & rd.notna())
    ritur = _vote3(_ema(rsi, 3), 58, 42)
    circuits = np.where(_ema(c, 5) > _ema(c, 26), 1, -1)
    trial_pts = np.where(trial_inc, np.where(c > _ema(c, 3), 1, -1), 0)
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    pr = 100 * (c - hh) / (hh - ll).where(hh != ll)
    virar = _vote3(_ema(pr, 3), -42, -58)
    ad = pd.Series(np.where(((c == h) & (c == lo)) | (h == lo), 0.0,
                            (2 * c - lo - h) / (h - lo).where(h != lo)), index=c.index) * v
    sv = v.rolling(14).sum()
    chikar = _vote3(ad.rolling(14).sum() / sv.where(sv != 0), 0.1, -0.1)
    # ATR 5 x 2 trailing state from hl2
    atr5 = _rma(tr, 5).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    sitar = np.zeros(m)
    up_p = dn_p = np.nan
    om = 1
    for i in range(m):
        ur, dr = hl2[i] - 2.0 * atr5[i], hl2[i] + 2.0 * atr5[i]
        u1 = ur if np.isnan(up_p) else up_p
        d1 = dr if np.isnan(dn_p) else dn_p
        c1 = cv[i - 1] if i else np.nan
        uf = max(ur, u1) if c1 > u1 else ur
        df_ = min(dr, d1) if c1 < d1 else dr
        om = 1 if (om == -1 and cv[i] > d1) else (-1 if (om == 1 and cv[i] < u1) else om)
        sitar[i] = om
        up_p, dn_p = uf, df_
    score = fitur + mitur + ritur + circuits + trial_pts + virar + chikar + sitar
    sc = pd.Series(score, index=c.index)
    s1 = sc.shift(1)
    pn = sc.where(~(((sc >= 0) & (s1 <= 0)) | ((sc <= 0) & (s1 >= 0))), 0.0)
    pn1 = pn.shift(1)
    f_up = ((pn1 < 0) & (pn >= 0)).to_numpy()
    f_dn = ((pn1 > 0) & (pn <= 0)).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = float(p["level_pct"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lvl, clr, pos = np.nan, 0, 0
    for i in range(m):
        if f_up[i]:
            lvl, clr = hv[i] * (1 + k), 1
        elif f_dn[i]:
            lvl, clr = lv[i] * (1 - k), -1
        if pos == 0 and clr == 1 and hv[i] > lvl:
            le[i], pos = True, 1
        elif pos == 1 and clr == -1 and lv[i] < lvl:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
