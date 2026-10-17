"""EMA 50 / 200 crosses with ADX above 25 and RSI on the open side, with a 3 % stop and target from the signal close,
closed when RSI reaches 70 (long) or 30 (short), daily bars.
Port of FMZ strategy #482684 "多重时间框架动态趋势跟踪策略结合EMA与ADX指标-Multi-Timeframe-Dynamic-Trend-Following-Strategy-with-EMA-and-ADX-Integration" (DOGE Enhanced Trend Following Strategy).

FMZ source id: 482684

Source
    https://www.fmz.com/strategy/482684 (PineScript v5, FMZ last modified 2025-02-27 17:52:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 97-144), EMA 50 / 200, DMI 14 / ADX 14 > 25, RSI 14 (70 / 30), TP x 1.03,
SL x 0.97
    crossover(ema50, ema200) and adx > 25 and rsi > 30 -> entry long with exit(limit = close x 1.03,
    stop = close x 0.97); crossunder and adx > 25 and rsi < 70 -> entry short (x 0.97 / x 1.03)
    close long when rsi > 70; close short when rsi < 30

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 240-minute EMAs requested by the script feed no order (a lower timeframe on the daily chart, unused).
    * The bracket is placed with the entry: 3 % / 3 % of the signal close, re-based on the fill (house rule).
    * The RSI closes (strategy.close with when) run after the entries: they act on the position held at the bar's
      start and never undo an entry on that bar (#430850). simulate() mirrors the house bracket from the fill
      (as #430254) so a close after a stop exit is not emitted; exits are emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, EMAs, ADX, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity; commission and slippage are costs; the bracket via stops(), quoted in
      original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482684_ema50_200_cross_adx_rsi_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [3.0, 6.0],
    "sl_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "di_len": 14, "adx_len": 14, "adx_min": 25.0, "rsi_len": 14,
                  "ob": 70.0, "os": 30.0, "tp_pct": 3.0, "sl_pct": 3.0}


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


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    _, _, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    strong = adx > p["adx_min"]
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & strong & (rsi > p["os"])).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & strong & (rsi < p["ob"])).to_numpy()
    xl, xs = (rsi > p["ob"]).to_numpy(), (rsi < p["os"]).to_numpy()
    sl, tp = p["sl_pct"] / 100, p["tp_pct"] / 100
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - sl) or h[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + sl) or lo[i] <= e * (1 - tp)):
                pos = 0
        start = pos
        if buy[i] and pos != 1 and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        if sell[i] and pos != -1 and i + 1 < m:
            se[i], pos, entry_i = True, -1, i + 1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
