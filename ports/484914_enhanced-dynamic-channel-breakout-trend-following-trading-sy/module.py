"""Turtle-style Donchian breakouts in the SMA 200 trend with an RSI cap, a 5-bar channel exit and a 2 ATR stop, broker
days: a high above the previous 15-bar high, above the SMA 200 with RSI 14 below 70, goes long when not already long;
a low under the previous 5-bar low closes it; the stop sits 2 ATR under the entry; shorts mirror it.
Port of FMZ strategy #484914 "增强型动态通道突破趋势跟踪交易系统-Enhanced-Dynamic-Channel-Breakout-Trend-Following-Trading-System" (Enhanced Turtle Trading for BTC 1H).

FMZ source id: 484914

Source
    https://www.fmz.com/strategy/484914 (PineScript v5, FMZ last modified 2025-03-05 09:49:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 183-269), Donchian 15 / 5, ATR 10, SMA 200, RSI 14 (30 / 70), stop 2 ATR
    longEntry = high > highest(high, 15)[1] and close > sma200 and rsi < 70 (short mirrored)
    longEntry and position <= 0 -> close_all, entry long (qty = risk units);  add units every 1 ATR (up to 4)
    position > 0 and low < lowest(low, 5)[1] -> close_all (short mirrored)
    position > 0: longTrailingStop = max(longTrailingStop[1], avg price - 2 ATR); exit(stop = longTrailingStop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel exits are bar-range-checked: exit signals at the next open (rule 3; #489638), from the position
      held at the bar's start (#430850); close_all + entry is the reversal (REVERSAL INTENDED).
    * The add-unit entries cannot fill (default pyramiding 1); they and the risk quantity are sizing.
    * The stop (rule 2, mark trailing_stop_pending): the level ratchets on the current ATR and the variable is never
      reset, so a later trade starts from the previous trade's level, as written. Fixed at entry here: sl_stop =
      stop_mult x ATR / close of the signal bar, shifted one bar inside stops() and re-based on the fill. simulate()
      mirrors that stop from the fill bar (#430254) so entries follow the position the engine holds.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header ("BTC 1H" in the title is a label): coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders and bar-range-checked exits; stop fixed at entry (marked).
    2 generic: PASS, channels, a moving average, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-unit quantity and add-ons quoted; the stop ported via stops() and quoted in
      original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484914_donchian_turtle_sma_rsi_stop"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "entry_period": [15, 20],
    "stop_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"entry_period": 15, "exit_period": 5, "atr_period": 10, "sma_period": 200, "rsi_period": 14,
                  "rsi_ob": 70, "rsi_os": 30, "stop_mult": 2.0}


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


def _sl_frac(bars_df, p):
    return p["stop_mult"] * _atr(bars_df, int(p["atr_period"])) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ne, nx = int(p["entry_period"]), int(p["exit_period"])
    sma = c.rolling(int(p["sma_period"])).mean()
    rsi = _rsi(c, int(p["rsi_period"]))
    go_l = ((h > h.rolling(ne).max().shift(1)) & (c > sma) & (rsi < p["rsi_ob"])).to_numpy()
    go_s = ((lo < lo.rolling(ne).min().shift(1)) & (c < sma) & (rsi > p["rsi_os"])).to_numpy()
    out_l = (lo < lo.rolling(nx).min().shift(1)).to_numpy()
    out_s = (h > h.rolling(nx).max().shift(1)).to_numpy()
    sl_f = _sl_frac(bars_df, p).to_numpy(dtype=float)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, fill_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= fill_i:                     # mirror of the house stop from the fill price
            e = ov[fill_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        start = pos
        if go_l[i] and pos <= 0:
            pos, fill_i, s_ = 1, i + 1, sl_f[i]
        if go_s[i] and pos >= 0:
            pos, fill_i, s_ = -1, i + 1, sl_f[i]
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _sl_frac(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
