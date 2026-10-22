"""RSI 14 crossing over 60 above its SMA 20 and rising, with the DMI outputs as named in the source, broker days, long only: entered from flat; a close at or over 2.5 ATR above, or at or under 1.5 ATR below, the last signal close closes.
Port of FMZ strategy #482773 "多指标趋势动量ATR目标价交易策略-Multi-Indicator-Trend-Momentum-ATR-Target-Trading-Strategy" (ADX & RSI Strategy with ATR Targets).

FMZ source id: 482773

Source
    https://www.fmz.com/strategy/482773 (PineScript v6, FMZ last modified 2025-02-27 17:51:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-160), DMI 14 / 14 (outputs bound as [adx, plusDI, minusDI]); RSI 14, SMA 20; ATR 14, target 2.5, stop 1.5
    [adx, plusDI, minusDI] = ta.dmi(14, 14);  adx > 18 and plusDI > minusDI and adx rising and rsi > sma(rsi, 20) and rsi rising and crossover(rsi, 60) -> entry Long (entryPrice := close, levels set)
    position > 0: close >= entry + 2.5 atr -> close Long;  close <= entry - 1.5 atr -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.dmi returns [+DI, -DI, ADX], so as written "adx" is +DI, "plusDI" is -DI and "minusDI" is the ADX:
      the filter is +DI over 18, -DI over the ADX and +DI rising. The target and stop are bar-close tests
      against levels from the last signal close (also re-set by a signal while the long is held), so they
      are exits in the loop, not broker stops; they act only on a long held into the bar. Long only. No
      sizing code. The source carries the Mozilla Public License 2.0 notice. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based ATR target / stop in the loop.
    2 generic: PASS, RSI 60 crossings with DMI and RSI trend filters.
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

NAME = "fmz_482773_rsi60_cross_dmi_as_named_close_atr_target_stop_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multiplier_target": [2.5, 4.0],
    "atr_multiplier_stop": [1.5, 3.0],
}
DEFAULT_PARAMS = {"atr_multiplier_target": 2.5, "atr_multiplier_stop": 1.5, "adx_length": 14, "rsi_length": 14,
                  "rsi_sma_length": 20, "atr_length": 14}


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
    return 100 - 100 / (1 + up / dn)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a_, b_, c_ = _dmi(bars_df, int(p["adx_length"]))      # bound as [adx, plusDI, minusDI], as written
    r = _rsi(c, int(p["rsi_length"]))
    rs = r.rolling(int(p["rsi_sma_length"])).mean()
    cond = ((a_ > 18) & (b_ > c_) & (a_ > a_.shift(1)) & (r > rs) & (r > r.shift(1))
            & (r > 60) & (r.shift(1) <= 60)).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    kt, ks = float(p["atr_multiplier_target"]), float(p["atr_multiplier_stop"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, tgt, stp = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if cond[i]:
            tgt, stp = cv[i] + atr[i] * kt, cv[i] - atr[i] * ks   # re-set also while a long is held
            if pos == 0:
                le[i], pend = True, 1
        if pos == 1 and (cv[i] >= tgt or cv[i] <= stp):
            lx[i], pend = True, 2
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
