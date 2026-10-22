"""Close crossings of the EMA 200 with the close on the same side of the EMA 20, broker days: the cross up goes long, the cross down goes short; a close 20 ticks beyond the entry price closes; reversing.
Port of FMZ strategy #477521 "多重均线交叉结合Camarilla支撑阻力趋势交易系统-Multi-EMA-Crossover-with-Camarilla-Support-Resistance-Trend-Trading-System" (Pradeep Crude oil Entry and Exit).

FMZ source id: 477521

Source
    https://www.fmz.com/strategy/477521 (PineScript v5, FMZ last modified 2025-01-06 11:13:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-200), EMA 20 / 50 / 100 / 200 (50 and 100 plotted); exit mode Price Movement, 20 ticks (1 % in the other mode); 100 % of 50000 capital as qty; Camarilla / CPR levels plotted only
    close > ema200 and close > ema20 and close[1] <= ema200 -> entry Long (qty = 50000 / close);  close < ema200 and close < ema20 and close[1] >= ema200 -> entry Short
    close - avg >= 20 x mintick -> close Long;  avg - close >= 20 x mintick -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit tests are bar-close tests on the entry price, so a loop tracks it (the fill open) and
      closes at the next open. The 20 ticks are 2.0 at the 0.1 tick, ported as an ATR multiple at the
      daily reading (~1000): 0.002 x ATR 14 of the bar (as #468324). A close acts only on a position held
      into the bar and leaves a same-bar reversal standing. The Camarilla and CPR levels are plotted
      only. REVERSAL INTENDED. The qty from capital x 100 % / close is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick exit as an ATR multiple.
    2 generic: PASS, EMA 200 close crossings with a small profit exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital 50000 x 100 % / close qty stored, not ported.
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

NAME = "fmz_477521_close_cross_ema200_ema20_side_tick_profit_close_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "exit_atr": [0.002, 1.0],
    "ema_long": [200, 100],
}
DEFAULT_PARAMS = {"exit_atr": 0.002, "ema_long": 200, "ema_short": 20, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    lc = ((c > el) & (c > es) & (c.shift(1) <= el.shift(1))).to_numpy()
    sc = ((c < el) & (c < es) & (c.shift(1) >= el.shift(1))).to_numpy()
    thr = (float(p["exit_atr"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg = 0, 0, np.nan
    for i in range(m):
        if nxt != pos:
            avg = ov[i] if nxt != 0 else np.nan
        pos = nxt
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        if sc[i] and pos != -1:
            se[i], nxt = True, -1
        if pos == 1 and not se[i] and cv[i] - avg >= thr[i]:
            lx[i], nxt = True, 0
        if pos == -1 and not le[i] and avg - cv[i] >= thr[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
