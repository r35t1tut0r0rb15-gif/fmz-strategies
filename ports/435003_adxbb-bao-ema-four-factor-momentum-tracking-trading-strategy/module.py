"""Four-factor trend entries, broker days: EMA 5 above EMA 21, EMA 50 above EMA 200, Bollinger %B above 0.75, the Awesome
Oscillator above 2 price units (re-expressed as an ATR multiple) and ADX 14 above 15 go long; the mirror goes short
(reversing); each trade carries a 5 % stop and a 10 % target from the signal close.
Port of FMZ strategy #435003 "基于ADXBB-BAO和EMA的量化交易策略Four-factor-Momentum-Tracking-Trading-Strategy-Based-on-ADX-BB-B-AO-and-EMA" (ADX + BB %B + AO + EMA).

FMZ source id: 435003

Source
    https://www.fmz.com/strategy/435003 (PineScript v4, FMZ last modified 2023-12-11 16:24:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 159-224), EMA 5 / 21 / 50 / 200; BB 20 / 2 %B 0.75 / 0.25; AO > 2 / < -2; ADX 14 / 14 > 15; SL 5 %, TP 10 % of the close; start 2018
    long = ema5 > ema21 and ema50 > ema200 and bbr > 0.75 and ao > 2 and adx > 15 -> entry long, exit(stop = close (1 - 5 %), limit = close (1 + 10 %))
    short = mirror with bbr < 0.25 and ao < -2 -> entry short, exit(stop = close (1 + 5 %), limit = close (1 - 10 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the AO is in price units (sma(hl2, 5) - sma(hl2, 34)) and its level 2 is about
      0.002 x the daily Wilder ATR 14 of BTC in 2023: the port compares the AO with ao_atr x ATR.
    * The bracket is set from the signal close: sl_stop 0.05, tp_stop 0.10 of the fill (re-based). A
      repeated signal inside the trade re-issues the bracket at that bar's close: not expressible
      (mark trailing_stop_pending); the opening levels are kept. The start date is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket fixed at entry (re-issued levels approximated).
    2 generic: ADAPT, the price-unit AO level -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435003_four_factor_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [15, 25],
    "ao_atr": [0.002, 0.2],
}
DEFAULT_PARAMS = {"adx_min": 15, "ao_atr": 0.002, "bb_ob": 0.75, "bb_os": 0.25, "sl_pct": 0.05, "tp_pct": 0.10}


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


def _fixnan(v, index):
    """Pine fixnan: a NaN (or inf) takes the last valid value before it (past values only)."""
    out = np.array(v, dtype=float)
    last = np.nan
    for i in range(len(out)):
        if np.isfinite(out[i]):
            last = out[i]
        else:
            out[i] = last
    return pd.Series(out, index=index)


def _adx_atr(h, lo, c, n):
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    rma = lambda x: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    trur = rma(tr)
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    plus = _fixnan((100 * rma(pdm) / trur).to_numpy(), c.index)
    minus = _fixnan((100 * rma(ndm) / trur).to_numpy(), c.index)
    s = plus + minus
    return 100 * rma((plus - minus).abs() / s.where(s != 0, 1.0)), trur


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (5, 21, 50, 200)}
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    bbr = (c - (basis - dev)) / (2 * dev).replace(0.0, np.nan)
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    adx, atr = _adx_atr(h, lo, c, 14)
    lvl = float(p["ao_atr"]) * atr
    ok = adx > float(p["adx_min"])
    le = ((e[5] > e[21]) & (e[50] > e[200]) & (bbr > float(p["bb_ob"])) & (ao > lvl) & ok).astype(bool)
    se = ((e[5] < e[21]) & (e[50] < e[200]) & (bbr < float(p["bb_os"])) & (ao < -lvl) & ok).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
