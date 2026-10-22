"""Close on one side of the EMA 50 with ADX (20 / 20) over 20, broker days: above goes long, below goes short; after 4 consecutive closes in profit a close-based ratchet starts, and a later close back under it (still in profit) closes; reversing.
Port of FMZ strategy #477530 "动态指数均线交叉策略结合ADX趋势强度过滤系统-Dynamic-EMA-Crossover-Strategy-with-ADX-Trend-Strength-Filtering-System" (Simple EMA 50 Strategy with ADX Filter).

FMZ source id: 477530

Source
    https://www.fmz.com/strategy/477530 (PineScript v6, FMZ last modified 2025-01-06 11:44:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-213), EMA 50; DMI 20, ADX smoothing 20, threshold 20; 4 profitable closes arm the ratchet
    long and close > avg -> count += 1, count >= 4 -> sl := max(sl, close);  otherwise count := 0, sl := na;  (mirror for shorts)
    long and sl and close < sl -> close Buy;  short and sl and close > sl -> close Sell;  adx > 20 and close > ema50 -> entry Buy;  adx > 20 and close < ema50 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the counters on the entry price (the fill open) as written: a close at or under the
      entry price resets the count and clears the ratchet, so the ratchet close fires only while the
      close is still above the entry price. The ratchet is a bar-close test filled at the next open, not
      a broker stop. The entries are states and repeat; a repeat on the held side is ignored, a close on
      the bar of a same-side repeat simply ends the trade (as #472251), and a close leaves a same-bar
      reversal standing. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA side with an ADX filter and a close ratchet.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477530_ema50_side_adx20_close_ratchet_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [50, 100],
    "adx_threshold": [20.0, 25.0],
}
DEFAULT_PARAMS = {"ema_length": 50, "adx_threshold": 20.0, "adx_length": 20, "count": 4}


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
    o, c = bars_df["open"], bars_df["close"]
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    strong = _dmi(bars_df, int(p["adx_length"]))[2] > float(p["adx_threshold"])
    lc = (strong & (c > e)).to_numpy()
    sc = (strong & (c < e)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    need = int(p["count"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg = 0, 0, np.nan
    lcnt = scnt = 0
    lsl = ssl = np.nan
    for i in range(m):
        if nxt != pos:
            avg = ov[i] if nxt != 0 else np.nan
        pos = nxt
        if pos == 1 and cv[i] > avg:
            lcnt += 1
            if lcnt >= need:
                lsl = cv[i] if np.isnan(lsl) else max(lsl, cv[i])
        else:
            lcnt, lsl = 0, np.nan
        if pos == -1 and cv[i] < avg:
            scnt += 1
            if scnt >= need:
                ssl = cv[i] if np.isnan(ssl) else min(ssl, cv[i])
        else:
            scnt, ssl = 0, np.nan
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        elif sc[i] and pos != -1:
            se[i], nxt = True, -1
        if pos == 1 and not se[i] and cv[i] < lsl:
            lx[i], nxt = True, 0
        if pos == -1 and not le[i] and cv[i] > ssl:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
