"""Two-stage fade of the move from the 02:00 UTC open, 1-hour bars: a close 0.25 % or more above the open of the 02:00 UTC
bar goes short, 0.25 % or more below goes long, each with the source's tick bracket as ATR fractions; a held side that
has run 0.35 % further is kept (the second-stage order re-enters it), as written.
Port of FMZ strategy #430872 "Two Stage Breakout Strategy" (Auto Entry Bot).

FMZ source id: 430872

Source
    https://www.fmz.com/strategy/430872 (PineScript v5, FMZ last modified 2023-11-02 15:58:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-173), SL 200 / TP 400 ticks, triggers 0.25 % / 0.35 %
    openPrice := open on the bar with hour == 2 and minute == 0; change = (close - openPrice) / openPrice x 100
    change >= 0.25 -> entry "Sell" short, exit(loss 200, profit 400 ticks);  change <= -0.25 -> entry "Buy" long, same exit
    short and change <= -0.35 -> cancel "Sell", entry "Sell2" short;  long and change >= 0.35 -> cancel "Buy", entry "Buy2" long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bracket is 200 / 400 ticks (20 / 40 USD on BTC_USDT at mintick 0.1); it
      becomes sl_atr / tp_atr x the Wilder ATR 14 of the signal bar, as fractions of its close (20 USD
      is about 0.1 ATR and 40 USD about 0.2 ATR on 1-hour BTC), fixed at entry.
    * hour and minute are the exchange time of the bar's open (UTC on Binance): the reference is the
      open of the 02:00 UTC bar, carried until the next one (UTC, no DST; not a venue open).
    * A held short with change <= -0.35 also meets the Buy rule: the Buy order reverses it and the
      Sell2 order then reverses back, so the short is held (mirror for longs). The port emits no
      signal on such a bar; the source's round trip and fresh bracket at the next open are not
      emitted (the first bracket stays). Same-side entries are ignored (pyramiding 1).
    * "Flat" follows the house bracket on bars (a stop checked first). strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick stop / target -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: reference open = the 02:00 UTC bar's open (exchange time, UTC on Binance; UTC, no DST; not a venue open).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430872_two_stage_open_fade"
FAMILY = "stop_and_reverse_bracket"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.1, 1.0],
    "tp_atr": [0.2, 2.0],
}
DEFAULT_PARAMS = {"trig1": 0.25, "trig2": 0.35, "ref_hour_utc": 2, "atr_len": 14, "sl_atr": 0.1, "tp_atr": 0.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).to_numpy()
    idx = bars_df.index.tz_convert("UTC")
    is_ref = (idx.hour == int(p["ref_hour_utc"])) & (idx.minute == 0)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    t1, t2 = float(p["trig1"]), float(p["trig2"])
    ref, pos, entry_i, s_, t_ = np.nan, 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if is_ref[i]:
            ref = ov[i]
        if np.isnan(ref) or np.isnan(af[i]):
            continue
        chg = (cv[i] - ref) / ref * 100
        if (pos == -1 and chg <= -t2) or (pos == 1 and chg >= t2):
            continue                                     # the second-stage order re-enters the held side
        if chg >= t1 and pos != -1:
            se[i], pos, entry_i = True, -1, i + 1
        elif chg <= -t1 and pos != 1:
            le[i], pos, entry_i = True, 1, i + 1
        else:
            continue
        s_, t_ = af[i] * float(p["sl_atr"]), af[i] * float(p["tp_atr"])
        sl_arr[i], tp_arr[i] = s_, t_
    return le, se, sl_arr, tp_arr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
