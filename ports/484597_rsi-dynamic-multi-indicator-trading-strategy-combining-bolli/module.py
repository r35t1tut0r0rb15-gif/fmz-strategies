"""Broker days: the close crossing back over the lower Bollinger band (20, 2) with RSI 14 under 30 goes long ("Long"), a close crossing over the upper band on above-average volume also goes long ("Breakout Long"); the mirrors go short; only the "Long" / "Short" trades carry a 2 % stop and 4 % target re-sent from each bar's close, followed in the signals; reversing.
Port of FMZ strategy #484597 "融合布林带与RSI的动态多指标交易策略-Dynamic-Multi-Indicator-Trading-Strategy-Combining-Bollinger-Bands-and-RSI" (Enhanced Bollinger Bands Strategy for Silver).

FMZ source id: 484597

Source
    https://www.fmz.com/strategy/484597 (PineScript v5, FMZ last modified 2025-03-03 10:38:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-242), BB 20 x 2; RSI 14 (30 / 70); volume SMA 20; SL 2 %, TP 4 % of each close; trail_points = a price level (no offset)
    crossover(close, lower) and rsi < 30 -> entry Long;  crossunder(close, upper) and rsi > 70 -> entry Short;  crossover(close, upper) and highVolume -> entry Breakout Long;  crossunder(close, lower) and highVolume -> entry Breakout Short
    every bar: exit("Exit Long", from_entry = "Long", stop = close x 0.98, limit = close x 1.04, trail_points = close x 0.985);  exit("Exit Short", from_entry = "Short", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits name only the "Long" / "Short" entries, so a breakout trade has no exit except the
      opposite entry (weird case). trail_points without trail_offset places no trailing stop (as #441084).
      The exits are re-sent every bar from that bar's close, so the levels move both ways; the signals
      follow them: a bar that reaches the previous bar's levels closes a "Long" / "Short" trade at the
      next open (mark trailing_stop_pending). Default pyramiding: a second long id while long adds
      nothing and the trade keeps its first id; the later call wins on a two-sided bar. The squeeze only
      colours the chart. The title names silver; the header is BTC_USDT. REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent bracket followed in the signals.
    2 generic: PASS, Bollinger re-entries and breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only (silver named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20 for the breakouts; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484597_bollinger_reentry_breakout_rolling_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl": [0.02, 0.03],
    "tp": [0.04, 0.06],
}
DEFAULT_PARAMS = {"sl": 0.02, "tp": 0.04}


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


def _xo(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    up_b, lo_b = basis + dev, basis - dev
    r = _rsi(c, 14).to_numpy()
    hv = (v > v.rolling(20).mean()).to_numpy()
    rev_l = _xo(c, lo_b) & (r < 30)
    rev_s = _xo(up_b, c) & (r > 70)
    brk_l = _xo(c, up_b) & hv
    brk_s = _xo(lo_b, c) & hv
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, kind = 0, 0, None
    for i in range(m):
        held = pine
        if i > 0 and kind == "rev" and held != 0:
            pc = cn[i - 1]
            if (held == 1 and (ln[i] <= pc * (1 - sl) or hn[i] >= pc * (1 + tp))) or \
               (held == -1 and (hn[i] >= pc * (1 + sl) or ln[i] <= pc * (1 - tp))):
                held, kind = 0, None
        new, nk = held, kind
        for flag, d, k in ((rev_l[i], 1, "rev"), (rev_s[i], -1, "rev"), (brk_l[i], 1, "brk"), (brk_s[i], -1, "brk")):
            if flag and new != d:
                new, nk = d, k                # an entry of the side already held adds nothing
        pine, kind = new, (nk if new != 0 else None)
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
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
