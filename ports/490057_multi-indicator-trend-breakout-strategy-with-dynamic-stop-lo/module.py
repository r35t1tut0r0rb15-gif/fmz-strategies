"""Broker days: a close above the previous 20-day high, above the EMA 50, with RSI 14 over 50 and ATR 14 above its 20-day average goes long with a stop 1.5 ATR under the signal close; the mirror below the 20-day low goes short; a close beyond the previous 10-day low (high for a short) closes the trade; reversing.
Port of FMZ strategy #490057 "Multi Indicator Trend Breakout Strategy with Dynamic Stop Loss" (Donchian Breakout Strategy).

FMZ source id: 490057

Source
    https://www.fmz.com/strategy/490057 (PineScript v5, FMZ last modified 2025-04-11 11:01:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 172-250), Donchian 20 entry / 10 exit; ATR 14 x 1.5 stop; EMA 50; RSI 14 (50); ATR > SMA 20 of ATR on; volume filter off; start 2025-01-01; 10 % of equity; commission 0.045 %
    longCondition = close > highest(high, 20)[1] and close > ema50 and rsi > 50 and atr > sma(atr, 20) -> entry Long, exit(stop = close - 1.5 atr)
    shortCondition mirrored -> entry Short, exit(stop = close + 1.5 atr)
    close < lowest(low, 10)[1] -> close Long;  close > highest(high, 10)[1] -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent on signal bars from that close: ported as a fraction of the fill, exact (1e-6
      floor); repeated breakouts while in the trade re-send it closer (not followed:
      trailing_stop_pending). The closes act only on a position the bar's entries leave unchanged; the
      loop also follows the stop on the bars only to know when the trade is flat. The volume filter is
      off by default, so volume is not used. The 2025-01-01 start (cancel_all before it) is dropped like
      other start dates. REVERSAL INTENDED. 10 % of equity and the commission are sizing and costs. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal close as a fraction of the fill.
    2 generic: PASS, Donchian breakouts in the EMA trend with a volatility filter and channel exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and commission 0.045 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the 2025 start date dropped.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_490057_donchian20_10_ema50_rsi_atr_filter_atr_stop_reversal"
FAMILY = "breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "entry_len": [20, 55],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"entry_len": 20, "exit_len": 10, "atr_mult": 1.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, xn = int(p["entry_len"]), int(p["exit_len"])
    atr = _atr(bars_df, 14)
    ema = c.ewm(span=50, adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = atr > atr.rolling(20).mean()
    buy = ((c > h.rolling(n).max().shift(1)) & (c > ema) & (r > 50) & vol_ok).to_numpy()
    sell = ((c < lo.rolling(n).min().shift(1)) & (c < ema) & (r < 50) & vol_ok).to_numpy()
    ex_l = (c < lo.rolling(xn).min().shift(1)).to_numpy()
    ex_s = (c > h.rolling(xn).max().shift(1)).to_numpy()
    an, cn, hn, ln = atr.to_numpy(), c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = float(p["atr_mult"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, st = 0, np.nan
    for i in range(m):
        if pos == 1 and ln[i] <= st:
            pos = 0                         # the stop closed the trade (the engine does it at the level)
        elif pos == -1 and hn[i] >= st:
            pos = 0
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos and i + 1 < m:
            if new == 1:
                le[i], st = True, cn[i] - k * an[i]
            elif new == -1:
                se[i], st = True, cn[i] + k * an[i]
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = _run(bars_df, p)
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    d = float(p["atr_mult"]) * _atr(bars_df, 14)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - d).shift(1) / o)
            .mask(sf, (c + d).shift(1) / o - 1))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
