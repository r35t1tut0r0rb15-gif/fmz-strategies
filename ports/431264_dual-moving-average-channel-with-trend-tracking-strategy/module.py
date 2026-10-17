"""SMA 7 / 14 with DMI, broker days, long only: the first bar with +DI over -DI, the SMA 7 over the SMA 14 and ADX over 20
goes long; the first bar of the mirror condition closes the long.
Port of FMZ strategy #431264 "Dual Moving Average Channel with Trend Tracking Strategy" ((S)MA+ADX+DI+time).

FMZ source id: 431264

Source
    https://www.fmz.com/strategy/431264 (PineScript v4, FMZ last modified 2023-11-06 15:41:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 150-193), SMA 7 / 14, DMI 14 / 14, key level 20
    buy = di+ > di- and sma7 > sma14 and adx > 20;  sell = di+ < di- and sma7 < sma14 and adx > 20
    buy and not buy[1] -> entry "L";  sell and not sell[1] -> close "L"

Interpretation choices (Pine rules in SURVEY_README.md)
    * dmi() as Pine's (Wilder rma of +DM / -DM and the true range; ADX the rma of DX). The window()
      is always true. buy and sell cannot meet on one bar. Long only; Opposite entries cannot occur.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMAs and DMI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431264_sma_dmi_long"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [14, 30],
    "key_level": [20, 25],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 14, "di_len": 14, "adx_len": 14, "key_level": 20}


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
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _dmi(bars, dilen, adxlen):
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    trr = _rma(tr, dilen)
    plus, minus = 100 * _rma(plus_dm, dilen) / trr, 100 * _rma(minus_dm, dilen) / trr
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adxlen)
    return plus, minus, adx


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    plus, minus, adx = _dmi(bars_df, int(p["di_len"]), int(p["adx_len"]))
    k = float(p["key_level"])
    buy = (plus - minus > 0) & (f > s) & (adx > k)
    sell = (plus - minus < 0) & (f < s) & (adx > k)
    b_t = (buy & ~buy.shift(1, fill_value=False)).to_numpy()
    s_t = (sell & ~sell.shift(1, fill_value=False)).to_numpy()
    m = len(b_t)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if b_t[i]:
            pos = 1
        elif s_t[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
