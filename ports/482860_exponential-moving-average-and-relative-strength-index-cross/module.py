"""Close crossing a hair above (below) EMA 68 with a point stop from the entry as an ATR multiple and RSI 13 profit
exits, daily (broker-day) bars: the close crossing above EMA 68 + 2 points goes long, closed at RSI 70 or a close 20
points under the entry; the mirror goes short, closed at RSI 28 or 20 points over the entry.
Port of FMZ strategy #482860 "指数移动平均与相对强弱指数交叉策略-Exponential-Moving-Average-and-Relative-Strength-Index-Crossover-Strategy" (EMA & RSI Custom Strategy).

FMZ source id: 482860

Source
    https://www.fmz.com/strategy/482860 (PineScript v5, FMZ last modified 2025-02-27 17:33:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 94-130), EMA 68, RSI 13, offsets 2, stop 20 points, RSI exits 70 / 28
    buy = crossover(close, ema + 2) -> entry long; while long: close <= avg - 20 or rsi >= 70 -> close
    sell = crossunder(close, ema - 2) -> entry short; while short: close >= avg + 20 or rsi <= 28 -> close
    order: buy, long closes, sell, short closes

Interpretation choices (Pine rules in SURVEY_README.md)
    * Point distances -> ATR(14) multiples (criterion 2), judged on the author's market (Binance ETH_USDT, daily ATR
      about 120 USD): the 2-point offsets are 0.017 ATR, the 20-point stop 0.17 ATR.
    * The stop is checked on closes from the entry price (the fill) and acts through strategy.close: an exit signal at
      the next open (rule 3), not a broker stop. State machine on the position held at each close, in the source's
      order; a close never undoes that bar's entry.
    * Entries reverse (REVERSAL INTENDED). No stop module. Daily bars are broker days (17:00 America/New_York) stamped
      with their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based exits as exit signals.
    2 generic: PASS, an EMA, RSI and point distances as ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_482860_ema68_offset_cross_rsi_exit_point_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_k": [0.17, 1.0],
    "ema_len": [68, 100],
}
DEFAULT_PARAMS = {"ema_len": 68, "rsi_len": 13, "offset_k": 0.017, "stop_k": 0.17, "atr_len": 14,
                  "rsi_long_exit": 70, "rsi_short_exit": 28}


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
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    atr = _atr(bars_df, int(p["atr_len"]))
    bp, sp = ema + p["offset_k"] * atr, ema - p["offset_k"] * atr
    buy = ((c > bp) & (c.shift(1) <= bp.shift(1))).to_numpy()
    sell = ((c < sp) & (c.shift(1) >= sp.shift(1))).to_numpy()
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    stop = (p["stop_k"] * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, entry = 0, np.nan
    for i in range(m):
        pos = held
        if buy[i]:
            pos = 1
        if held == 1 and pos == 1 and (cv[i] <= entry - stop[i] or rsi[i] >= p["rsi_long_exit"]):
            pos = 0
        if sell[i]:
            pos = -1
        if held == -1 and pos == -1 and (cv[i] >= entry + stop[i] or rsi[i] <= p["rsi_short_exit"]):
            pos = 0
        tgt[i] = pos
        if pos != held and pos != 0 and i + 1 < m:
            entry = o[i + 1]                          # strategy.position_avg_price: the next open fill
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
