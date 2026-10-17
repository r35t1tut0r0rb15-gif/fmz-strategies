"""Stochastic RSI below 20 turning up with a positive K-D / K-MACD spread, long only from flat, with a 2.5 ATR stop
and target from the entry and an exit when the stochastic RSI above 80 turns down, daily bars.
Port of FMZ strategy #482816 "动态自适应多指标交叉策略结合SRSI和MACD的智能风控系统-Dynamic-Adaptive-Multi-Indicator-Crossing-Strategy-with-SRSI-MACD-Smart-Risk-Control-System" (SRSI + MACD Strategy with Dynamic Stop-Loss and Take-Profit).

FMZ source id: 482816

Source
    https://www.fmz.com/strategy/482816 (PineScript v6, FMZ last modified 2025-02-27 17:44:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-158), RSI 16, stochastic 16 smoothed 3 / 3, MACD 12 / 26 / 9, ATR 14,
risk factor 2.5
    k = sma(stoch(rsi, rsi, rsi, 16), 3), d = sma(k, 3); MACD rescaled to K's 16-bar range
    buy = (mean(k - d, k - macdNorm) > 0 or k - d > 0) and (k rising or macd rising) and k < 20
    sell = (mean <= 0 or k - d <= 0) and (k falling or macd falling) and k > 80
    buy and flat -> entry long; while long, every bar: exit(stop = avg price - 2.5 ATR, limit = avg price + 2.5 ATR)
    sell -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is measured from strategy.position_avg_price (the fill) but re-issued every bar with the CURRENT
      ATR (a moving level): fixed at entry as 2.5 ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill; mark trailing_stop_pending. Applied from the fill (decision owed as #489289).
    * Flat-only entries with stops: simulate() mirrors the house bracket from the fill bar (as #430254); an entry is
      allowed on the bar a stop is hit. The close acts on the position held at the bar's start.
    * Long only. Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, a stochastic RSI, MACD and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482816_stoch_rsi_macd_turn_atr_bracket_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk": [2.5, 1.5],
    "rsi_len": [16, 14],
}
DEFAULT_PARAMS = {"rsi_len": 16, "stoch_len": 16, "smooth_k": 3, "smooth_d": 3, "atr_len": 14, "risk": 2.5}


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


def _fracs(bars_df, p):
    return (p["risk"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy()


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    n = int(p["rsi_len"])
    rsi = _rsi(c, n)
    sn = int(p["stoch_len"])
    rl, rh = rsi.rolling(sn).min(), rsi.rolling(sn).max()
    k = (100 * (rsi - rl) / (rh - rl)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    ml, mh = macd.rolling(n).min(), macd.rolling(n).max()
    kl, kh = k.rolling(n).min(), k.rolling(n).max()
    norm = (macd - ml) / (mh - ml) * (kh - kl) + kl
    dkd = k - d
    total = (dkd + (k - norm)) / 2
    buy = (((total > 0) | (dkd > 0)) & ((k > k.shift(1)) | (macd > macd.shift(1))) & (k < 20)).to_numpy()
    sell = (((total <= 0) | (dkd <= 0)) & ((k < k.shift(1)) | (macd < macd.shift(1))) & (k > 80)).to_numpy()
    sl = _fracs(bars_df, p)
    m = len(o)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos == 1 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if lo[i] <= e * (1 - s_) or h[i] >= e * (1 + s_):
                pos = 0
        start = pos
        if start == 0 and buy[i] and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
        if start == 1 and entry_i <= i and sell[i]:
            lx[i], pos = True, 0
    return le, lx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = pd.Series(_fracs(bars_df, p), index=bars_df.index).shift(1)
    return {"sl_stop": sl, "tp_stop": sl}


def portfolio_kwargs(**params):
    return {}
