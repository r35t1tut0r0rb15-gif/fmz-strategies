"""Broker days, long only: latched flags set when the close crosses under the lower Bollinger band (20, 2), RSI 3 crosses over 15 and the stochastic (10, 3) crosses over 15, with a rising EMA 10 of MFI 14, go long; latched flags for a close crossing under the upper band and RSI 3 crossing under 85 close it; each flag is cleared by the opposite event.
Port of FMZ strategy #481117 "Multi Indicator Trend Divergence Quantitative Trading Strategy" (Izmir Stratejisi).

FMZ source id: 481117

Source
    https://www.fmz.com/strategy/481117 (PineScript v5, FMZ last modified 2025-02-08 16:08:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 125-205), BB 20 x 2; RSI 3 (85 / 15); stoch 10 / 3; MFI 14 with EMA 10 trend; latched flags
    bbBreakdown := crossunder(close, lower) ? true : bbBreakdown;  rsiBreakout := crossover(rsi, 15) ? true : ...;  stochBreakout := crossover(k, 15) ? true : ...;  buy = all three and ema(mfi, 10) > ema(mfi[1], 10)
    bbBreakup := crossunder(close, upper) ? true : ...;  rsiBreakdown := crossunder(rsi, 85) ? true : ...;  sell = bbBreakup and rsiBreakdown
    after the signals: crossunder(close, lower) clears bbBreakup;  crossover(rsi, 15) clears rsiBreakdown;  crossover(k, 15) clears stochBreakdown;  crossunder(close, upper) clears bbBreakdown;  crossunder(rsi, 85) clears rsiBreakout;  crossunder(k, 85) clears stochBreakout

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags latch until the opposite event clears them, and the signals read them before that bar's
      clears. ta.mfi(close, 14) sums volume x close over up / down closes; "mfi[1]" makes the trend the
      EMA of MFI against the EMA of the previous bar's MFI. The stochastic sell flag is computed but not
      used (commented out). The close acts only on a position the bar's entry leaves unchanged; an entry
      while long adds nothing. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, latched Bollinger / RSI / stochastic oversold-recovery set-ups with MFI trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in the MFI 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481117_latched_bb_rsi3_stoch_mfi_trend_long_only"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_lo": [15.0, 20.0],
    "rsi_hi": [85.0, 80.0],
}
DEFAULT_PARAMS = {"rsi_lo": 15.0, "rsi_hi": 85.0, "st_lo": 15.0, "st_hi": 85.0}


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
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _xo(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    upb, lob = basis + dev, basis - dev
    r = _rsi(c, 3)
    ll, hh = lo.rolling(10).min(), h.rolling(10).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(3).mean()
    chg = c.diff()
    pos_f = (v * c.where(~(chg <= 0), 0.0)).rolling(14).sum()
    neg_f = (v * c.where(~(chg >= 0), 0.0)).rolling(14).sum()
    mfi = 100.0 - 100.0 / (1.0 + pos_f / neg_f.where(neg_f != 0))
    mfi_up = (mfi.ewm(span=10, adjust=False).mean() > mfi.shift(1).ewm(span=10, adjust=False).mean()).to_numpy()
    rl, rh = pd.Series(float(p["rsi_lo"]), index=c.index), pd.Series(float(p["rsi_hi"]), index=c.index)
    sl_, sh_ = pd.Series(float(p["st_lo"]), index=c.index), pd.Series(float(p["st_hi"]), index=c.index)
    c_dn_lo, c_dn_up = _xo(lob, c), _xo(upb, c)            # close crossing under the lower / upper band
    r_up_lo, r_dn_hi = _xo(r, rl), _xo(rh, r)
    k_up_lo, k_dn_hi = _xo(k, sl_), _xo(sh_, k)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bb_dn = rsi_bo = st_bo = bb_up = rsi_bd = st_bd = False
    pos = 0
    for i in range(m):
        bb_dn = True if c_dn_lo[i] else bb_dn
        rsi_bo = True if r_up_lo[i] else rsi_bo
        st_bo = True if k_up_lo[i] else st_bo
        buy = bb_dn and rsi_bo and st_bo and mfi_up[i]
        bb_up = True if c_dn_up[i] else bb_up
        rsi_bd = True if r_dn_hi[i] else rsi_bd
        st_bd = True if k_dn_hi[i] else st_bd
        sell = bb_up and rsi_bd
        if c_dn_lo[i]:
            bb_up = False
        if r_up_lo[i]:
            rsi_bd = False
        if k_up_lo[i]:
            st_bd = False
        if c_dn_up[i]:
            bb_dn = False
        if r_dn_hi[i]:
            rsi_bo = False
        if k_dn_hi[i]:
            st_bo = False
        if pos == 0:
            if buy:
                le[i], pos = True, 1
        elif sell:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
