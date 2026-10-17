"""RSI 14 below 30 bought, closed once the close is 3 ATR above the average of the (up to four) oversold signal
closes, long only, daily (broker-day) bars.
Port of FMZ strategy #482909 "基于相对强弱指数和平均真实波幅的多层次动态成本均摊波段交易策略-Multi-Level-Dynamic-Cost-Averaging-Swing-Trading-Strategy-Based-on-RSI-and-ATR" (DCA-Based Swing Strategy (Risk $200) with Signals).

FMZ source id: 482909

Source
    https://www.fmz.com/strategy/482909 (PineScript v6, FMZ last modified 2025-02-27 17:22:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 117-165), RSI 14 < 30, ATR 14, at most 4 buys, take profit 3 ATR
    buy = rsi < 30 and entryCount < 4: entry "DCA Buy" (qty = 200 / 2 ATR); avg = running mean of the buy-signal
    closes; entryCount += 1
    close >= avg + 3 ATR and entryCount > 0: close, reset avg and count

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() keeps the default pyramiding of 1, so the later "DCA" buys add nothing: one position, as written
      (and adds would be sizing anyway, #490570). The script's own average of the signal closes still sets the exit.
    * The take-profit is checked on closes and acts through strategy.close: an exit signal at the next open (rule 3).
      The $200 risk qty is sizing: not ported. Long only; the source has no shorts. No stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-based target is an exit signal.
    2 generic: PASS, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482909_rsi_oversold_avg_signal_atr_target_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_atr": [3.0, 2.0],
    "rsi_os": [30, 35],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_os": 30, "atr_len": 14, "tp_atr": 3.0, "max_entries": 4}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    avg, count = np.nan, 0
    for i in range(m):
        if rsi[i] < p["rsi_os"] and count < int(p["max_entries"]):
            le[i] = True
            avg = cv[i] if np.isnan(avg) else (avg * count + cv[i]) / (count + 1)
            count += 1
        if count > 0 and cv[i] >= avg + p["tp_atr"] * atr[i]:
            lx[i] = not le[i]                         # never an exit on the signal's own bar
            avg, count = np.nan, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
