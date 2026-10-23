"""Broker days: in the script's one-step supertrend up-state (bands hl2 -/+ 3 ATR 10), a bar on volume over 1.2 x its 20-day average with a body over 0.3 ATR and RSI 14 under 70 goes long with a 1 ATR stop and 2 ATR target from the signal close; the down-state mirror (RSI over 30) goes short; reversing.
Port of FMZ strategy #491511 "多指标融合自动化交易系统SuperTrend-ATR-RSI动态风控策略-Multi-Indicator-Fusion-Automated-Trading-System-SuperTrend-ATR-RSI-Dynamic-Risk-Control-Strategy" (Supertrend Hombrok Bot).

FMZ source id: 491511

Source
    https://www.fmz.com/strategy/491511 (PineScript v5, FMZ last modified 2025-04-21 16:15:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 165-243), ATR 10 x 3 bands; one-step band ratchet; RSI 14 (70 / 30); volume SMA 20 x 1.2; body > 0.3 ATR; SL 1 ATR, TP 2 ATR; cash 1000, qty = 10 / close
    trendUp = close[1] > upperBand[1] ? max(upperBand, upperBand[1]) : upperBand  (upperBand = hl2 - 3 atr);  trendDown mirrored on hl2 + 3 atr
    trend: -1 -> 1 on close > trendDown, 1 -> -1 on close < trendUp
    buyCond = trend == 1 and volume > 1.2 x sma(volume, 20) and body > 0.3 atr and rsi < 70 -> entry Compra, exit(stop = close - atr, limit = close + 2 atr);  sellCond mirrored (rsi > 30)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands ratchet only one step (against the previous bar's raw band, not the previous ratcheted
      level), as written, so the state flips more easily than a supertrend. Entries fire on every
      qualifying bar of a state; repeats while in the trade re-send the bracket (not followed:
      trailing_stop_pending); the bracket is sent on signal bars from that close: ported as fractions of
      the fill, exact (1e-6 floor). The loop follows the bracket on the bars only to know when the trade
      is flat. REVERSAL INTENDED. The cash order size is sizing. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, band-state trend entries on volume and body strength.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash 1000 per order and qty = 10 / close stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.2 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491511_one_step_supertrend_volume_body_rsi_atr_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [3.0, 2.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_period": 10, "atr_mult": 3.0, "rr": 2.0}


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
    atr = _atr(bars_df, int(p["atr_period"]))
    an = atr.to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    k = float(p["atr_mult"])
    ub, lb = hl2 - k * an, hl2 + k * an
    pu = np.concatenate([[np.nan], ub[:-1]])
    pl = np.concatenate([[np.nan], lb[:-1]])
    pu = np.where(np.isnan(pu), ub, pu)       # nz(upperBand[1], upperBand)
    pl = np.where(np.isnan(pl), lb, pl)
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    pc = np.concatenate([[np.nan], cn[:-1]])
    t_up = np.where(pc > pu, np.maximum(ub, pu), ub)
    t_dn = np.where(pc < pl, np.minimum(lb, pl), lb)
    m = len(cn)
    state = np.ones(m, dtype=int)
    tr = 1
    for i in range(m):
        if tr == -1 and cn[i] > t_dn[i]:
            tr = 1
        elif tr == 1 and cn[i] < t_up[i]:
            tr = -1
        state[i] = tr
    r = _rsi(c, 14)
    filt = ((v > v.rolling(20).mean() * 1.2) & ((c - o).abs() > atr * 0.3)).to_numpy()
    buy = (state == 1) & filt & (r < 70).to_numpy()
    sell = (state == -1) & filt & (r > 30).to_numpy()
    rr = float(p["rr"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, st, tg = 0, np.nan, np.nan
    for i in range(m):
        if pos == 1 and (ln[i] <= st or hn[i] >= tg):
            pos = 0                         # the bracket closed the trade (the engine does it at the level)
        elif pos == -1 and (hn[i] >= st or ln[i] <= tg):
            pos = 0
        if buy[i] and pos != 1 and i + 1 < m:
            le[i], pos, st, tg = True, 1, cn[i] - an[i], cn[i] + rr * an[i]
        elif sell[i] and pos != -1 and i + 1 < m:
            se[i], pos, st, tg = True, -1, cn[i] + an[i], cn[i] - rr * an[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_period"]))
    sl_d, tp_d = atr, float(p["rr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
