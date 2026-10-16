"""Noro bottom score with an RSI filter, long only, broker days: when at least 3 of six bottom signals (Vix Fix spike,
locomotive, CVI, UCS, RSI(2) < 10, pin bar) agree under the SMA 25 and RSI 14 is below 35, go long; RSI 14 crossing
down through 70 closes the long.
Port of FMZ strategy #429577 "The Multi Timeframe Bottom Reversal Strategy" (Noro's BottomSensivity v0.6 strategy + rsi + Alarm).

FMZ source id: 429577

Source
    https://www.fmz.com/strategy/429577 (PineScript v4, FMZ last modified 2023-10-18 12:27:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-268), sensitivity 3, SMA 25, locomotive 3 bars, RSI 14 35 / 70
    score = wvf spike + locomotive + CVI turn + UCS long + rsi2 < 10 + pin bar; bottom = high < sma25 and score >= 3
    bottom and rsi(close,14) < 35 -> entry long; crossunder(rsi(close,14), 70) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each component as the source: Vix Fix 22 / BB 20 x 2 / range 50 x 0.85; locomotive = a green bar
      after 2 (here 3) red bars; CVI = (close - sma(hl2,3)) / (sma(atr(3),3) x sqrt 3) leaving <= -0.51;
      UCS = SMI < -35 with the 3-bar momentum turning up; pin bar after a red bar.
    * "Only red candles" is off; the SMA filter is on. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ratios, ATR-normalised indicators and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429577_noro_bottom_score_rsi"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "botsens": [3, 2],
    "oversold": [35, 45],
}
DEFAULT_PARAMS = {"botsens": 3, "smalen": 25, "bars": 3, "oversold": 35, "overbought": 70}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["smalen"])).mean()
    hc = c.rolling(22).max()
    wvf = (hc - lo) / hc * 100
    upper = wvf.rolling(20).mean() + 2 * wvf.rolling(20).std(ddof=0)
    vix = ((wvf >= upper) | (wvf >= wvf.rolling(50).max() * 0.85)).astype(int)
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index)
    nb = int(p["bars"])
    loco = ((bar == 1) & (bar.shift(1) == -1) & (bar.shift(2) == -1) & ((bar.shift(3) == -1) | (nb < 3))
            & ((bar.shift(4) == -1) | (nb < 4))).astype(int)
    body = (c - o).abs()
    up_sh = np.where(o > c, h - o, h - c)
    dn_sh = pd.Series(np.where(o > c, c - lo, o - lo), index=c.index)
    pin = ((o.shift(1) > c.shift(1)) & (body.shift(1) > body) & (dn_sh > 0.5 * body)
           & (dn_sh > 2 * pd.Series(up_sh, index=c.index))).astype(int)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    vol = _rma(tr, 3).rolling(3).mean()
    cvi = (c - ((h + lo) / 2).rolling(3).mean()) / (vol * np.sqrt(3))
    b1 = cvi <= -0.51
    cvib = (b1.shift(1, fill_value=False) & ~b1).astype(int)
    ll, hh = lo.rolling(5).min(), h.rolling(5).max()
    e2 = lambda x: x.ewm(span=3, adjust=False).mean().ewm(span=3, adjust=False).mean()  # noqa: E731
    avgrel, avgdiff = e2(c - (hh + ll) / 2), e2(hh - ll)
    smi = (avgrel / (avgdiff / 2) * 100).where(avgdiff != 0, 0.0)
    mom = (c - c.shift(3)) / c.shift(3) * 1000
    ucs = ((smi < -35) & (mom > 0) & (mom.shift(1) < 0)).astype(int)
    d = c.diff()
    up2, dn2 = _rma(d.clip(lower=0), 2), _rma((-d).clip(lower=0), 2)
    r2 = pd.Series(np.where(dn2 == 0, 100.0, np.where(up2 == 0, 0.0, 100 - 100 / (1 + up2 / dn2))), index=c.index)
    rsib = (r2.where(up2.notna() & dn2.notna()) < 10).astype(int)
    score = vix + loco + cvib + ucs + rsib + pin
    bottom = (h < sma) & (score >= p["botsens"])
    r14 = _rsi(c, 14)
    long_e = (bottom & (r14 < p["oversold"])).astype(bool)
    long_x = ((r14 < p["overbought"]) & (r14.shift(1) >= p["overbought"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
