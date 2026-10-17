"""RSI 14 crossing above 60 while rising above its SMA 20, with the DMI filter as the source destructures it, goes long;
closed when a close reaches 2.5 ATR above or 1.5 ATR below the signal close, long only, daily bars.
Port of FMZ strategy #482773 "多指标趋势动量ATR目标价交易策略-Multi-Indicator-Trend-Momentum-ATR-Target-Trading-Strategy" (ADX & RSI Strategy with ATR Targets).

FMZ source id: 482773

Source
    https://www.fmz.com/strategy/482773 (PineScript v6, FMZ last modified 2025-02-27 17:51:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-150), DMI 14 / 14, RSI 14 with SMA 20, ATR 14 (2.5 / 1.5)
    [adx, plusDI, minusDI] = ta.dmi(14, 14)  (ta.dmi returns [+DI, -DI, ADX])
    long = adx > 18 and plusDI > minusDI and adx rising and rsi > sma(rsi, 20) and rsi rising and crossover(rsi, 60)
    long -> target = close + 2.5 ATR, stop = close - 1.5 ATR, entry long
    while long: close >= target or close <= stop -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.dmi returns (+DI, -DI, ADX) but is unpacked as (adx, plusDI, minusDI), so the filter reads
      +DI > 18 and -DI > ADX and +DI rising: ported as written.
    * The target and stop are checked on closes with strategy.close: exit signals at the next open (rule 3; as
      #489638). The levels are overwritten by every signal, also while held (as written).
    * The checks run only once the position exists (from the fill bar). Long only. Signal module, no stops. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based exits.
    2 generic: PASS, DMI, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482773_rsi60_cross_dmi_close_atr_levels_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_mult": [2.5, 4.0],
    "sl_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"di_len": 14, "adx_len": 14, "rsi_len": 14, "rsi_sma": 20, "atr_len": 14,
                  "tp_mult": 2.5, "sl_mult": 1.5}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    di_p, di_m, adx_true = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    a, b, d = di_p, di_m, adx_true                 # the source's "adx", "plusDI", "minusDI"
    rsi = _rsi(c, int(p["rsi_len"]))
    cond = ((a > 18) & (b > d) & (a.diff() > 0) & (rsi > rsi.rolling(int(p["rsi_sma"])).mean()) & (rsi.diff() > 0)
            & (rsi > 60) & (rsi.shift(1) <= 60)).to_numpy()
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, pending = False, False
    tgt = stp = np.nan
    for i in range(m):
        if pending:
            held, pending = True, False          # filled at this bar's open
        if cond[i]:
            tgt, stp = cv[i] + atr[i] * p["tp_mult"], cv[i] - atr[i] * p["sl_mult"]
            if not held and i + 1 < m:
                le[i], pending = True, True
        if held and (cv[i] >= tgt or cv[i] <= stp):
            lx[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
