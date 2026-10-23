"""One-minute bars, short only: the RSI 20 of the session VWAP crossing under 85 goes short; the position closes when that RSI crosses back over 30, or 28 bars after it crossed under 30.
Port of FMZ strategy #437003 "基于RSI指标的跨时间框架策略VWAP-RSI-Oversold-Crossunder-BTC-Short-Strategy" (Soran Strategy 2 - SHORT SIGNALS).

FMZ source id: 437003

Source
    https://www.fmz.com/strategy/437003 (PineScript v4, FMZ last modified 2023-12-29 14:12:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 131-195), resolution "" (chart); RSI 20 of vwap(close); levels 85 / 30; late leave 28 bars; Laguerre off
    rsiVWAP = security(tickerid, "", rsi(vwap(close), 20));  crossunder(rsiVWAP, 85) -> entry Short
    close Short when (timebear and crossunder(rsiVWAP, 30)[28]) or crossover(rsiVWAP, 30)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The resolution input is empty, so the security() call is the chart itself. vwap(close) is the
      session VWAP, anchored at the broker-day start (as earlier ports). "and" binds before "or", so the
      close is the 28-bars-late crossunder test or any crossover of 30, as written. The long inputs feed
      nothing (no long orders). The 2020 start is dropped. Short only. 50 % of equity is sizing. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWAP-RSI overbought crossunder shorts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 50 % of equity, capital 1000, pyramiding 1, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG437003 (2 members, best partner #443128, Jaccard 0.808); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP of the close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start; the 2020 start dropped.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437003_vwap_rsi20_overbought_crossunder_1m_short"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14],
    "late_leave": [28, 14],
}
DEFAULT_PARAMS = {"length": 20, "ob": 85.0, "os": 30.0, "late_leave": 28}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    r = _rsi(vwap, int(p["length"]))
    ob, os_ = float(p["ob"]), float(p["os"])
    ent = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    cu = (r < os_) & (r.shift(1) >= os_)
    co = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    late = cu.shift(int(p["late_leave"]), fill_value=False).to_numpy()
    ext = late | co
    m = len(ent)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            se[i], pos = True, -1
        elif pos == -1 and ext[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
