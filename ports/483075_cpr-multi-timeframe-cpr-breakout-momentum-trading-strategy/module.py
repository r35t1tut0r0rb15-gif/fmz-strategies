"""Bar size searched (no header): a close above the previous broker day's CPR top above the EMA 20, with a higher low at the latest RSI 14 cross-up of 30 than at the one before and above-average volume, goes long with a stop half the CPR width under its bottom and a target 1.5 widths over its top; the mirror goes short; reversing.
Port of FMZ strategy #483075 "多重时间周期CPR突破动量交易策略-Multi-Timeframe-CPR-Breakout-Momentum-Trading-Strategy" (Ahmad Ali Khan CPR Strategy).

FMZ source id: 483075

Source
    https://www.fmz.com/strategy/483075 (PineScript v5, FMZ last modified 2025-02-21 11:45:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 84-159), daily CPR from request.security("D", high[1] / low[1] / close[1], lookahead_on); EMA 20; RSI 14 divergence by valuewhen; volume SMA 20
    pivot = (H + L + C) / 3 of the previous day;  bc = (H + L) / 2;  tc = 2 pivot - bc;  long_condition = close > tc and close > ema20 and valuewhen(crossover(rsi, 30), low, 0) > valuewhen(..., 1) and volume > sma(volume, 20) -> entry Long, exit("XL", stop = bc - 0.5 (tc - bc), limit = tc + 1.5 (tc - bc))
    short mirrored (close < bc, bearish_div from crossunder(rsi, 70) highs) -> entry Short, exit("XS", stop = tc + 0.5 width, limit = bc - 1.5 width)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily values use [1] with lookahead_on, so they are the previous broker day's high, low and
      close (no look-ahead). The weekly open only plots. The divergence flags are states between RSI
      crossings. The width tc - bc can be negative (close under the day's midpoint), which moves the
      levels to the other side, as written. The levels are sent on signal bars: ported as fractions of
      the fill, exact (1e-6 floor); the entry is a state, and repeats re-send them (not followed:
      trailing_stop_pending). No backtest header: FREQ = "bar_size_pending", the bars from the house
      bar_sizes.build_bars; when the searched size is above 1 h, the mark coarse_bar_stop also applies.
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-day CPR bracket as fractions of the fill.
    2 generic: PASS, CPR breakouts with EMA trend, RSI divergence and volume.
    3 crypto-exchange-only: no (no exchange header; no symbol named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily CPR; no venue-open rule.
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483075_daily_cpr_breakout_ema_rsi_divergence_volume_reversal"
FAMILY = "pivot_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_w": [0.5, 1.0],
    "tp_w": [1.5, 2.5],
}
DEFAULT_PARAMS = {"ema_len": 20, "sl_w": 0.5, "tp_w": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _cpr(bars_df):
    """Previous broker day's H / L / C mapped to every bar of the day (the security [1] reading)."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    dh = pd.Series(h.to_numpy(), index=day).groupby(level=0).max()
    dl = pd.Series(lo.to_numpy(), index=day).groupby(level=0).min()
    dc = pd.Series(c.to_numpy(), index=day).groupby(level=0).last()
    ph, pl, pc = (s.shift(1).reindex(day).to_numpy() for s in (dh, dl, dc))
    pivot = (ph + pl + pc) / 3
    bc = (ph + pl) / 2
    tc = pivot + (pivot - bc)
    return pd.Series(bc, index=bars_df.index), pd.Series(tc, index=bars_df.index)


def _last_two(cond, src):
    """ta.valuewhen(cond, src, 0) and (cond, src, 1)."""
    cv, sv = cond.to_numpy(), src.to_numpy(dtype=float)
    a, b = np.full(len(sv), np.nan), np.full(len(sv), np.nan)
    last = prev = np.nan
    for i in range(len(sv)):
        if cv[i]:
            prev, last = last, sv[i]
        a[i], b[i] = last, prev
    return a, b


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    bc, tc = _cpr(bars_df)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    l0, l1 = _last_two((r > 30) & (r.shift(1) <= 30), lo)
    h0, h1 = _last_two((r < 70) & (r.shift(1) >= 70), h)
    vol_ok = v > v.rolling(20).mean()
    buy = (c > tc) & (c > ema) & pd.Series(l0 > l1, index=c.index) & vol_ok
    sell = (c < bc) & ~(c > ema) & pd.Series(h0 < h1, index=c.index) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    bc, tc = _cpr(bars_df)
    w = tc - bc
    slw, tpw = float(p["sl_w"]), float(p["tp_w"])
    sl_l, tp_l = bc - slw * w, tc + tpw * w
    sl_s, tp_s = tc + slw * w, bc - tpw * w
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - sl_l.shift(1) / o)
            .mask(sf, sl_s.shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, tp_l.shift(1) / o - 1)
            .mask(sf, 1 - tp_s.shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
