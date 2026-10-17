"""SMA 200 crossovers confirmed two bars later by RSI and ADX, from flat, with a 2 % target and a 1.5 ATR stop,
closed on the confirmed cross down, long only, daily (broker-day) bars.
Port of FMZ strategy #482901 "均线动态趋势跟踪与RSI-ADX复合指标交易策略-Dynamic-Moving-Average-Trend-Following-Strategy-with-RSI-ADX-Composite-Indicators" (BTC/USD MA200 with RSI, ADX, ATR).

FMZ source id: 482901

Source
    https://www.fmz.com/strategy/482901 (PineScript v5, FMZ last modified 2025-02-27 17:27:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-133), SMA 200, RSI 14, DMI 14 / 14, ATR 14
    buy = crossover(close, sma200)[2] and rsi > 40 and adx > 20 and close > sma200, with no open trade ->
    entry + exit(limit = close x 1.02, stop = close - 1.5 ATR)
    sell = crossunder(close, sma200)[2] and rsi < 60 and adx > 20 and close < sma200 -> close the open trade

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: tp 2 %, sl 1.5 ATR / close, shifted one bar inside
      stops() and re-based on the fill (house rule).
    * Entries only from flat (opentrades == 0): simulate() mirrors the house bracket on bars from the fill bar (as
      #430254 _run); an entry is allowed on the bar a stop or target is hit. The sell close is an exit signal.
    * Long only; the source has no shorts. ADX as Pine's ta.dmi. Stop module: portfolio_kwargs {} (D4). Daily bars are
      broker days (17:00 America/New_York) stamped with their first minute (as #430984); stops on daily bars:
      coarse_bar_stop. FREQ = "1D" from the backtest header ("BTC/USD" in the title is a label).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, moving averages, RSI, ADX, ATR multiples and a percentage target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482901_sma200_cross_confirm_flat_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [2.0, 5.0],
    "sl_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"ma_len": 200, "atr_len": 14, "tp_pct": 2.0, "sl_mult": 1.5}


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


def _fracs(bars_df, p):
    return (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy(), p["tp_pct"] / 100


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    cs = bars_df["close"]
    ma = cs.rolling(int(p["ma_len"])).mean()
    rsi = _rsi(cs, 14)
    _, _, adx = _adx_pine(bars_df, 14, 14)
    xu = ((cs > ma) & (cs.shift(1) <= ma.shift(1))).shift(2, fill_value=False)
    xd = ((cs < ma) & (cs.shift(1) >= ma.shift(1))).shift(2, fill_value=False)
    buy = (xu & (rsi > 40) & (adx > 20) & (cs > ma)).to_numpy()
    sell = (xd & (rsi < 60) & (adx > 20) & (cs < ma)).to_numpy()
    sl, tp = _fracs(bars_df, p)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos == 1 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if lo[i] <= e * (1 - s_) or h[i] >= e * (1 + tp):
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
    sl, tp = _fracs(bars_df, p)
    return {"sl_stop": pd.Series(sl, index=bars_df.index).shift(1), "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
