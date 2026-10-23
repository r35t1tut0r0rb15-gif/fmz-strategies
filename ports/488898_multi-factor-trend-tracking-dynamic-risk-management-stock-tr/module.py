"""Broker days: EMA 20 > 50, SMA 14 > 28 and SMA 10 > 20 with a rising smoothed ATR, volume over 1.3 x its 20-day average and the close above the SMA 50 goes long with a 2 ATR stop and 4 ATR target from the signal close; the mirror goes short; RSI 14 over 75 closes a long, under 25 a short, and volume under half its average closes either; reversing.
Port of FMZ strategy #488898 "Multi Factor Trend Tracking Dynamic Risk Management Stock Trading Strategy" (G-Channel Strategy for Stocks).

FMZ source id: 488898

Source
    https://www.fmz.com/strategy/488898 (PineScript v5, FMZ last modified 2025-03-31 16:47:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 117-169), EMA 20 / 50, SMA 14 / 28, SMA 10 / 20; "ADX" = EMA 14 of RMA 14 of ATR 14 vs its SMA 14; volume SMA 20 x 1.3 / 0.5; ATR 14 x 2 / 4; RSI 14 (75 / 25); 10 % of equity
    longCondition = ema20 > ema50 and sma14 > sma28 and sma10 > sma20 and adx > sma(adx, 14) and volume > 1.3 x sma(volume, 20) and close > sma50 -> entry Long, exit("Take Profit", "Long", limit = close + 4 atr, stop = close - 2 atr)
    shortCondition = all three MA tests false and adx rising and the volume test and close < sma50 -> entry Short, exit(same id, "Short", ...)
    rsi > 75 -> close Long;  rsi < 25 -> close Short;  volume < 0.5 x sma(volume, 20) -> close Long and Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ADX" is a smoothed ATR, so the filter is rising volatility. The bracket is sent on signal bars
      as levels from that close: ported as fractions of the fill, exact (1e-6 floor); repeats while in
      the trade re-send it (not followed: trailing_stop_pending). Both sides share one exit id, but their
      signal bars never coincide. The closes act only on a position the bar's entries leave unchanged;
      the loop also follows the bracket on the bars only to know when the trade is flat (a stop or target
      lets the next state bar re-enter). The title names stocks; the header is ETH_USDT. REVERSAL
      INTENDED. 10 % of equity is sizing. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, MA-stack trend states on rising volatility and volume, RSI / low-volume exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.3 x and 0.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488898_g_channel_ma_stack_atr_volume_rsi_exit_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 3.0],
    "tp_atr": [4.0, 6.0],
}
DEFAULT_PARAMS = {"sl_atr": 2.0, "tp_atr": 4.0}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    g = c.ewm(span=20, adjust=False).mean() > c.ewm(span=50, adjust=False).mean()
    fv = c.rolling(14).mean() > c.rolling(28).mean()
    co = c.rolling(10).mean() > c.rolling(20).mean()
    atr = _atr(bars_df, 14)
    adx = _rma(atr, 14).ewm(span=14, adjust=False).mean()
    rising = adx > adx.rolling(14).mean()
    vma = v.rolling(20).mean()
    vol_ok = v > vma * 1.3
    s50 = c.rolling(50).mean()
    buy = (g & fv & co & rising & vol_ok & (c > s50)).to_numpy()
    sell = (~g & ~fv & ~co & rising & vol_ok & (c < s50)).to_numpy()
    r = _rsi(c, 14)
    low_v = (v < vma * 0.5).to_numpy()
    ex_l, ex_s = (r > 75).to_numpy() | low_v, (r < 25).to_numpy() | low_v
    an, cn, hn, ln = atr.to_numpy(), c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    slk, tpk = float(p["sl_atr"]), float(p["tp_atr"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, st, tg = 0, np.nan, np.nan
    for i in range(m):
        if pos == 1 and (ln[i] <= st or hn[i] >= tg):
            pos = 0                         # the bracket closed the trade (the engine does it at the level)
        elif pos == -1 and (hn[i] >= st or ln[i] <= tg):
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
                le[i], st, tg = True, cn[i] - slk * an[i], cn[i] + tpk * an[i]
            elif new == -1:
                se[i], st, tg = True, cn[i] + slk * an[i], cn[i] - tpk * an[i]
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
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
