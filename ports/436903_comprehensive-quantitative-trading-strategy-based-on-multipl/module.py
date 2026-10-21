"""SuperTrend, QQE band and Trend Indicator A-V2 agreement, broker days, long only: while the close[2]-driven SuperTrend is up, the previous smoothed RSI sits above its QQE band and the previous EMA 52 of closes is at
or above the EMA 52 of opens, the long is held; otherwise it is closed.
Port of FMZ strategy #436903 "Comprehensive Quantitative Trading Strategy Based on Multiple Indicators" (Comprehensive Strategy).

FMZ source id: 436903

Source
    https://www.fmz.com/strategy/436903 (PineScript v4, FMZ last modified 2023-12-28 17:46:45).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 195-261), only long on; SuperTrend ATR 9 x 3.9 of hl2; QQE RSI 6 / smoothing 5 / factor 3; TIA-V2 EMA 52
    upST / dnST ratchet on close[2] > upST[1] / close[2] < dnST[1];  trendST flips on close[2] > dnST[1] / close[2] < upST[1]
    qqeCondition = RsiMa[1] - 50 > upper[1] ? true : RsiMa[1] - 50 < lower[1] ? false : na (band = sma(RsiMa - 50, 50) +- 0.35 stdev);  TIA = ema(close, 52)[1] >= ema(open, 52)[1];  OnlyLong: long cond -> entry Buy, else close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend is the script's own variant (it tests close[2], not the close), ported as written.
      qqeCondition is true / false / na; na fails both the long test and the short test. The QQE's
      darQQE line is computed but not used by the orders. The long is re-sent on every bar of the
      condition (pyramiding 0 ignores repeats) and closed on every other bar. The both-sides branch is off
      by default (OnlyLong true) and not ported. Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR SuperTrend, RSI band and EMA comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG436903 (2 members, best partner #441988, Jaccard 0.959); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436903_supertrend_qqe_tia_long_state"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_mult": [3.9, 2.5],
    "tia_len": [52, 26],
}
DEFAULT_PARAMS = {"st_mult": 3.9, "tia_len": 52, "st_period": 9, "rsi_len": 6, "rsi_smooth": 5, "band_len": 50,
                  "band_k": 0.35}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _trend_st(bars_df, n, mult):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    src = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn, tr_ = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            u = src[i] - mult * atr[i]
            d = src[i] + mult * atr[i]
            c2 = cv[i - 2] if i >= 2 else np.nan
            if i >= 1 and c2 > up[i - 1]:
                u = max(u, up[i - 1]) if not np.isnan(u) else np.nan
            if i >= 1 and c2 < dn[i - 1]:
                d = min(d, dn[i - 1]) if not np.isnan(d) else np.nan
            up[i], dn[i] = u, d
            t = tr_[i - 1] if i >= 1 else 1.0
            if t == -1 and i >= 1 and c2 > dn[i - 1]:
                t = 1.0
            elif t == 1 and i >= 1 and c2 < up[i - 1]:
                t = -1.0
            tr_[i] = t
    return tr_


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    st = _trend_st(bars_df, int(p["st_period"]), float(p["st_mult"]))
    rma_ = _rsi(c, int(p["rsi_len"])).ewm(span=int(p["rsi_smooth"]), adjust=False).mean()
    x = rma_ - 50
    bl = int(p["band_len"])
    basis = x.rolling(bl).mean()
    dev = float(p["band_k"]) * x.rolling(bl).std(ddof=0)
    qqe_true = (x.shift(1) > (basis + dev).shift(1)).to_numpy()
    n = int(p["tia_len"])
    tia = (c.ewm(span=n, adjust=False).mean().shift(1) >= o.ewm(span=n, adjust=False).mean().shift(1)).to_numpy()
    cond = (st == 1) & qqe_true & tia
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(cond, index=ix), pd.Series(~cond, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
