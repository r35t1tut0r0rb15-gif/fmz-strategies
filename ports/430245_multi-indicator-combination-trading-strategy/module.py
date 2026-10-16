"""ADX / DI+ / CCI / awesome-oscillator dip, broker days, long only: ADX 14 above 25 with DI+ under 10, CCI 20 under 0 and
the awesome oscillator under 0 goes long; DI+ above 25 closes the long.
Port of FMZ strategy #430245 "Multi indicator Combination Trading Strategy" (Strategy Niel).

FMZ source id: 430245

Source
    https://www.fmz.com/strategy/430245 (PineScript v3, FMZ last modified 2023-10-26 15:22:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-236), ADX 14 / DI 14, ADX > 25, DI+ < 10, CCI 20 < 0, AO (5 / 34 of hl2) < 0, sell when DI+ > 25
    buy = adx > 25 and DI+ < 10 and cci(close, 20) < 0 and (sma(hl2, 5) - sma(hl2, 34)) < 0 -> entry long
    sell = DI+ > 25 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ADX and DI as the source's dirmov (Wilder averages; fixnan carries the last DI over a zero true
      range). The entry and exit tests exclude each other (DI+ under 10 vs over 25).
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX / DI levels, a CCI and an oscillator sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: floor(equity / close) per entry stored in original_sizing.txt.
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

NAME = "fmz_430245_adx_di_cci_ao_dip_long"
FAMILY = "directional_movement"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_above": [25, 20],
    "di_below": [10, 15],
}
DEFAULT_PARAMS = {"adx_above": 25, "di_below": 10, "di_exit": 25, "cci_len": 20, "adx_len": 14, "di_len": 14,
                  "ao_fast": 5, "ao_slow": 34}


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
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, di_len, adx_len):
    up, down = h.diff(), -lo.diff()
    plus_dm = ((up > down) & (up > 0)).astype(float) * up.fillna(0.0)
    minus_dm = ((down > up) & (down > 0)).astype(float) * down.fillna(0.0)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, di_len).replace(0.0, np.nan)
    plus = _fixnan(100 * _rma(plus_dm, di_len) / atr)
    minus = _fixnan(100 * _rma(minus_dm, di_len) / atr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len), plus


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (src - ma) / (0.015 * dev.replace(0.0, np.nan))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    adx, plus = _dmi(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    hl2 = (h + lo) / 2
    ao = hl2.rolling(int(p["ao_fast"])).mean() - hl2.rolling(int(p["ao_slow"])).mean()
    cci = _cci(c, int(p["cci_len"]))
    long_e = ((adx > p["adx_above"]) & (plus < p["di_below"]) & (cci < 0) & (ao < 0)).astype(bool)
    long_x = (plus > p["di_exit"]).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
