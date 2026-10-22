"""CCI (14) crossings of +-100 confirmed by the DMI, the ADX over 20 and the MACD (24, 52, 9), daily bars: the CCI crossing over -100 with DI+ above DI-, the MACD over its signal and the ADX over 20 goes
long, the mirror at +100 goes short; the CCI crossing over +100 closes a long, under -100 closes a short; reversing.
Port of FMZ strategy #449812 "CCIDMIMACDADX Multi Indicator Combination Strategy CCI DMI MACD ADX" (CCI, DMI, MACD, and ADX Strategy).

FMZ source id: 449812

Source
    https://www.fmz.com/strategy/449812 (PineScript v5, FMZ last modified 2024-04-29 14:06:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-161), CCI 14, levels 100 / -100; DMI 14 / 14 with ADX threshold 20; MACD 24 / 52 / 9
    crossover(cci, -100) and di+ > di- and macd > signal and adx > 20 -> entry Buy;  crossover(cci, 100) -> close Buy;  crossunder(cci, 100) and di- > di+ and macd < signal and adx > 20 -> entry Sell;  crossunder(cci, -100) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules of #449713 with an ADX filter, on daily bars. The calls run in the script's order: a
      close acts only on a position held into the bar and not reversed by that bar's entry. ta.cci uses
      the mean absolute deviation; ta.dmi uses Wilder smoothing (ADX = rma of the DX). REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI crossings with DMI, ADX and MACD confirmation, CCI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449812_cci_cross_dmi_adx_macd_confirm_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [14, 20],
    "adx_min": [20.0, 25.0],
}
DEFAULT_PARAMS = {"cci_len": 14, "adx_min": 20.0, "level": 100.0, "dmi_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    cci = (c - ma) / (0.015 * md)
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    k = int(p["dmi_len"])
    atr = _rma(tr, k)
    dip, dim = 100 * _rma(pdm, k) / atr, 100 * _rma(mdm, k) / atr
    adx = 100 * _rma((dip - dim).abs() / (dip + dim), k)
    strong = adx > float(p["adx_min"])
    macd = c.ewm(span=24, adjust=False).mean() - c.ewm(span=52, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lv = float(p["level"])
    c1 = cci.shift(1)
    with np.errstate(invalid="ignore"):
        buy = ((cci > -lv) & (c1 <= -lv) & (dip > dim) & (macd > sig) & strong).to_numpy()
        bx = ((cci > lv) & (c1 <= lv)).to_numpy()
        sell = ((cci < lv) & (c1 >= lv) & (dim > dip) & (macd < sig) & strong).to_numpy()
        sxc = ((cci < -lv) & (c1 >= -lv)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            le[i], new = True, 1
        if bx[i] and pos == 1 and new == 1:          # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if sell[i] and new != -1:
            se[i], le[i], lx[i], new = True, False, False, -1
        if sxc[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
