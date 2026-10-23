"""Broker days, one trade at a time from flat: both Elder Force Indexes (EMA 13 and EMA 50 of price change x volume) more than 2 standard deviations (50 bars) above their 50-bar mean go long, both more than 2 below go short; a ratcheting stop (1.5 ATR 14 from the close) and a ratcheting target (0.5 ATR above the close), re-sent from the bar after the fill, are followed in the signals.
Port of FMZ strategy #473264 "基于标准差和移动平均线的Elders力量指数量化交易策略-Elders-Force-Index-Quantitative-Trading-Strategy-Based-on-Standard-Deviation-and-Moving-Averages" (Elder's Force Index Strategy with ATR-Based SL and TP).

FMZ source id: 473264

Source
    https://www.fmz.com/strategy/473264 (PineScript v5, FMZ last modified 2024-11-28 17:08:24).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-177), EFI 13 / 50; z-score over 50 bars, +-2; ATR 14; stop 1.5 ATR, "trailing" target 0.5 ATR
    long_condition = efi_fast_result > 2 and efi_long_result > 2;  if long_condition and not is_position_open: entry Long, stop_loss := close - 1.5 atr, take_profit := close + 0.5 atr
    while open: stop_loss := max(stop_loss, close - 1.5 atr), take_profit := max(take_profit, close + 0.5 atr) (short: min, mirrored);  exit(stop = stop_loss, limit = take_profit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only from flat (is_position_open is read at the bar's close, before its new orders). The
      exits are first sent at the fill bar's close and re-sent every bar with both levels ratcheted from
      that bar's close and ATR; the target sits 0.5 ATR above the latest close, so it is touched often
      (weird case). The house engine cannot move a target or arm a stop late, so the signals follow
      them: a bar whose low reaches the stop or whose high reaches the target (mirrored for shorts) closes
      the trade at the next open (mark trailing_stop_pending). Pine's stdev is the population deviation.
      Opposite entries cannot occur in the source (one trade at a time from flat); in the signals a
      touch on a bar that also signals the other way closes and reverses at the next open. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ratcheting stop and target followed in the signals.
    2 generic: PASS, Elder Force Index z-score breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in the force index; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur in the source (entries only from flat); a touch-and-signal bar reverses at the next open in the signals.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473264_efi_zscore_ratchet_atr_stop_target_followed"
FAMILY = "force_index"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "numdev": [2.0, 1.5],
    "tp_mult": [0.5, 1.0],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 50, "sd_len": 50, "numdev": 2.0, "sl_mult": 1.5, "tp_mult": 0.5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    force = c.diff() * v
    n = int(p["sd_len"])
    z = []
    for span in (int(p["fast"]), int(p["slow"])):
        e = force.ewm(span=span, adjust=False).mean()
        z.append((e - e.rolling(n).mean()) / e.rolling(n).std(ddof=0))
    k = float(p["numdev"])
    buy = ((z[0] > k) & (z[1] > k)).to_numpy()
    sell = ((z[0] < -k) & (z[1] < -k)).to_numpy()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14).to_numpy(dtype=float)
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sk, tk = float(p["sl_mult"]), float(p["tp_mult"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, held_prev = 0, 0, 0
    st = tp = np.nan
    for i in range(m):
        held = pine
        if held != 0 and held_prev == held:       # exits sent at the previous close
            if (held == 1 and (ln[i] <= st or hn[i] >= tp)) or (held == -1 and (hn[i] >= st or ln[i] <= tp)):
                held = 0
        new = held
        if held == 0:
            if buy[i]:
                new, st, tp = 1, cn[i] - atr[i] * sk, cn[i] + atr[i] * tk
            if sell[i]:
                new, st, tp = -1, cn[i] + atr[i] * sk, cn[i] - atr[i] * tk
        elif held == 1:
            st, tp = max(st, cn[i] - atr[i] * sk), max(tp, cn[i] + atr[i] * tk)
        else:
            st, tp = min(st, cn[i] + atr[i] * sk), min(tp, cn[i] - atr[i] * tk)
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
        held_prev, pine = held, new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
