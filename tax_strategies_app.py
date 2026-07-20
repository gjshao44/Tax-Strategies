import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import json
from engine import calculate_roadmap, calculate_comprehensive_tax
from config import LANG_MAP

st.set_page_config(page_title="Retirement Tax Strategy Planner", layout="wide")

# Place this at the very top of your app
defaults = {
    "ss_h_monthly": 4000,
    "ss_h_start": 2029,
    "ss_w_monthly": 3000,
    "ss_w_start": 2029,
    "legacy_weight": 0.8,
    "working_salary": 200000,
    "annual_expense": 100000,
    "qd_perc_raw" : 80,
    "retire_year" : 2026,
    "h_age_at_retire" : 64,
    "w_age_at_retire" : 64,
    "ira_h_init" : 1500000,
    "ira_w_init" : 10000,
    "roth_init" : 100000,
    "brokerage_init" : 1000000,
    "ira_growth_raw" : 4.0,
    "roth_growth_raw" : 5.0,
    "broker_growth_raw" : 3.0,
    "inflation_rate_raw" : 2.5,
    "ss_est_age_h" : 67,
    "ss_h_monthly" : 4000,
    "ss_est_age_w" : 67,
    "ss_w_monthly" : 3000,
    "annual_401k" : 23500,
    "annual_saving_rate" : 30,
    "lab_max_irmaa" : 5,
    "sim_years" : 25,
    "muni_yield_slider" : 4.0, 
    "taxable_yield_slider" : 5.0,
    "taxable_div_in": 0,
    "muni_int_in" : 0,
    "annual_ltcg": 0

}

for key, default_value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Then set the specific derived ones manually
if "ss_est_amt_h" not in st.session_state:
    st.session_state["ss_est_amt_h"] = st.session_state["ss_h_monthly"]
if "ss_est_amt_q" not in st.session_state:
    st.session_state["ss_est_amt_w"] = st.session_state["ss_w_monthly"]

GROWTH_PROFILE_PARAMS = {
    "ultra_conservative": {"shift": -4.0, "stddev": 3.0},
    "conservative": {"shift": -2.0, "stddev": 6.0},
    "moderate": {"shift": 0.0, "stddev": 10.0},
    "aggressive": {"shift": 2.0, "stddev": 14.0},
}

# --- 2. SIDEBAR INPUTS ---
if st.session_state.get("_apply_all_pending"):
    st.session_state["_apply_all_pending"] = False
    for k, v in st.session_state["_apply_all_values"].items():
        st.session_state[k] = v

with st.sidebar:
    lang = st.radio("Language / 语言选择", ["English", "Chinese"], horizontal=True)
    t = LANG_MAP[lang]

    st.header(t["sidebar_levers"])
    status_options = ["MFJ", "Single", "MFS"]
    saved_status = st.session_state.get("tax_status", "MFJ")
    status_idx = status_options.index(saved_status) if saved_status in status_options else 0
    tax_status = st.selectbox(t["filing_status"], status_options, index=status_idx)
    sim_years = st.slider("Simulation Horizon (Years)", 20, 40)
    st.slider("Annual Roth Conversion ($)", 0, 200000, step=5000, key="roth_conv")
    ws_map = {"tax_efficient": t["ws_tax_efficient"], "ira_first": t["ws_ira_first"], "roth_first": t["ws_roth_first"], "proportional": t["ws_proportional"]}
    ws_keys = list(ws_map.keys())
    ws_labels = list(ws_map.values())
    saved_ws = st.session_state.get("withdrawal_strategy", "tax_efficient")
    ws_idx = ws_keys.index(saved_ws) if saved_ws in ws_keys else 0
    ws_selected_label = st.selectbox(t["withdrawal_label"], ws_labels, index=ws_idx, help=t["withdrawal_help"])
    withdrawal_strategy = ws_keys[ws_labels.index(ws_selected_label)]
    gp_map = {"ultra_conservative": t["gp_ultra_conservative"], "conservative": t["gp_conservative"], "moderate": t["gp_moderate"], "aggressive": t["gp_aggressive"]}
    gp_keys = list(gp_map.keys())
    gp_labels = list(gp_map.values())
    saved_gp = st.session_state.get("growth_profile", "moderate")
    gp_idx = gp_keys.index(saved_gp) if saved_gp in gp_keys else 2
    gp_selected_label = st.selectbox(t["growth_profile_label"], gp_labels, index=gp_idx, help=t["growth_profile_help"])
    growth_profile = gp_keys[gp_labels.index(gp_selected_label)]

    st.header(t["sidebar_cash"])
    working_salary = st.number_input("Annual Working Salary ($)", step=1000, help="Your current gross salary. Applied as income in the retirement year and used for retire-timing analysis.")
    annual_expense = st.number_input("Annual Living Expense (Today's $)", step=1000, key="annual_expense")
    qd_perc_raw = st.slider(t["qd_ratio"], 0, 100)
    qd_perc = qd_perc_raw / 100

    st.header("📥 Passive Income (Retirement)")
    st.number_input("Annual Taxable Dividends ($)", step=1000,key="taxable_div_in", help="Dividend income from taxable brokerage accounts during retirement.")
    taxable_div_in = st.session_state["taxable_div_in"]
    st.number_input("Annual Tax-Free Muni Interest ($)", step=1000,key="muni_int_in", help="Municipal bond interest income (tax-exempt).")
    muni_int_in = st.session_state["muni_int_in"]
    annual_ltcg = st.number_input("Annual Capital Gains Realized ($)", step=1000, key="annual_ltcg", help="Expected annual long-term capital gains from brokerage account sales.")
    ss_h_monthly = st.number_input("Husband SS Monthly ($)", step=100, help="Estimated Social Security monthly benefit.", key="ss_h_monthly")
    ss_h_start = st.number_input("Husband SS Start Year", step=1, key="ss_h_start")
    ss_w_monthly = st.number_input("Wife SS Monthly ($)", step=100, help="Estimated Social Security monthly benefit.", key="ss_w_monthly")
    ss_w_start = st.number_input("Wife SS Start Year", step=1, key="ss_w_start")
    _total_passive = taxable_div_in + muni_int_in + annual_ltcg + (ss_h_monthly + ss_w_monthly) * 12
    st.caption(f"**Total passive income (at full SS): ${_total_passive:,.0f}/yr**")

    with st.expander(t["sidebar_timeline"], expanded=False):
        retire_year = st.number_input("Full Retirement Year", step=1, key="retire_year")
        h_age_at_retire = st.number_input(f"Husband Age in {retire_year}", step=1, key="h_age_at_retire")
        w_age_at_retire = st.number_input(f"Wife Age in {retire_year}", step=1, key="w_age_at_retire")

    with st.expander(t["sidebar_assets"], expanded=False):
        ira_h_init = st.number_input("Husband IRA Balance ($)",step=1000, key="ira_h_init")
        ira_w_init = st.number_input("Wife IRA Balance ($)",step=1000, key="ira_w_init")
        roth_init = st.number_input("Roth IRA Balance ($)",step=1000, key="roth_init")
        brokerage_init = st.number_input("Taxable Brokerage Balance ($)",step=1000, key="brokerage_init")

    with st.expander(t["sidebar_growth"], expanded=False):
        ira_growth_raw = st.slider("IRA Growth Rate (%)", 1.0, 10.0, step=0.1, key="ira_growth_raw")
        roth_growth_raw = st.slider("Roth Growth Rate (%)", 1.0, 10.0, step=0.1, key="roth_growth_raw")
        broker_growth_raw = st.slider("Brokerage Growth Rate (%)", 1.0, 10.0, step=0.1, key="broker_growth_raw")
        inflation_rate_raw = st.slider("Inflation Rate (%)", 0.0, 5.0, step=0.1, key="inflation_rate_raw")
        inflation_rate = inflation_rate_raw / 100

    gp_shift = GROWTH_PROFILE_PARAMS[growth_profile]["shift"]
    ira_growth = max(0.5, ira_growth_raw + gp_shift) / 100
    roth_growth = max(0.5, roth_growth_raw + gp_shift) / 100
    broker_growth = max(0.5, broker_growth_raw + gp_shift) / 100
    if gp_shift != 0:
        st.caption(t["growth_profile_caption"].format(shift=gp_shift, ira=ira_growth*100, roth=roth_growth*100, broker=broker_growth*100))

    st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # 2. Display the Copyright Notice
    st.sidebar.caption("© 2026 G. Shao (github gjshao44). All rights reserved.")

    # 3. Add scannable links to your policy files
    # Note: If hosting publicly, replace these names with your live GitHub or website URLs
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; opacity: 0.7;">
            <a href="https://github.com/gjshao44/Tax-Strategies/blob/main/TERMS.md" target="_blank" style="color: inherit; text-decoration: none; margin-right: 10px;">Terms of Service</a> | 
            <a href="https://github.com/gjshao44/Tax-Strategies/blob/main/PRIVACY.md" target="_blank" style="color: inherit; text-decoration: none; margin-left: 10px;">Privacy Policy</a>
        </div>
        """,
        unsafe_allow_html=True
)


def estimate_ss_at_age(known_monthly, known_age, target_age, fra=67):
    """Extrapolate SS monthly benefit from a known estimate at one age to any claiming age (62-70)."""
    fra_monthly = known_monthly
    if known_age < fra:
        months_early = (fra - known_age) * 12
        if months_early <= 36:
            reduction = months_early * (5/9/100)
        else:
            reduction = 36 * (5/9/100) + (months_early - 36) * (5/12/100)
        fra_monthly = known_monthly / (1 - reduction)
    elif known_age > fra:
        months_late = (known_age - fra) * 12
        credit = months_late * (8/12/100)
        fra_monthly = known_monthly / (1 + credit)

    if target_age == fra:
        return fra_monthly
    elif target_age < fra:
        months_early = (fra - target_age) * 12
        if months_early <= 36:
            reduction = months_early * (5/9/100)
        else:
            reduction = 36 * (5/9/100) + (months_early - 36) * (5/12/100)
        return fra_monthly * (1 - reduction)
    else:
        months_late = (target_age - fra) * 12
        credit = months_late * (8/12/100)
        return fra_monthly * (1 + credit)

# --- 4. CALCULATION ENGINE ---
@st.cache_data
def get_optimal_conversion(core_args, lab_horizon, legacy_weight, max_irmaa_limit=5):
    mid_weight = 1.0 - legacy_weight
    total_ira_init = core_args["ira_h_init"] + core_args["ira_w_init"]
    
    # Dynamically scale upper bound based on IRA size
    upper_bound = min(500000, max(200000, int((total_ira_init * 0.1) // 10000 * 10000)))
    upper_bound = min(upper_bound, total_ira_init)
    upper_bound = max(10000, int(upper_bound // 10000 * 10000))
    
    test_amounts = list(range(0, upper_bound + 1, 10000))
    
    best_score = -1e18
    best_amt = 0
    mid_idx = int(lab_horizon * 0.33)
    end_idx = int(lab_horizon * 0.95)
    
    for amt in test_amounts:
        df_sim = calculate_roadmap(**core_args, conv_override=amt, horizon_override=lab_horizon)
        score = (df_sim.iloc[mid_idx]['Expected Net Worth'] * mid_weight) + (df_sim.iloc[end_idx]['Expected Net Worth'] * legacy_weight)
        
        # Apply IRMAA constraint penalty
        max_tier_reached = df_sim['irmaa_tier'].max()
        penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
        score -= penalty
        
        if score > best_score:
            best_score = score
            best_amt = amt
    return best_amt

@st.cache_data
def run_monte_carlo(core_args, profile_key, ira_growth_raw, roth_growth_raw, broker_growth_raw, n_sims=100, seed=42):
    params = GROWTH_PROFILE_PARAMS[profile_key]
    shift = params["shift"]
    stddev = params["stddev"] / 100
    mean_ira = max(0.5, ira_growth_raw + shift) / 100
    mean_roth = max(0.5, roth_growth_raw + shift) / 100
    mean_broker = max(0.5, broker_growth_raw + shift) / 100
    horizon = core_args.get("horizon_override") or core_args["sim_years"]
    rng = np.random.default_rng(seed)
    all_nw = np.zeros((n_sims, horizon))
    for s in range(int(n_sims)):
        ira_seq = tuple(float(x) for x in rng.normal(mean_ira, stddev, int(horizon)))
        roth_seq = tuple(float(x) for x in rng.normal(mean_roth, stddev, int(horizon)))
        broker_seq = tuple(float(x) for x in rng.normal(mean_broker, stddev, int(horizon)))
        gs = (ira_seq, roth_seq, broker_seq)
        df_sim = calculate_roadmap(
            **{**core_args, "ira_growth": mean_ira, "roth_growth": mean_roth, "broker_growth": mean_broker},
            growth_sequence=gs
        )
        all_nw[s] = df_sim["Expected Net Worth"].values
    years = list(range(int(core_args["retire_year"]), int(core_args["retire_year"]) + int(horizon)))
    p10 = np.percentile(all_nw, 10, axis=0)
    p50 = np.percentile(all_nw, 50, axis=0)
    p90 = np.percentile(all_nw, 90, axis=0)
    return years, p10, p50, p90

@st.cache_data
def run_retirement_confidence(core_args, ira_growth_raw, roth_growth_raw, broker_growth_raw, n_sims=200, seed=42):
    """Run Monte Carlo for a single retirement scenario. Returns confidence % and percentile net worths."""
    stddev = 0.16
    mean_ira = ira_growth_raw / 100
    mean_roth = roth_growth_raw / 100
    mean_broker = broker_growth_raw / 100
    horizon = core_args["sim_years"]
    rng = np.random.default_rng(seed)
    final_nw = np.zeros(n_sims)
    money_lasts_count = 0
    for s in range(int(n_sims)):
        ira_seq = tuple(float(x) for x in rng.normal(mean_ira, stddev, int(horizon)))
        roth_seq = tuple(float(x) for x in rng.normal(mean_roth, stddev, int(horizon)))
        broker_seq = tuple(float(x) for x in rng.normal(mean_broker, stddev, int(horizon)))
        gs = (ira_seq, roth_seq, broker_seq)
        df_sim = calculate_roadmap(
            **{**core_args, "ira_growth": mean_ira, "roth_growth": mean_roth, "broker_growth": mean_broker},
            growth_sequence=gs
        )
        final_total_nw = df_sim.iloc[-1]["Total Net Worth"]
        final_nw[s] = final_total_nw
        if final_total_nw > 0:
            money_lasts_count += 1
    confidence = money_lasts_count / n_sims * 100
    nw_90 = float(np.percentile(final_nw, 10))
    nw_75 = float(np.percentile(final_nw, 25))
    nw_50 = float(np.percentile(final_nw, 50))
    return confidence, nw_90, nw_75, nw_50


# --- 5. UI DISPLAY ---
st.title(t["title"])

core_args = {
    "ira_h_init": ira_h_init, "ira_w_init": ira_w_init, "roth_init": roth_init, "brokerage_init": brokerage_init,
    "retire_year": retire_year, "sim_years": sim_years, "h_age_at_retire": h_age_at_retire, "w_age_at_retire": w_age_at_retire,
    "tax_status": tax_status, "roth_conv": st.session_state.get("roth_conv", 0), "annual_ltcg": annual_ltcg, "annual_expense": annual_expense, "qd_perc": qd_perc,
    "taxable_div_in": taxable_div_in, "muni_int_in": muni_int_in, "last_salary": working_salary,
    "ss_h_monthly": ss_h_monthly, "ss_h_start": ss_h_start, "ss_w_monthly": ss_w_monthly, "ss_w_start": ss_w_start,
    "ira_growth": ira_growth, "roth_growth": roth_growth, "broker_growth": broker_growth, "inflation_rate": inflation_rate,
    "lang": lang, "withdrawal_strategy": withdrawal_strategy
}

lab_horizon = max(20, sim_years)
legacy_weight_val = st.session_state.get("lab_legacy_weight", 0.80)
max_irmaa_limit_val = st.session_state.get("lab_max_irmaa", 5)
best_amt_for_calc = get_optimal_conversion(core_args, lab_horizon, legacy_weight_val, max_irmaa_limit_val)
st.session_state['best_amt'] = best_amt_for_calc

tab_retire, tab_ss, tab_lab, tab_muni, tab_cg, tab_whatif, tab_roadmap, tab_data = st.tabs([t["tab_retire"], t["tab_ss"], t["tab_lab"], t["tab_muni"], t["tab_cg"], t["tab_whatif"], t["tab_roadmap"], t["tab_data"]])

with tab_retire:
    st.subheader(t["retire_h"])
    st.caption(t["retire_desc"])

    with st.expander("Pre-retirement savings assumptions (for delayed retirement scenarios)", expanded=False):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            annual_401k = st.number_input(
                "Annual 401k Contribution ($)",
                step=1000,
                help="How much you contribute to 401k/IRA per year while working.",
                key="annual_401k"
            )
        with col_r2:
            annual_saving_rate = st.slider(
                "Annual Savings Rate (%)",
                min_value=10, max_value=60,
                step=5,
                help="Total % of salary saved (including 401k). Remainder after 401k goes to brokerage.",
                key="annual_saving_rate"
            )

    end_year = retire_year + sim_years
    retire_test_years = list(range(int(retire_year) - 1, int(retire_year) + 5))
    retire_summary_rows = []

    with st.spinner("Running Monte Carlo simulations for each retirement year..."):
        for ry in retire_test_years:
            years_delta = ry - retire_year
            test_h_age = h_age_at_retire + years_delta
            test_w_age = w_age_at_retire + years_delta
            sim_horizon_for_scenario = end_year - ry

            if sim_horizon_for_scenario < 5:
                continue

            test_ira_h = ira_h_init
            test_broker = brokerage_init
            test_roth = roth_init

            if years_delta > 0:
                annual_total_saving = working_salary * (annual_saving_rate / 100)
                annual_to_broker = max(0, annual_total_saving - annual_401k)
                for yr_offset in range(int(years_delta)):
                    test_ira_h = test_ira_h * (1 + ira_growth) + annual_401k
                    test_broker = test_broker * (1 + broker_growth) + annual_to_broker
                    test_roth = test_roth * (1 + roth_growth)
            elif years_delta < 0:
                for yr_offset in range(abs(int(years_delta))):
                    test_ira_h = test_ira_h / (1 + ira_growth)
                    test_broker = test_broker / (1 + broker_growth)
                    test_roth = test_roth / (1 + roth_growth)

            test_args = {
                **core_args,
                "retire_year": ry,
                "sim_years": sim_horizon_for_scenario,
                "h_age_at_retire": test_h_age,
                "w_age_at_retire": test_w_age,
                "ira_h_init": test_ira_h,
                "roth_init": test_roth,
                "brokerage_init": test_broker,
                "last_salary": working_salary if years_delta >= 0 else 0,
            }

            confidence, nw_90, nw_75, nw_50 = run_retirement_confidence(
                test_args, ira_growth_raw, roth_growth_raw, broker_growth_raw
            )

            retire_summary_rows.append({
                t["retire_col_year"]: ry,
                t["retire_col_age"]: f"{test_h_age}/{test_w_age}",
                t["retire_col_confidence"]: confidence,
                t["retire_col_nw_90"]: nw_90,
                t["retire_col_nw_75"]: nw_75,
                t["retire_col_nw_50"]: nw_50,
                t["retire_col_working_years"]: f"{int(years_delta):+d}" if years_delta != 0 else "baseline",
            })

    # --- Key Insight: combined income summary + retirement confidence ---
    ss_annual = (ss_h_monthly + ss_w_monthly) * 12
    passive_total = taxable_div_in + muni_int_in + annual_ltcg + ss_annual
    passive_pre_ss = taxable_div_in + muni_int_in + annual_ltcg
    income_gap = annual_expense - passive_total

    safe_scenarios = [r for r in retire_summary_rows if r[t["retire_col_confidence"]] >= 90]
    current_row = next((r for r in retire_summary_rows if r[t["retire_col_year"]] == retire_year), None)
    cur_conf = current_row[t["retire_col_confidence"]] if current_row else 0

    if income_gap > 0:
        gap_text = f"Annual expense **\\${annual_expense:,.0f}** − passive income **\\${passive_total:,.0f}** = **\\${income_gap:,.0f}/yr from savings** (\\${annual_expense - passive_pre_ss:,.0f}/yr before SS starts)."
    else:
        gap_text = f"Annual expense **\\${annual_expense:,.0f}** is fully covered by passive income **\\${passive_total:,.0f}** — surplus of **\\${-income_gap:,.0f}/yr** after SS starts."

    if safe_scenarios:
        earliest_safe = min(safe_scenarios, key=lambda r: r[t["retire_col_year"]])
        earliest_year = earliest_safe[t["retire_col_year"]]
        earliest_age = earliest_safe[t["retire_col_age"]]
        confidence_val = earliest_safe[t["retire_col_confidence"]]
        retire_text = f"You can afford to retire as early as **{earliest_year}** (age {earliest_age}) with **{confidence_val:.0f}% confidence** your money lasts through {end_year}. Your current plan (retire {retire_year}) has **{cur_conf:.0f}% confidence**."
        st.success(f"**{t['retire_insight']}:** {gap_text}\n\n{retire_text}")
    else:
        best = max(retire_summary_rows, key=lambda r: r[t["retire_col_confidence"]])
        retire_text = f"No tested retirement year achieves 90% confidence. The best is **{best[t['retire_col_year']]}** (age {best[t['retire_col_age']]}) at **{best[t['retire_col_confidence']]:.0f}% confidence**. Consider reducing expenses or delaying retirement further."
        st.warning(f"**{t['retire_insight']}:** {gap_text}\n\n{retire_text}")

    if safe_scenarios:
        if earliest_year != retire_year:
            if st.button(f"Apply: Retire in {earliest_year} (age {earliest_age})", key="apply_retire"):
                delta = earliest_year - retire_year
                st.session_state["retire_year"] = earliest_year
                st.session_state["h_age_at_retire"] = h_age_at_retire + delta
                st.session_state["w_age_at_retire"] = w_age_at_retire + delta
                st.rerun()

    # --- Charts ---
    st.divider()

    # Income vs Expense over time
    gap_chart_data = []
    for ry in retire_test_years:
        years_delta = ry - retire_year
        test_h_age = h_age_at_retire + years_delta
        sim_horizon = end_year - ry
        if sim_horizon < 5:
            continue
        label = f"{ry} (age {test_h_age})"
        for yr_idx in range(int(sim_horizon)):
            year = ry + yr_idx
            inf_factor = (1 + inflation_rate) ** yr_idx
            yr_expense = annual_expense * inf_factor
            h_ss = (ss_h_monthly * 12 * inf_factor) if year >= ss_h_start else 0
            w_ss = (ss_w_monthly * 12 * inf_factor) if year >= ss_w_start else 0
            yr_income = (taxable_div_in + muni_int_in + annual_ltcg) * inf_factor + h_ss + w_ss
            gap_chart_data.append({
                "Year": year,
                "Scenario": label,
                "Expense": yr_expense,
                "Passive Income": yr_income,
                "Gap (from savings)": max(0, yr_expense - yr_income),
            })

    df_gap = pd.DataFrame(gap_chart_data)
    current_label = f"{retire_year} (age {h_age_at_retire})"
    df_gap_current = df_gap[df_gap["Scenario"] == current_label].copy()

    if not df_gap_current.empty:
        st.subheader(t["gap_chart_h"])
        st.caption(t["gap_chart_desc"])
        gap_melted = df_gap_current.melt(
            id_vars=["Year"],
            value_vars=["Expense", "Passive Income", "Gap (from savings)"],
            var_name="Category", value_name="Amount"
        )
        gap_line_chart = alt.Chart(gap_melted).mark_line(strokeWidth=2.5).encode(
            x=alt.X("Year:Q", axis=alt.Axis(format="d")),
            y=alt.Y("Amount:Q", title="Annual Amount ($)"),
            color=alt.Color("Category:N", scale=alt.Scale(
                domain=["Expense", "Passive Income", "Gap (from savings)"],
                range=["#e74c3c", "#2ecc71", "#f39c12"]
            )),
            strokeDash=alt.StrokeDash("Category:N", scale=alt.Scale(
                domain=["Expense", "Passive Income", "Gap (from savings)"],
                range=[[1, 0], [1, 0], [5, 5]]
            )),
            tooltip=[
                alt.Tooltip("Year:Q", format="d"),
                alt.Tooltip("Category:N"),
                alt.Tooltip("Amount:Q", format="$,.0f"),
            ]
        )
        st.altair_chart(gap_line_chart, width='stretch')

    # Confidence bar chart
    st.subheader(t["retire_chart_h"])
    st.caption(t["retire_chart_desc"])

    df_retire_chart = pd.DataFrame(retire_summary_rows)
    conf_col = t["retire_col_confidence"]
    df_retire_chart["_risk_level"] = df_retire_chart[conf_col].apply(
        lambda c: "Safe (≥90%)" if c >= 90 else ("Moderate (75-89%)" if c >= 75 else "At Risk (<75%)")
    )
    bar_chart = alt.Chart(df_retire_chart).mark_bar(
        cornerRadiusTopLeft=4, cornerRadiusTopRight=4
    ).encode(
        x=alt.X(f'{t["retire_col_year"]}:O', title="Retirement Year"),
        y=alt.Y(f'{conf_col}:Q', title="Confidence (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("_risk_level:N", scale=alt.Scale(
            domain=["Safe (≥90%)", "Moderate (75-89%)", "At Risk (<75%)"],
            range=["#2ecc71", "#f39c12", "#e74c3c"]
        ), legend=alt.Legend(title="Risk Level")),
        tooltip=[
            alt.Tooltip(f'{t["retire_col_year"]}:O', title="Retire Year"),
            alt.Tooltip(f'{t["retire_col_age"]}:N', title="Age"),
            alt.Tooltip(f'{conf_col}:Q', format='.0f', title="Confidence (%)"),
            alt.Tooltip(f'{t["retire_col_nw_90"]}:Q', format='$,.0f', title="Final NW (90% conf)"),
            alt.Tooltip(f'{t["retire_col_nw_50"]}:Q', format='$,.0f', title="Final NW (50% conf)"),
        ]
    )

    threshold_line = alt.Chart(pd.DataFrame({"y": [90]})).mark_rule(
        color="#2ecc71", strokeDash=[5, 5], strokeWidth=2
    ).encode(y="y:Q")

    st.altair_chart(bar_chart + threshold_line, width='stretch')

    st.subheader(t["retire_table_h"])
    df_retire_summary = pd.DataFrame(retire_summary_rows)
    st.dataframe(
        df_retire_summary.style.format({
            t["retire_col_confidence"]: "{:.0f}%",
            t["retire_col_nw_90"]: "${:,.0f}",
            t["retire_col_nw_75"]: "${:,.0f}",
            t["retire_col_nw_50"]: "${:,.0f}",
        }),
        width='stretch',
        hide_index=True
    )

with tab_ss:
    st.subheader(t["ss_h"])
    st.caption(t["ss_desc"])

    st.markdown(f"**{t['ss_input_h']}**")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        ss_est_age_h = st.number_input(
            t["ss_estimate_age_h"], min_value=62, max_value=70,
            key="ss_est_age_h"
        )
    with col_s2:
        ss_est_amt_h = st.number_input(
            t["ss_estimate_amt_h"], min_value=0, max_value=10000,
            step=100,
            key="ss_est_amt_h"
        )
    with col_s3:
        ss_est_age_w = st.number_input(
            t["ss_estimate_age_w"], min_value=62, max_value=70,
            key="ss_est_age_w"
        )
    with col_s4:
        ss_est_amt_w = st.number_input(
            t["ss_estimate_amt_w"], min_value=0, max_value=10000,
            step=100,
            key="ss_est_amt_w"
        )

    birth_year_h = retire_year - h_age_at_retire
    birth_year_w = retire_year - w_age_at_retire

    ss_strategies = [
        ("Both at 62", 62, 62),
        ("Both at 65", 65, 65),
        ("Both at FRA (67)", 67, 67),
        ("Both at 70", 70, 70),
        ("H:70 / W:62", 70, 62),
        ("H:67 / W:62", 67, 62),
        ("H:62 / W:67", 62, 67),
    ]

    ss_chart_data = []
    ss_summary_rows = []

    h_fra_monthly = estimate_ss_at_age(ss_est_amt_h, ss_est_age_h, 67)

    seen_effective = set()
    with st.spinner("Comparing Social Security claiming strategies..."):
        for label, h_claim_age, w_claim_age in ss_strategies:
            effective_h_claim = max(h_claim_age, h_age_at_retire)
            effective_w_claim = max(w_claim_age, w_age_at_retire)
            if (effective_h_claim, effective_w_claim) in seen_effective:
                continue
            seen_effective.add((effective_h_claim, effective_w_claim))
            h_monthly = estimate_ss_at_age(ss_est_amt_h, ss_est_age_h, effective_h_claim)
            w_monthly = estimate_ss_at_age(ss_est_amt_w, ss_est_age_w, effective_w_claim)
            h_start_year = birth_year_h + effective_h_claim
            w_start_year = birth_year_w + effective_w_claim

            test_args = {
                **core_args,
                "ss_h_monthly": h_monthly,
                "ss_h_start": h_start_year,
                "ss_w_monthly": w_monthly,
                "ss_w_start": w_start_year,
            }

            df_ss = calculate_roadmap(**test_args)

            effective_label = f"H:{effective_h_claim} / W:{effective_w_claim}"
            for _, row in df_ss.iterrows():
                ss_chart_data.append({
                    "Year": row["Year"],
                    "Expected Net Worth": row["Expected Net Worth"],
                    "Strategy": effective_label
                })

            ss_summary_rows.append({
                t["ss_col_strategy"]: effective_label,
                t["ss_col_h_age"]: effective_h_claim,
                t["ss_col_w_age"]: effective_w_claim,
                t["ss_col_h_monthly"]: h_monthly,
                t["ss_col_w_monthly"]: w_monthly,
                t["ss_col_annual"]: (h_monthly + w_monthly) * 12,
                t["ss_col_final_nw"]: df_ss.iloc[-1]["Expected Net Worth"],
                t["ss_col_total_tax"]: df_ss["OUT: Fed Tax"].sum(),
            })

    best_ss = max(ss_summary_rows, key=lambda r: r[t["ss_col_final_nw"]])
    worst_ss = min(ss_summary_rows, key=lambda r: r[t["ss_col_final_nw"]])
    ss_spread = best_ss[t["ss_col_final_nw"]] - worst_ss[t["ss_col_final_nw"]]
    st.info(f"**{t['ss_insight']}:** \"{best_ss[t['ss_col_strategy']]}\" produces **{ss_spread:,.0f}** more in expected net worth than \"{worst_ss[t['ss_col_strategy']]}\". Delaying SS generally wins if you have assets to bridge the gap, but dies with you — claiming earlier protects against longevity risk if assets are limited.")
    st.caption(f"⚠️ Results are sensitive to simulation horizon ({sim_years} years). A shorter horizon favors early claiming (more years of checks received). Try increasing the horizon to 30+ years to see if delayed claiming eventually wins.")

    best_h_claim = best_ss[t["ss_col_h_age"]]
    best_w_claim = best_ss[t["ss_col_w_age"]]
    best_h_monthly = best_ss[t["ss_col_h_monthly"]]
    best_w_monthly = best_ss[t["ss_col_w_monthly"]]
    best_h_start_yr = birth_year_h + best_h_claim
    best_w_start_yr = birth_year_w + best_w_claim
    current_match = (abs(best_h_monthly - ss_h_monthly) < 1 and abs(best_w_monthly - ss_w_monthly) < 1
                     and best_h_start_yr == ss_h_start and best_w_start_yr == ss_w_start)
    if not current_match:
        if st.button(f"Apply: {best_ss[t['ss_col_strategy']]} — H {best_h_monthly:,.0f}/mo at {best_h_claim}, W {best_w_monthly:,.0f}/mo at {best_w_claim}", key="apply_ss"):
            st.session_state["ss_h_monthly"] = int(best_h_monthly)
            st.session_state["ss_h_start"] = best_h_start_yr
            st.session_state["ss_w_monthly"] = int(best_w_monthly)
            st.session_state["ss_w_start"] = best_w_start_yr
            st.rerun()

    st.divider()
    st.subheader(t["ss_chart_h"])
    st.caption(t["ss_chart_desc"])
    df_ss_chart = pd.DataFrame(ss_chart_data)

    nearest_ss = alt.selection_point(nearest=True, on="pointerover", fields=["Year"], empty=False)

    base_ss = alt.Chart(df_ss_chart).encode(
        x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
        y=alt.Y('Expected Net Worth:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
        color=alt.Color('Strategy:N', legend=alt.Legend(title="SS Strategy")),
    )

    lines_ss = base_ss.mark_line(strokeWidth=2.5)

    selectors_ss = alt.Chart(df_ss_chart).mark_point(size=80, filled=True).encode(
        x='Year:Q',
        opacity=alt.value(0),
    ).add_params(nearest_ss)

    points_ss = base_ss.mark_point(size=60, filled=True).encode(
        opacity=alt.condition(nearest_ss, alt.value(1), alt.value(0)),
        tooltip=[
            alt.Tooltip('Strategy:N', title="Strategy"),
            alt.Tooltip('Year:Q', format='d', title="Year"),
            alt.Tooltip('Expected Net Worth:Q', format='$,.0f', title="Net Worth"),
        ]
    )

    vrule_ss = alt.Chart(df_ss_chart).mark_rule(color='gray', strokeDash=[3, 3]).encode(
        x='Year:Q',
        opacity=alt.condition(nearest_ss, alt.value(0.6), alt.value(0)),
    )

    st.altair_chart(alt.layer(lines_ss, selectors_ss, points_ss, vrule_ss), width='stretch')

    st.subheader(t["ss_table_h"])
    df_ss_summary = pd.DataFrame(ss_summary_rows)
    st.dataframe(
        df_ss_summary.style.format({
            t["ss_col_h_monthly"]: "${:,.0f}",
            t["ss_col_w_monthly"]: "${:,.0f}",
            t["ss_col_annual"]: "${:,.0f}",
            t["ss_col_final_nw"]: "${:,.0f}",
            t["ss_col_total_tax"]: "${:,.0f}",
        }),
        width='stretch',
        hide_index=True
    )
    st.caption(f"Note: Benefits shown are each spouse's own benefit at their claiming age. If W's own benefit < 50% of H's FRA (${h_fra_monthly * 0.5:,.0f}/mo), she may be eligible for a spousal top-up once H files — enter the higher amount as her estimate if applicable.")

    with st.expander("📋 Reference: Extrapolated Monthly Benefits by Claiming Age"):
        ss_extrap_data = []
        for age in range(62, 71):
            h_benefit = estimate_ss_at_age(ss_est_amt_h, ss_est_age_h, age)
            w_benefit = estimate_ss_at_age(ss_est_amt_w, ss_est_age_w, age)
            ss_extrap_data.append({
                "Claim Age": age,
                "H Monthly": f"${h_benefit:,.0f}",
                "W Monthly": f"${w_benefit:,.0f}",
                "Combined Annual": f"${(h_benefit + w_benefit) * 12:,.0f}",
            })
        st.dataframe(pd.DataFrame(ss_extrap_data), width='stretch', hide_index=True)
        st.caption("Based on SSA formula: 5/9% per month reduction before FRA (first 36 months), 5/12% per month thereafter. 8% per year delayed credit after FRA up to age 70.")

with tab_lab:
    st.subheader(t["lab_h"])
    st.caption(t["lab_desc"])

    # --- Optimization Preferences ---
    st.subheader(t["lab_pref_h"])
    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        legacy_weight = st.slider(
            t["lab_pref_label"],
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            help=t["lab_pref_help"],
            key="lab_legacy_weight"
        )
        if legacy_weight < 0.3:
            st.caption("← Prioritizing **spending power now**")
        elif legacy_weight > 0.7:
            st.caption("→ Prioritizing **leaving more later**")
        else:
            st.caption("↔ Balanced between spending now and leaving later")
    with col_pref2:
        irmaa_monthly = {0: "$0", 1: "$80", 2: "$200", 3: "$320", 4: "$440", 5: "$480+"}
        max_irmaa_limit = st.slider(
            t["lab_irmaa_label"],
            min_value=0,
            max_value=5,
            step=1,
            help=t["lab_irmaa_help"],
            key="lab_max_irmaa"
        )
        surcharge_str = irmaa_monthly[max_irmaa_limit]
        if max_irmaa_limit == 0:
            st.caption(f"Max Medicare surcharge: **{surcharge_str}/mo per person** (no extra cost)")
        elif max_irmaa_limit == 5:
            st.caption(f"Max Medicare surcharge: **no limit** (all tiers allowed)")
        else:
            st.caption(f"Max Medicare surcharge: **{surcharge_str}/mo per person**")
    mid_weight = 1.0 - legacy_weight

    st.success(f"💡 **{t['lab_roth_optimum']} {best_amt_for_calc:,.0f}** (current setting: {st.session_state.get('roth_conv', 0):,.0f})")
    if best_amt_for_calc != st.session_state.get('roth_conv', 0):
        if st.button(f"Apply: Set annual Roth conversion to {best_amt_for_calc:,.0f}", key="apply_roth_top"):
            st.session_state["_apply_all_pending"] = True
            st.session_state["_apply_all_values"] = {"roth_conv": int(best_amt_for_calc)}
            st.rerun()

    st.divider()

    st.subheader(t["lab_roth_h"], help=t["lab_roth_desc"].format(lab_horizon=lab_horizon))
    
    total_ira_init = ira_h_init + ira_w_init
    # Dynamically scale upper bound based on IRA size
    lab_upper_bound = min(500000, max(200000, int((total_ira_init * 0.1) // 10000 * 10000)))
    lab_upper_bound = min(lab_upper_bound, total_ira_init)
    lab_upper_bound = max(10000, int(lab_upper_bound // 10000 * 10000))
    
    test_amounts = list(range(0, lab_upper_bound + 1, 10000))
    lab_results = []
    
    mid_idx = int(lab_horizon * 0.33)
    end_idx = int(lab_horizon * 0.95)
    
    with st.spinner(f"Analyzing Roth Conversion amounts over {lab_horizon} years..."):
        for amt in test_amounts:
            res_df_sim = calculate_roadmap(**core_args, conv_override=amt, horizon_override=lab_horizon)
            
            mid_nw = res_df_sim.iloc[mid_idx]['Expected Net Worth']
            end_nw = res_df_sim.iloc[end_idx]['Expected Net Worth']
            weighted_score = (mid_nw * mid_weight) + (end_nw * legacy_weight)
            
            max_tier_reached = res_df_sim['irmaa_tier'].max()
            penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
            score = weighted_score - penalty
            
            lab_results.append({
                "amt": amt,
                "ex_nw": score,
                "raw_nw": weighted_score,
                "mid_nw": mid_nw,
                "end_nw": end_nw,
                "max_irmaa": max_tier_reached
            })
    
    res_df = pd.DataFrame(lab_results)
    best_amt = res_df.loc[res_df["ex_nw"].idxmax(), "amt"]
    best_row = res_df.loc[res_df["ex_nw"].idxmax()]
    
    # Chart 1: Roth Conversion with continuous line + colored points
    line = alt.Chart(res_df).mark_line(color='#bdc3c7', strokeWidth=3).encode(
        x=alt.X('amt:Q', title=t["lab_roth_chart_x"]),
        y=alt.Y('raw_nw:Q', title="Weighted Expected Net Worth ($)", scale=alt.Scale(zero=False))
    )
    points = alt.Chart(res_df).mark_point(size=60, filled=True).encode(
        x=alt.X('amt:Q'),
        y=alt.Y('raw_nw:Q'),
        color=alt.condition(
            f"datum.max_irmaa <= {max_irmaa_limit}",
            alt.value('#2ecc71'),  # Green if within limit
            alt.value('#e74c3c')   # Red if violating
        ),
        tooltip=[
            alt.Tooltip('amt:Q', title=t["lab_roth_chart_x"]),
            alt.Tooltip('raw_nw:Q', title="Expected Net Worth", format="$,.0f"),
            alt.Tooltip('max_irmaa:N', title="Max IRMAA Tier")
        ]
    )
    rule1 = alt.Chart(pd.DataFrame({'amt': [best_amt]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='amt:Q')
    st.altair_chart(line + points + rule1, width='stretch')
    st.caption("🟢 Green = within Medicare surcharge limit | 🔴 Red = exceeds limit | ┆ Dashed line = optimum")
    st.success(f"💡 **{t['lab_roth_optimum']} {best_amt:,.0f}**")

    c1, c2 = st.columns(2)
    c1.metric(f"🎯 Liquidity Milestone (Year {mid_idx})", f"${best_row['mid_nw']:,.0f}")
    c2.metric(f"🛡️ Legacy Security (Year {end_idx})", f"${best_row['end_nw']:,.0f}")

    st.divider()

    # Chart 2: Stop Age Optimizer
    st.subheader(t["lab_stop_h"], help=t["lab_stop_desc"].format(best_amt=best_amt))
    
    # We maintain a sensible range for age optimization regardless of horizon
    test_ages = list(range(65, 95))
    age_results = []
    
    with st.spinner("Optimizing Stop Age..."):
        for age in test_ages:
            res_age_df = calculate_roadmap(**core_args, conv_override=best_amt, conv_stop_age_override=age, horizon_override=lab_horizon)
            
            mid_nw = res_age_df.iloc[mid_idx]['Expected Net Worth']
            end_nw = res_age_df.iloc[end_idx]['Expected Net Worth']
            weighted_score = (mid_nw * 0.2) + (end_nw * 0.8)
            
            max_tier_reached = res_age_df['irmaa_tier'].max()
            penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
            score = weighted_score - penalty
            
            age_results.append({
                "age": age,
                "ex_nw": score,
                "raw_nw": weighted_score,
                "max_irmaa": max_tier_reached
            })
            
    res_age_df = pd.DataFrame(age_results)
    best_age = res_age_df.loc[res_age_df["ex_nw"].idxmax(), "age"]
    
    line2 = alt.Chart(res_age_df).mark_line(color='#bdc3c7', strokeWidth=3).encode(
        x=alt.X('age:Q', title=t["lab_stop_chart_x"], scale=alt.Scale(zero=False)),
        y=alt.Y('raw_nw:Q', title="Weighted Expected Net Worth ($)", scale=alt.Scale(zero=False))
    )
    points2 = alt.Chart(res_age_df).mark_point(size=60, filled=True).encode(
        x=alt.X('age:Q'),
        y=alt.Y('raw_nw:Q'),
        color=alt.condition(
            f"datum.max_irmaa <= {max_irmaa_limit}",
            alt.value('#3498db'),  # Blue if within limit
            alt.value('#e74c3c')   # Red if violating
        ),
        tooltip=[
            alt.Tooltip('age:Q', title=t["lab_stop_chart_x"]),
            alt.Tooltip('raw_nw:Q', title="Expected Net Worth", format="$,.0f"),
            alt.Tooltip('max_irmaa:N', title="Max IRMAA Tier")
        ]
    )
    rule2 = alt.Chart(pd.DataFrame({'age': [best_age]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='age:Q')
    st.altair_chart(line2 + points2 + rule2, width='stretch')
    st.caption("🔵 Blue = within Medicare surcharge limit | 🔴 Red = exceeds limit | ┆ Dashed line = optimum")
    st.warning(f"🛑 **{t['lab_stop_optimum']} {best_age}**")

    st.divider()

    # --- Golden Window Visualization ---
    st.markdown(f"#### {t['lab_golden_h']}")
    st.caption(t["lab_golden_desc"])

    birth_year_h_lab = retire_year - h_age_at_retire
    rmd_start_age = 75 if birth_year_h_lab >= 1960 else 73
    ss_start_year_h = ss_h_start
    rmd_start_year = birth_year_h_lab + rmd_start_age
    golden_start = retire_year
    golden_end = min(ss_start_year_h, rmd_start_year) - 1

    golden_data = []
    for yr in range(int(retire_year), int(retire_year + sim_years)):
        age_in_yr = h_age_at_retire + (yr - retire_year)
        if yr <= golden_end:
            phase = "Golden Window (low tax)"
        elif yr < rmd_start_year:
            phase = "SS income (moderate tax)"
        else:
            phase = "SS + RMDs (higher tax)"
        golden_data.append({"Year": yr, "Age": age_in_yr, "Phase": phase})

    df_golden = pd.DataFrame(golden_data)
    golden_chart = alt.Chart(df_golden).mark_bar(size=12).encode(
        x=alt.X('Year:O', title="Year", axis=alt.Axis(labelAngle=-45)),
        color=alt.Color('Phase:N',
            scale=alt.Scale(
                domain=["Golden Window (low tax)", "SS income (moderate tax)", "SS + RMDs (higher tax)"],
                range=["#2ecc71", "#f39c12", "#e74c3c"]
            ),
            legend=alt.Legend(title="Tax Phase")
        ),
        tooltip=[alt.Tooltip('Year:O'), alt.Tooltip('Age:Q'), alt.Tooltip('Phase:N')]
    ).encode(y=alt.value(20))
    st.altair_chart(golden_chart, width='stretch')

    col_gw1, col_gw2, col_gw3 = st.columns(3)
    col_gw1.metric("Golden Window", f"{retire_year}–{golden_end}" if golden_end >= retire_year else "None", f"{max(0, golden_end - retire_year + 1)} years")
    col_gw2.metric("SS Starts", f"{ss_start_year_h}", f"Age {ss_start_year_h - birth_year_h_lab}")
    col_gw3.metric("RMDs Start", f"{rmd_start_year}", f"Age {rmd_start_age}")

    # --- Bracket Impact (reference) ---
    with st.expander(f"📋 Reference: {t['lab_bracket_h']}"):
        base_deduct_lab = 32200 if tax_status == "MFJ" else 16100
        extra_deduct_lab = 0
        if tax_status == "MFJ":
            if h_age_at_retire >= 65: extra_deduct_lab += 1650
            if w_age_at_retire >= 65: extra_deduct_lab += 1650
        else:
            if h_age_at_retire >= 65: extra_deduct_lab += 1950
        total_deduction = base_deduct_lab + extra_deduct_lab

        other_income = taxable_div_in * (1 - qd_perc)
        if tax_status == "MFJ":
            brackets_display = [
                ("0% (standard deduction)", 0, total_deduction),
                ("10%", total_deduction, total_deduction + 23200),
                ("12%", total_deduction + 23200, total_deduction + 94300),
                ("22%", total_deduction + 94300, total_deduction + 201050),
                ("24%", total_deduction + 201050, total_deduction + 383900),
            ]
        else:
            brackets_display = [
                ("0% (standard deduction)", 0, total_deduction),
                ("10%", total_deduction, total_deduction + 11600),
                ("12%", total_deduction + 11600, total_deduction + 47150),
                ("22%", total_deduction + 47150, total_deduction + 100525),
                ("24%", total_deduction + 100525, total_deduction + 191950),
            ]

        optimal_conv = best_amt_for_calc
        gross_with_conv = other_income + optimal_conv
        bracket_rows = []
        for bracket_name, low, high in brackets_display:
            fills = ""
            if gross_with_conv > low:
                amt_in_bracket = min(gross_with_conv, high) - low
                if amt_in_bracket > 0:
                    fills = f"${amt_in_bracket:,.0f}"
            bracket_rows.append({
                "Bracket": bracket_name,
                "Income Range": f"${low:,.0f} – ${high:,.0f}",
                "Filled By": fills if fills else "—",
            })

        st.dataframe(pd.DataFrame(bracket_rows), width='stretch', hide_index=True)
        st.caption(f"Based on retirement year 1 with ${other_income:,.0f} ordinary income + ${optimal_conv:,.0f} optimal Roth conversion. Standard deduction: ${total_deduction:,.0f} ({tax_status}).")

with tab_muni:
    st.subheader(t["muni_h"])
    st.caption(t["muni_desc"])

    # --- Inputs ---
    muni_col1, muni_col2 = st.columns(2)
    with muni_col1:
        muni_yield_pct = st.slider(t["muni_yield_label"], 2.0, 6.0, step=0.25, key="muni_yield_slider")
    with muni_col2:
        taxable_yield_pct = st.slider("Taxable Bond Yield (%)", 3.0, 8.0, step=0.25, key="taxable_yield_slider")

    # Calculate user's marginal bracket from year 1 of simulation
    df_yr1 = calculate_roadmap(**core_args)
    yr1_magi = df_yr1.iloc[0]["OUT: MAGI"]
    yr1_fed_tax = df_yr1.iloc[0]["OUT: Fed Tax"]
    base_deduct_muni = 32200 if tax_status == "MFJ" else 16100
    extra_deduct_muni = 0
    if tax_status == "MFJ":
        if h_age_at_retire >= 65: extra_deduct_muni += 1650
        if w_age_at_retire >= 65: extra_deduct_muni += 1650
    else:
        if h_age_at_retire >= 65: extra_deduct_muni += 1950
    total_deduct_muni = base_deduct_muni + extra_deduct_muni
    yr1_ord_taxable = max(0, yr1_magi - muni_int_in - total_deduct_muni)

    if tax_status == "MFJ":
        muni_brackets = [(23200, 0.10), (94300, 0.12), (201050, 0.22), (383900, 0.24), (999999999, 0.32)]
    else:
        muni_brackets = [(11600, 0.10), (47150, 0.12), (100525, 0.22), (191950, 0.24), (999999999, 0.32)]

    marginal_rate = 0.10
    for limit, rate in muni_brackets:
        if yr1_ord_taxable <= limit:
            marginal_rate = rate
            break

    tey = muni_yield_pct / (1 - marginal_rate)

    # --- Insight + Apply ---
    st.divider()
    st.markdown(f"**{t['muni_bracket_label']}:** {marginal_rate*100:.0f}% (based on Year 1 taxable income of {yr1_ord_taxable:,.0f})")
    st.markdown(f"**{t['muni_tey_result']}:** {tey:.2f}% — a taxable bond must yield at least this to beat a {muni_yield_pct:.1f}% muni at your bracket.")

    if tey > taxable_yield_pct:
        st.success(f"At your {marginal_rate*100:.0f}% bracket, munis ({muni_yield_pct:.1f}%) beat taxable bonds ({taxable_yield_pct:.1f}%) after tax. TEY advantage: +{tey - taxable_yield_pct:.2f}%.")
    else:
        st.info(f"Taxable bonds ({taxable_yield_pct:.1f}%) currently yield more than the muni TEY ({tey:.2f}%). Munis may still help if reducing MAGI avoids IRMAA.")

    # --- Allocation comparison simulation ---
    st.divider()
    st.subheader(t["muni_alloc_h"])
    st.caption(t["muni_alloc_desc"])

    total_fixed_income = taxable_div_in + muni_int_in
    alloc_scenarios = [0, 25, 50, 75, 100]
    muni_results = []

    for pct in alloc_scenarios:
        test_muni = int(total_fixed_income * pct / 100)
        test_taxable = total_fixed_income - test_muni
        df_muni_sim = calculate_roadmap(
            **{**core_args, "muni_int_in": test_muni, "taxable_div_in": test_taxable}
        )
        final_nw = df_muni_sim.iloc[-1]["Expected Net Worth"]
        total_tax = df_muni_sim["OUT: Fed Tax"].sum()
        yr1_magi_sim = df_muni_sim.iloc[0]["OUT: MAGI"]
        muni_results.append({
            t["muni_col_alloc"]: f"{pct}%",
            t["muni_col_muni_income"]: test_muni,
            t["muni_col_taxable_income"]: test_taxable,
            t["muni_col_final_nw"]: final_nw,
            t["muni_col_total_tax"]: total_tax,
            t["muni_col_magi_yr1"]: yr1_magi_sim,
        })

    df_muni_results = pd.DataFrame(muni_results)

    best_muni_row = df_muni_results.loc[df_muni_results[t["muni_col_final_nw"]].idxmax()]
    best_muni_pct = best_muni_row[t["muni_col_alloc"]]
    best_muni_nw = best_muni_row[t["muni_col_final_nw"]]
    worst_muni_nw = df_muni_results[t["muni_col_final_nw"]].min()

    tey_favors_taxable = tey <= taxable_yield_pct
    best_pct_val = int(best_muni_pct.replace("%", ""))
    if tey_favors_taxable and best_pct_val > 0:
        st.markdown(f"**{t['muni_insight']}:** Although taxable bonds win on pure yield, the full simulation (including IRMAA savings and tax interactions over time) favors **{best_muni_pct}** muni allocation of fixed income ({total_fixed_income:,.0f}), yielding {best_muni_nw:,.0f} final expected net worth — {best_muni_nw - worst_muni_nw:,.0f} more than the worst allocation.")
    else:
        st.markdown(f"**{t['muni_insight']}:** Optimal muni allocation is **{best_muni_pct}** of fixed income ({total_fixed_income:,.0f}), yielding {best_muni_nw:,.0f} final expected net worth — {best_muni_nw - worst_muni_nw:,.0f} more than the worst allocation.")

    current_pct = int(round(muni_int_in / max(1, total_fixed_income) * 100))
    if str(current_pct) + "%" != best_muni_pct:
        best_pct_int = int(best_muni_pct.replace("%", ""))
        best_muni_dollar = int(total_fixed_income * best_pct_int / 100)
        best_taxable_dollar = total_fixed_income - best_muni_dollar
        if st.button(f"Apply: Set muni to {best_muni_dollar:,.0f} and taxable to {best_taxable_dollar:,.0f}", key="apply_muni"):
            st.session_state["_apply_all_pending"] = True
            st.session_state["_apply_all_values"] = {
                "muni_int_in": best_muni_dollar,
                "taxable_div_in": best_taxable_dollar,
            }
            st.rerun()

    # --- Chart ---
    st.divider()
    muni_chart_data = []
    for pct in alloc_scenarios:
        test_muni = int(total_fixed_income * pct / 100)
        test_taxable = total_fixed_income - test_muni
        df_muni_chart = calculate_roadmap(
            **{**core_args, "muni_int_in": test_muni, "taxable_div_in": test_taxable}
        )
        for _, row in df_muni_chart.iterrows():
            muni_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Muni Allocation": f"{pct}%"})

    df_muni_chart_all = pd.DataFrame(muni_chart_data)
    muni_alloc_order = [f"{p}%" for p in alloc_scenarios]

    muni_lines = alt.Chart(df_muni_chart_all).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
        y=alt.Y('Expected Net Worth:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
        color=alt.Color('Muni Allocation:N', sort=muni_alloc_order, legend=alt.Legend(title="Muni %")),
    )
    nearest_muni = alt.selection_point(nearest=True, on="pointerover", fields=["Year"], empty=False)
    selectors_muni = alt.Chart(df_muni_chart_all).mark_point(size=80, filled=True).encode(x='Year:Q', opacity=alt.value(0)).add_params(nearest_muni)
    points_muni = muni_lines.mark_point(size=60, filled=True).encode(
        opacity=alt.condition(nearest_muni, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip('Year:Q', format='d'), alt.Tooltip('Expected Net Worth:Q', format='$,.0f'), alt.Tooltip('Muni Allocation:N')]
    )
    vrule_muni = alt.Chart(df_muni_chart_all).mark_rule(color='gray', strokeDash=[3, 3]).encode(
        x='Year:Q', opacity=alt.condition(nearest_muni, alt.value(0.6), alt.value(0))
    )
    st.altair_chart(alt.layer(muni_lines, selectors_muni, points_muni, vrule_muni), width='stretch')

    # --- IRMAA impact note ---
    st.divider()
    st.subheader(t["muni_irmaa_h"])
    st.caption(t["muni_irmaa_desc"])
    irmaa_threshold = 218000 if tax_status == "MFJ" else 174000
    st.markdown(f"Your Year 1 MAGI: **{yr1_magi:,.0f}** | IRMAA threshold: **{irmaa_threshold:,.0f}**")
    if yr1_magi > irmaa_threshold:
        st.warning(f"Your MAGI exceeds the IRMAA threshold by {yr1_magi - irmaa_threshold:,.0f}. Note: muni interest is included in MAGI, so increasing munis will not reduce your IRMAA tier.")
    else:
        headroom = irmaa_threshold - yr1_magi
        st.success(f"You have {headroom:,.0f} of MAGI headroom before IRMAA triggers. Muni income keeps AGI lower, potentially allowing larger Roth conversions within this headroom.")

    # --- Reference table ---
    st.divider()
    st.subheader(t["muni_ref_h"])
    ref_brackets = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    ref_yields = [3.0, 3.5, 4.0, 4.5, 5.0]
    tey_rows = []
    for bracket in ref_brackets:
        row_data = {"Marginal Rate": f"{bracket*100:.0f}%"}
        for yld in ref_yields:
            row_data[f"{yld:.1f}% Muni"] = f"{yld / (1 - bracket):.2f}%"
        tey_rows.append(row_data)
    st.dataframe(pd.DataFrame(tey_rows), width='stretch', hide_index=True)

    # --- Comparison table ---
    st.dataframe(
        df_muni_results.style.format({
            t["muni_col_muni_income"]: "${:,.0f}",
            t["muni_col_taxable_income"]: "${:,.0f}",
            t["muni_col_final_nw"]: "${:,.0f}",
            t["muni_col_total_tax"]: "${:,.0f}",
            t["muni_col_magi_yr1"]: "${:,.0f}",
        }),
        width='stretch', hide_index=True
    )

with tab_cg:
    st.subheader(t["cg_h"])
    st.caption(t["cg_desc"])

    # --- Calculate 0% bracket capacity ---
    if tax_status == "MFJ":
        cg_zero_limit = 94050
    else:
        cg_zero_limit = 47025

    base_deduct_cg = 32200 if tax_status == "MFJ" else 16100
    extra_deduct_cg = 0
    if tax_status == "MFJ":
        if h_age_at_retire >= 65: extra_deduct_cg += 1650
        if w_age_at_retire >= 65: extra_deduct_cg += 1650
    else:
        if h_age_at_retire >= 65: extra_deduct_cg += 1950
    total_deduct_cg = base_deduct_cg + extra_deduct_cg

    # Year 1 ordinary income (excluding cap gains) to find 0% capacity
    df_cg_base = calculate_roadmap(**{**core_args, "annual_ltcg": 0})
    yr1_ordinary_cg = max(0, df_cg_base.iloc[0]["OUT: MAGI"] - muni_int_in - total_deduct_cg)
    zero_bracket_capacity = max(0, cg_zero_limit - yr1_ordinary_cg)

    # --- Harvest comparison simulation (run first to find optimal) ---
    # Cap harvest at ~10% of brokerage per year (can't harvest gains you don't have)
    max_annual_harvest = int(brokerage_init * 0.10)
    baseline_total_tax = df_cg_base["OUT: Fed Tax"].sum()
    harvest_step = max(10000, round(max_annual_harvest / 8, -4))
    harvest_amounts = sorted(set([0] + list(range(0, max_annual_harvest + 1, int(harvest_step))) + [max_annual_harvest]))
    cg_results = []

    for amt in harvest_amounts:
        df_cg_sim = calculate_roadmap(**{**core_args, "annual_ltcg": amt})
        final_nw = df_cg_sim.iloc[-1]["Expected Net Worth"]
        total_tax = df_cg_sim["OUT: Fed Tax"].sum()
        extra_tax = total_tax - baseline_total_tax

        cg_results.append({
            t["cg_col_amount"]: amt,
            t["cg_col_in_zero"]: min(amt, zero_bracket_capacity),
            t["cg_col_in_fifteen"]: max(0, amt - zero_bracket_capacity),
            t["cg_col_tax_on_cg"]: extra_tax,
            t["cg_col_final_nw"]: final_nw,
            t["cg_col_total_tax"]: total_tax,
        })

    df_cg_results = pd.DataFrame(cg_results)
    best_cg_row = df_cg_results.loc[df_cg_results[t["cg_col_final_nw"]].idxmax()]
    best_cg_amt = int(best_cg_row[t["cg_col_amount"]])
    best_cg_nw = best_cg_row[t["cg_col_final_nw"]]
    baseline_cg_nw = df_cg_results.iloc[0][t["cg_col_final_nw"]]
    best_cg_extra_tax = best_cg_row[t["cg_col_tax_on_cg"]]

    # --- Insight + Apply (top) ---
    st.divider()
    st.markdown(f"**{t['cg_zero_h']}:** {zero_bracket_capacity:,.0f}/year — gains up to this amount are taxed at 0% (your ordinary income fills {yr1_ordinary_cg:,.0f} of the {cg_zero_limit:,.0f} limit).")

    if best_cg_extra_tax <= 0:
        st.success(f"**{t['cg_insight']}:** Optimal harvest is **{best_cg_amt:,.0f}/year** — entirely within the 0% bracket. Net worth gain: +{best_cg_nw - baseline_cg_nw:,.0f} vs. harvesting nothing, with no additional tax.")
    else:
        st.success(f"**{t['cg_insight']}:** Optimal harvest is **{best_cg_amt:,.0f}/year**, yielding +{best_cg_nw - baseline_cg_nw:,.0f} net worth vs. doing nothing. Additional {sim_years}-year tax cost: {best_cg_extra_tax:,.0f}.")

    if annual_ltcg != best_cg_amt:
        if st.button(f"Apply: Set annual capital gains to {best_cg_amt:,.0f}", key="apply_cg_optimal"):
            st.session_state["_apply_all_pending"] = True
            st.session_state["_apply_all_values"] = {"annual_ltcg": best_cg_amt}
            st.rerun()

    # --- Chart ---
    st.divider()
    st.subheader(t["cg_harvest_h"])
    st.caption(t["cg_harvest_desc"])

    cg_chart_data = []
    chart_harvest_amounts = sorted(set([0, int(max_annual_harvest * 0.25), int(max_annual_harvest * 0.5), int(max_annual_harvest * 0.75), max_annual_harvest]))
    for amt in chart_harvest_amounts:
        df_cg_chart = calculate_roadmap(**{**core_args, "annual_ltcg": amt})
        for _, row in df_cg_chart.iterrows():
            cg_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Annual Harvest": f"${amt:,.0f}"})

    df_cg_chart_all = pd.DataFrame(cg_chart_data)
    harvest_order = [f"${a:,.0f}" for a in chart_harvest_amounts]

    cg_lines = alt.Chart(df_cg_chart_all).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
        y=alt.Y('Expected Net Worth:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
        color=alt.Color('Annual Harvest:N', sort=harvest_order, legend=alt.Legend(title="Annual Harvest")),
    )
    nearest_cg = alt.selection_point(nearest=True, on="pointerover", fields=["Year"], empty=False)
    selectors_cg = alt.Chart(df_cg_chart_all).mark_point(size=80, filled=True).encode(x='Year:Q', opacity=alt.value(0)).add_params(nearest_cg)
    points_cg = cg_lines.mark_point(size=60, filled=True).encode(
        opacity=alt.condition(nearest_cg, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip('Year:Q', format='d'), alt.Tooltip('Expected Net Worth:Q', format='$,.0f'), alt.Tooltip('Annual Harvest:N')]
    )
    vrule_cg = alt.Chart(df_cg_chart_all).mark_rule(color='gray', strokeDash=[3, 3]).encode(
        x='Year:Q', opacity=alt.condition(nearest_cg, alt.value(0.6), alt.value(0))
    )
    st.altair_chart(alt.layer(cg_lines, selectors_cg, points_cg, vrule_cg), width='stretch')

    # --- Comparison table ---
    st.divider()
    st.dataframe(
        df_cg_results.style.format({
            t["cg_col_amount"]: "${:,.0f}",
            t["cg_col_in_zero"]: "${:,.0f}",
            t["cg_col_in_fifteen"]: "${:,.0f}",
            t["cg_col_tax_on_cg"]: "${:,.0f}",
            t["cg_col_final_nw"]: "${:,.0f}",
            t["cg_col_total_tax"]: "${:,.0f}",
        }),
        width='stretch', hide_index=True
    )

    # --- Reference table ---
    st.divider()
    st.subheader(t["cg_ref_h"])
    cg_ref_data = [
        {"Rate": "0%", "Single": "$0 – $47,025", "MFJ": "$0 – $94,050"},
        {"Rate": "15%", "Single": "$47,026 – $291,850", "MFJ": "$94,051 – $583,750"},
        {"Rate": "20%", "Single": "Over $291,850", "MFJ": "Over $583,750"},
        {"Rate": "3.8% NIIT", "Single": "MAGI > $200,000", "MFJ": "MAGI > $250,000"},
    ]
    st.dataframe(pd.DataFrame(cg_ref_data), width='stretch', hide_index=True)

with tab_whatif:
    st.subheader(t["whatif_h"])
    st.caption(t["whatif_desc"])

    # --- Run simulations upfront to get insights ---
    ws_chart_keys = ["tax_efficient", "ira_first", "roth_first", "proportional"]
    ws_chart_display = [t["ws_tax_efficient"], t["ws_ira_first"], t["ws_roth_first"], t["ws_proportional"]]
    ws_chart_data = []
    ws_final_nw = {}
    ws_key_by_name = {}
    for ws_key, ws_name in zip(ws_chart_keys, ws_chart_display):
        df_ws = calculate_roadmap(**{**core_args, "withdrawal_strategy": ws_key})
        ws_final_nw[ws_name] = df_ws.iloc[-1]["Expected Net Worth"]
        ws_key_by_name[ws_name] = ws_key
        for _, row in df_ws.iterrows():
            ws_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Strategy": ws_name})
    df_ws_chart = pd.DataFrame(ws_chart_data)

    best_ws_name = max(ws_final_nw, key=ws_final_nw.get)
    worst_ws_name = min(ws_final_nw, key=ws_final_nw.get)
    ws_spread = ws_final_nw[best_ws_name] - ws_final_nw[worst_ws_name]
    best_ws_key = ws_key_by_name[best_ws_name]

    mc_gp_map = {"ultra_conservative": t["gp_ultra_conservative"], "conservative": t["gp_conservative"], "moderate": t["gp_moderate"], "aggressive": t["gp_aggressive"]}
    mc_gp_keys = list(mc_gp_map.keys())
    mc_gp_labels = list(mc_gp_map.values())
    mc_core = {k: v for k, v in core_args.items() if k != "withdrawal_strategy"}
    mc_core["withdrawal_strategy"] = "tax_efficient"
    mc_final_medians = {}
    mc_chart_data = []
    for gp_key, gp_name in zip(mc_gp_keys, mc_gp_labels):
        years, p10, p50, p90 = run_monte_carlo(mc_core, gp_key, ira_growth_raw, roth_growth_raw, broker_growth_raw)
        mc_final_medians[gp_name] = p50[-1]
        for j, yr in enumerate(years):
            mc_chart_data.append({"Year": yr, "Median": p50[j], "P10": p10[j], "P90": p90[j], "Profile": gp_name})

    best_gp_name = max(mc_final_medians, key=mc_final_medians.get)
    worst_gp_name = min(mc_final_medians, key=mc_final_medians.get)
    gp_spread = mc_final_medians[best_gp_name] - mc_final_medians[worst_gp_name]
    best_gp_key = mc_gp_keys[mc_gp_labels.index(best_gp_name)]

    # --- Withdrawal strategy section ---
    st.divider()
    st.subheader(t["withdrawal_chart_h"])
    st.caption(t["withdrawal_chart_desc"].format(sim_years=sim_years))

    with st.expander("What does each withdrawal strategy do?", expanded=False):
        st.markdown("""
- **Tax-Efficient (Brokerage → IRA → Roth):** Spends taxable accounts first, preserving tax-advantaged growth longest. Generally optimal for most retirees.
- **IRA-First (IRA → Brokerage → Roth):** Drains the IRA early to reduce future RMDs. Can help if your IRA is very large relative to other accounts.
- **Roth-First (Roth → Brokerage → IRA):** Spends tax-free money first. Rarely optimal — wastes Roth's compounding advantage — but useful if you need liquidity without triggering IRMAA.
- **Proportional:** Draws equally from all accounts by balance ratio. A middle-ground approach that avoids concentration risk.
""")

    current_ws_name = ws_chart_display[ws_chart_keys.index(withdrawal_strategy)]
    if withdrawal_strategy == best_ws_key:
        st.success(f"**Best withdrawal strategy:** {best_ws_name} (already applied) — {ws_spread:,.0f} more in final net worth than {worst_ws_name}.")
    else:
        st.info(f"**Best withdrawal strategy:** {best_ws_name} — {ws_spread:,.0f} more in final net worth than {worst_ws_name}. Current: {current_ws_name}.")
        if st.button(f"Apply: Set withdrawal strategy to {best_ws_name}", key="apply_ws"):
            st.session_state["withdrawal_strategy"] = best_ws_key
            st.rerun()

    ws_lines = alt.Chart(df_ws_chart).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
        y=alt.Y('Expected Net Worth:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
        color=alt.Color('Strategy:N', sort=ws_chart_display, legend=alt.Legend(title="Withdrawal Strategy")),
    )
    nearest_ws = alt.selection_point(nearest=True, on="pointerover", fields=["Year"], empty=False)
    selectors_ws = alt.Chart(df_ws_chart).mark_point(size=80, filled=True).encode(x='Year:Q', opacity=alt.value(0)).add_params(nearest_ws)
    points_ws = ws_lines.mark_point(size=60, filled=True).encode(
        opacity=alt.condition(nearest_ws, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip('Year:Q', format='d'), alt.Tooltip('Expected Net Worth:Q', format='$,.0f'), alt.Tooltip('Strategy:N')]
    )
    vrule_ws = alt.Chart(df_ws_chart).mark_rule(color='gray', strokeDash=[3, 3]).encode(
        x='Year:Q', opacity=alt.condition(nearest_ws, alt.value(0.6), alt.value(0))
    )
    st.altair_chart(alt.layer(ws_lines, selectors_ws, points_ws, vrule_ws), width='stretch')

    # --- Growth profile Monte Carlo ---
    st.divider()
    st.subheader(t["growth_chart_h"])
    st.caption(t["growth_chart_desc"].format(sim_years=sim_years))

    with st.expander("What does each growth profile represent?", expanded=False):
        st.markdown(f"""
- **Ultra-Conservative (-4%):** Bond-heavy portfolio or prolonged bear market. Rates: IRA {max(0.5, ira_growth_raw-4):.1f}% | Roth {max(0.5, roth_growth_raw-4):.1f}% | Brokerage {max(0.5, broker_growth_raw-4):.1f}%. Volatility: 3%.
- **Conservative (-2%):** Below-average returns, mild recession. Rates: IRA {max(0.5, ira_growth_raw-2):.1f}% | Roth {max(0.5, roth_growth_raw-2):.1f}% | Brokerage {max(0.5, broker_growth_raw-2):.1f}%. Volatility: 6%.
- **Moderate (your settings):** Your current growth assumptions as the baseline. Rates: IRA {ira_growth_raw:.1f}% | Roth {roth_growth_raw:.1f}% | Brokerage {broker_growth_raw:.1f}%. Volatility: 10%.
- **Aggressive (+2%):** Bull market or equity-heavy allocation. Rates: IRA {ira_growth_raw+2:.1f}% | Roth {roth_growth_raw+2:.1f}% | Brokerage {broker_growth_raw+2:.1f}%. Volatility: 14%.

**Reading the chart:** Solid line = **median** (50th percentile, most likely outcome). Shaded band = **10th–90th percentile** (80% of simulated paths fall here). Narrow band = predictable; wide band = high uncertainty.
""")

    # Show both upside and downside perspective
    df_mc_all = pd.DataFrame(mc_chart_data)
    aggressive_p10 = df_mc_all[df_mc_all["Profile"] == mc_gp_labels[3]].iloc[-1]["P10"]
    aggressive_p90 = df_mc_all[df_mc_all["Profile"] == mc_gp_labels[3]].iloc[-1]["P90"]
    moderate_median = mc_final_medians[mc_gp_labels[2]]
    conservative_p10 = df_mc_all[df_mc_all["Profile"] == mc_gp_labels[1]].iloc[-1]["P10"]

    st.info(f"**Upside vs. downside:** {best_gp_name} median is {gp_spread:,.0f} higher than {worst_gp_name}, but its 10th percentile ({aggressive_p10:,.0f}) could underperform {mc_gp_labels[2]} median ({moderate_median:,.0f}). Higher growth comes with wider uncertainty bands.")

    current_gp_name = mc_gp_labels[mc_gp_keys.index(growth_profile)]
    gp_col1, gp_col2, gp_col3, gp_col4 = st.columns(4)
    for col, gp_key, gp_name in zip([gp_col1, gp_col2, gp_col3, gp_col4], mc_gp_keys, mc_gp_labels):
        with col:
            if gp_key == growth_profile:
                st.button(f"{gp_name} (current)", key=f"apply_gp_{gp_key}", disabled=True)
            else:
                if st.button(f"Apply: {gp_name}", key=f"apply_gp_{gp_key}"):
                    st.session_state["growth_profile"] = gp_key
                    st.rerun()

    # Profile selector to reduce overlap
    st.divider()
    mc_selected = st.multiselect("Select scenarios to compare", mc_gp_labels, default=mc_gp_labels, key="mc_profile_select")

    if mc_selected:
        df_mc = df_mc_all[df_mc_all["Profile"].isin(mc_selected)]
        mc_profiles_shown = [lbl for lbl in mc_gp_labels if lbl in mc_selected]
        color_range = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        shown_colors = [color_range[mc_gp_labels.index(lbl)] for lbl in mc_profiles_shown]
        color_scale = alt.Scale(domain=mc_profiles_shown, range=shown_colors)

        base_lines = alt.Chart(df_mc).mark_line(strokeWidth=2.5).encode(
            x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
            y=alt.Y('Median:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
            color=alt.Color('Profile:N', scale=color_scale, sort=mc_profiles_shown, legend=alt.Legend(title="Growth Profile")),
            tooltip=[alt.Tooltip('Year:Q', format='d'), alt.Tooltip('Median:Q', title="Median", format='$,.0f'), alt.Tooltip('P10:Q', title="10th Pctl", format='$,.0f'), alt.Tooltip('P90:Q', title="90th Pctl", format='$,.0f'), alt.Tooltip('Profile:N')]
        )
        bands = alt.Chart(df_mc).mark_area(opacity=0.15).encode(
            x=alt.X('Year:Q', axis=alt.Axis(format='d')),
            y=alt.Y('P10:Q', title=""),
            y2='P90:Q',
            fill=alt.Fill('Profile:N', scale=color_scale, sort=mc_profiles_shown, legend=None)
        )
        st.altair_chart(alt.layer(base_lines, bands), width='stretch')
    else:
        st.warning("Select at least one profile to display.")

with tab_roadmap:
    st.subheader(t["roadmap_tab_h"])
    st.caption(t["roadmap_tab_desc"])

    # --- 1. CALCULATE THREE SCENARIOS ---
    best_pct_int_road = int(best_muni_pct.replace("%", ""))
    best_muni_dollar_road = int(total_fixed_income * best_pct_int_road / 100)
    best_taxable_dollar_road = total_fixed_income - best_muni_dollar_road

    # Re-compute optimal Roth given all other optimal settings
    joint_base_args = {
        **core_args,
        "ss_h_monthly": int(best_h_monthly), "ss_h_start": best_h_start_yr,
        "ss_w_monthly": int(best_w_monthly), "ss_w_start": best_w_start_yr,
        "muni_int_in": best_muni_dollar_road, "taxable_div_in": best_taxable_dollar_road,
        "annual_ltcg": best_cg_amt,
        "withdrawal_strategy": best_ws_key,
    }
    best_roth_joint = get_optimal_conversion(joint_base_args, lab_horizon, legacy_weight_val, max_irmaa_limit_val)

    df_baseline = calculate_roadmap(**core_args, conv_override=0, ltcg_override=0)
    df_active = calculate_roadmap(**core_args)
    optimal_args = {**joint_base_args, "roth_conv": best_roth_joint}
    df_optimal = calculate_roadmap(**optimal_args)

    # --- 2. EXTRACT METRICS ---
    mid_idx = int(sim_years * 0.33)
    end_idx = int(sim_years * 0.95)
    mid_w = 1.0 - legacy_weight_val
    end_w = legacy_weight_val

    def _weighted_score(df):
        return df.iloc[mid_idx]['Expected Net Worth'] * mid_w + df.iloc[end_idx]['Expected Net Worth'] * end_w

    nw_base, nw_strat, nw_opt = _weighted_score(df_baseline), _weighted_score(df_active), _weighted_score(df_optimal)
    tax_base, tax_strat, tax_opt = df_baseline['OUT: Fed Tax'].sum(), df_active['OUT: Fed Tax'].sum(), df_optimal['OUT: Fed Tax'].sum()
    roth_base, roth_strat, roth_opt = df_baseline.iloc[-1]['Roth Bal'], df_active.iloc[-1]['Roth Bal'], df_optimal.iloc[-1]['Roth Bal']
    init_nw = ira_h_init + ira_w_init + roth_init + brokerage_init
    total_outflow = df_active['raw_outflow'].sum()
    total_rmd = df_active['INPUT: RMDs'].sum()
    total_tax_paid = df_active['OUT: Fed Tax'].sum()
    final_nw_active = df_active.iloc[-1]['Expected Net Worth']

    # --- Key Insight (top) ---
    st.divider()
    nw_gain_vs_idle = nw_strat - nw_base
    if nw_gain_vs_idle > 0:
        st.success(f"**Your active strategy adds {nw_gain_vs_idle:,.0f} in expected net worth** vs. doing nothing over {sim_years} years. Final expected NW: {final_nw_active:,.0f}. Total tax: {total_tax_paid:,.0f}.")
    elif nw_gain_vs_idle < 0:
        st.warning(f"**Your current settings underperform idle** by {-nw_gain_vs_idle:,.0f}. Consider adjusting Roth conversion or capital gains harvesting in earlier tabs.")
    elif nw_gain_vs_idle == 0:
        st.warning(f"**Your current settings is the same as idle**. Consider adjusting Roth conversion or capital gains harvesting in earlier tabs.")

    # --- OPTIMIZATION SUMMARY: surface each tab's recommendation ---
    st.divider()
    st.subheader("⚡ Recommended Settings from Each Tab")

    opt_rows = []
    any_unapplied = False

    # Roth conversion (jointly optimized with other settings)
    roth_applied = (st.session_state.roth_conv == best_roth_joint)
    opt_rows.append({"Decision": "Roth Conversion", "Optimal": f"${best_roth_joint:,.0f}/yr", "Current": f"${st.session_state.roth_conv:,.0f}/yr", "Applied": "✅" if roth_applied else "❌"})
    if not roth_applied:
        any_unapplied = True

    # Social Security
    ss_applied = (abs(best_h_monthly - ss_h_monthly) < 1 and abs(best_w_monthly - ss_w_monthly) < 1
                  and best_h_start_yr == ss_h_start and best_w_start_yr == ss_w_start)
    opt_rows.append({"Decision": "Social Security", "Optimal": f"H:{best_h_claim} W:{best_w_claim}", "Current": f"H:{ss_h_start - birth_year_h} W:{ss_w_start - birth_year_w}", "Applied": "✅" if ss_applied else "❌"})
    if not ss_applied:
        any_unapplied = True

    # Muni allocation
    muni_applied = (muni_int_in == best_muni_dollar_road)
    opt_rows.append({"Decision": "Muni Allocation", "Optimal": f"{best_muni_pct} (${best_muni_dollar_road:,.0f})", "Current": f"{int(round(muni_int_in / max(1, total_fixed_income) * 100))}% (${muni_int_in:,.0f})", "Applied": "✅" if muni_applied else "❌"})
    if not muni_applied:
        any_unapplied = True

    # Capital gains harvesting
    cg_applied = (annual_ltcg == best_cg_amt)
    opt_rows.append({"Decision": "Capital Gains Harvest", "Optimal": f"${best_cg_amt:,.0f}/yr", "Current": f"${annual_ltcg:,.0f}/yr", "Applied": "✅" if cg_applied else "❌"})
    if not cg_applied:
        any_unapplied = True

    # Withdrawal strategy
    ws_applied = (withdrawal_strategy == best_ws_key)
    opt_rows.append({"Decision": "Withdrawal Strategy", "Optimal": best_ws_name, "Current": current_ws_name, "Applied": "✅" if ws_applied else "❌"})
    if not ws_applied:
        any_unapplied = True

    st.dataframe(pd.DataFrame(opt_rows), width='stretch', hide_index=True)

    if any_unapplied:
        if st.button("🚀 Apply All Optimal Settings", key="apply_all_optimal"):
            st.session_state["_apply_all_pending"] = True
            st.session_state["_apply_all_values"] = {
                "roth_conv": int(best_roth_joint),
                "ss_h_monthly": int(best_h_monthly),
                "ss_h_start": best_h_start_yr,
                "ss_w_monthly": int(best_w_monthly),
                "ss_w_start": best_w_start_yr,
                "muni_int_in": best_muni_dollar_road,
                "taxable_div_in": best_taxable_dollar_road,
                "annual_ltcg": best_cg_amt,
                "withdrawal_strategy": best_ws_key,
            }
            st.rerun()
    else:
        st.success("All settings are already at their optimal values.")

    # --- 3. KPI DASHBOARD ---
    st.divider()
    st.subheader(t["kpi_h"].format(sim_years=sim_years))
    st.caption(t["comp_desc"].format(sim_years=sim_years))

    def _kpi_card(label, value, color, comparison=None):
        comp_html = ""
        if comparison:
            comp_html = f'<span style="font-size: 0.75rem; color: #888888;">{comparison}</span>'
        return f"""
        <div style="background-color: rgba({color}, 0.08); border: 1px solid rgba({color}, 0.3); padding: 12px 8px; border-radius: 8px; text-align: center; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <h4 style="margin: 0; color: #888888; font-size: 0.8rem; font-weight: normal;">{label}</h4>
            <p style="margin: 4px 0 2px 0; font-size: 1.4rem; font-weight: bold; color: rgba({color}, 1);">{value}</p>
            {comp_html}
        </div>
        """

    ira_pct = (ira_h_init + ira_w_init) / max(1, init_nw) * 100
    roth_pct = roth_init / max(1, init_nw) * 100
    broker_pct = brokerage_init / max(1, init_nw) * 100
    total_living = df_active['raw_outflow'].sum() - total_tax_paid
    rmd_pct_of_ira = total_rmd / max(1, ira_h_init + ira_w_init) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(_kpi_card(t["kpi_init_nw"], f"${init_nw:,.0f}", "155, 89, 182",
            f"IRA {ira_pct:.0f}% | Roth {roth_pct:.0f}% | Taxable {broker_pct:.0f}%"), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card(t["kpi_nw"], f"${nw_strat:,.0f}", "46, 204, 113",
            f"Idle: ${nw_base:,.0f} | Opt: ${nw_opt:,.0f}"), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_card(t["kpi_total_outflow"].format(sim_years=sim_years), f"${total_outflow:,.0f}", "149, 165, 166",
            f"Living: ${total_living:,.0f} | Tax: ${total_tax_paid:,.0f}"), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_card(t["kpi_tax"], f"${tax_strat:,.0f}", "243, 156, 18",
            f"Idle: ${tax_base:,.0f} | Opt: ${tax_opt:,.0f}"), unsafe_allow_html=True)
    with c5:
        st.markdown(_kpi_card(t["kpi_rmd"], f"${total_rmd:,.0f}", "230, 126, 34",
            f"{rmd_pct_of_ira:.0f}% of initial IRA balance"), unsafe_allow_html=True)
    with c6:
        st.markdown(_kpi_card(t["kpi_roth"], f"${roth_strat:,.0f}", "52, 152, 219",
            f"Idle: ${roth_base:,.0f} | Opt: ${roth_opt:,.0f}"), unsafe_allow_html=True)

    # --- Net Worth Trajectory Chart (Strategy vs Idle vs Optimal) ---
    st.divider()
    plan_chart_data = []
    for _, row in df_active.iterrows():
        plan_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Scenario": t["kpi_strategy"]})
    for _, row in df_baseline.iterrows():
        plan_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Scenario": t["kpi_baseline"]})
    for _, row in df_optimal.iterrows():
        plan_chart_data.append({"Year": row["Year"], "Expected Net Worth": row["Expected Net Worth"], "Scenario": t["kpi_optimum"]})
    df_plan_chart = pd.DataFrame(plan_chart_data)
    plan_order = [t["kpi_strategy"], t["kpi_optimum"], t["kpi_baseline"]]

    plan_lines = alt.Chart(df_plan_chart).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Year:Q', title="Year", axis=alt.Axis(format='d')),
        y=alt.Y('Expected Net Worth:Q', title="Expected Net Worth ($)", scale=alt.Scale(zero=False)),
        color=alt.Color('Scenario:N', sort=plan_order, legend=alt.Legend(title="Scenario")),
        strokeDash=alt.StrokeDash('Scenario:N', sort=plan_order, legend=None),
    )
    nearest_plan = alt.selection_point(nearest=True, on="pointerover", fields=["Year"], empty=False)
    selectors_plan = alt.Chart(df_plan_chart).mark_point(size=80, filled=True).encode(x='Year:Q', opacity=alt.value(0)).add_params(nearest_plan)
    points_plan = plan_lines.mark_point(size=60, filled=True).encode(
        opacity=alt.condition(nearest_plan, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip('Year:Q', format='d'), alt.Tooltip('Expected Net Worth:Q', format='$,.0f'), alt.Tooltip('Scenario:N')]
    )
    vrule_plan = alt.Chart(df_plan_chart).mark_rule(color='gray', strokeDash=[3, 3]).encode(
        x='Year:Q', opacity=alt.condition(nearest_plan, alt.value(0.6), alt.value(0))
    )
    st.altair_chart(alt.layer(plan_lines, selectors_plan, points_plan, vrule_plan), width='stretch')

    # --- SUMMARY TABLE ---
    st.divider()
    st.subheader(t["summary_h"].format(sim_years=sim_years))
    total_tax = df_active["OUT: Fed Tax"].sum()
    total_taxable_yield = df_active["raw_div"].sum() + df_active["raw_cg"].sum() + df_active["raw_rmd"].sum()
    tax_per_dollar = total_tax / max(1, total_taxable_yield)

    summary_rows = [
        {"Type": t["acc_ira"], "Init": ira_h_init + ira_w_init, "Final": df_active.iloc[-1]['IRA Bal'], "Yield": df_active["raw_rmd"].sum(), "Liability": df_active["raw_rmd"].sum() * tax_per_dollar},
        {"Type": t["acc_roth"], "Init": roth_init, "Final": df_active.iloc[-1]['Roth Bal'], "Yield": df_active["raw_roth_yield"].sum(), "Liability": 0.0},
        {"Type": t["acc_broker"], "Init": brokerage_init, "Final": df_active.iloc[-1]['Brokerage'], "Yield": df_active["raw_div"].sum() + df_active["raw_cg"].sum() + df_active["raw_muni"].sum(), "Liability": (df_active["raw_div"].sum() + df_active["raw_cg"].sum()) * tax_per_dollar}
    ]
    df_sum_table = pd.DataFrame(summary_rows)
    totals_row = {"Type": t["total_label"], "Init": df_sum_table["Init"].sum(), "Final": df_sum_table["Final"].sum(), "Yield": df_sum_table["Yield"].sum(), "Liability": df_sum_table["Liability"].sum()}
    df_final_sum_display = pd.concat([df_sum_table, pd.DataFrame([totals_row])], ignore_index=True)

    yield_col = t["sum_yield"].format(sim_years=sim_years)
    tax_col = t["sum_liability"].format(sim_years=sim_years)

    df_final_sum_renamed = df_final_sum_display.rename(columns={"Type": "Account", "Init": t["sum_init"], "Final": t["sum_final"], "Yield": yield_col, "Liability": tax_col})
    st.table(df_final_sum_renamed.style.format({t["sum_init"]: "${:,.0f}", t["sum_final"]: "${:,.0f}", yield_col: "${:,.0f}", tax_col: "${:,.0f}"}))

    # --- YEAR-BY-YEAR ROADMAP (expandable) ---
    st.divider()
    st.subheader(f"{t['roadmap_h']} {retire_year}")
    with st.expander("Click to expand year-by-year detail", expanded=False):
        show_all_cols = st.checkbox("Show all columns", value=False, key="roadmap_all_cols")

        col_map = {
            "INPUT: SS": t["col_ss"], "raw_div": t["col_div"], "raw_muni": t["col_muni"],
            "raw_cg": t["col_cg"], "LEVER: Roth": t["col_roth"], "INPUT: RMDs": t["col_rmd"], "OUT: MAGI": t["col_magi"],
            "OUT: Fed Tax": t["col_tax"], "raw_outflow": t["col_outflow"],
            "Total Net Worth": t["col_nw"], "Expected Net Worth": t["col_ex_nw"],
            "🚨 Important Events": t["col_events"], "Fed OBBBA":  t["col_obbba"]
        }

        if show_all_cols:
            display_cols = ['Year', 'Ages', 'INPUT: SS', 'raw_div', 'raw_muni', 'raw_cg', 'LEVER: Roth', 'INPUT: RMDs', 'OUT: MAGI', 'OUT: Fed Tax', 'Fed OBBBA', 'raw_outflow', 'Total Net Worth', 'Expected Net Worth', 'IRMAA', '🚨 Important Events']
            fmt = {t["col_ss"]: "${:,.0f}", t["col_div"]: "${:,.0f}", t["col_muni"]: "${:,.0f}", t["col_cg"]: "${:,.0f}", t["col_roth"]: "${:,.0f}", t["col_rmd"]: "${:,.0f}", t["col_magi"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_obbba"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_nw"]: "${:,.0f}", t["col_ex_nw"]: "${:,.0f}"}
        else:
            display_cols = ['Year', 'Ages', 'LEVER: Roth', 'INPUT: RMDs', 'OUT: Fed Tax', 'raw_outflow', 'Expected Net Worth', 'IRMAA', '🚨 Important Events']
            fmt = {t["col_roth"]: "${:,.0f}", t["col_rmd"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_ex_nw"]: "${:,.0f}"}

        st.table(df_active[display_cols].rename(columns=col_map).style.format(fmt))

    # --- About & Methodology (reference, at end) ---
    with st.expander("📖 " + t["motivation_h"] + " & " + t["meth_h"], expanded=False):
        st.subheader(t["motivation_h"])
        st.write(t["motivation_body"])

        st.subheader(t["meth_h"])
        st.markdown(t["meth_body"])

        st.subheader(t["use_h"])
        st.markdown(t["use_body"])

# 1. Define the callback function outside of your main layout
def process_profile_upload():
    # Access the file directly from session_state using the widget's key
    uploaded_file = st.session_state["profile_uploader"]
    
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            for key, value in data.items():
                st.session_state[key] = value
            st.toast("Profile loaded successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")
        # Safely remove the file from session state so the widget resets
        st.session_state.pop("profile_uploader", None)

with tab_data:
    st.subheader(t["tab_data"])
    
    # Create the data payload matching current state settings
    current_profile = {
        "retire_year": retire_year,
        "sim_years": sim_years,
        "h_age_at_retire": h_age_at_retire,
        "w_age_at_retire": w_age_at_retire,
        "ira_h_init": ira_h_init,
        "ira_w_init": ira_w_init,
        "roth_init": roth_init,
        "brokerage_init": brokerage_init,
        "tax_status": tax_status,
        "roth_conv": st.session_state.get('roth_conv', 0),
        "annual_ltcg": annual_ltcg,
        "annual_expense": annual_expense,
        "qd_perc_raw": qd_perc_raw,
        "taxable_div_in": taxable_div_in,
        "muni_int_in": muni_int_in,
        "working_salary": working_salary,
        "ss_h_monthly": ss_h_monthly,
        "ss_h_start": ss_h_start,
        "ss_w_monthly": ss_w_monthly,
        "ss_w_start": ss_w_start,
        "ira_growth_raw": ira_growth_raw,
        "roth_growth_raw": roth_growth_raw,
        "broker_growth_raw": broker_growth_raw,
        "inflation_rate_raw": inflation_rate_raw,
        "lab_legacy_weight": legacy_weight_val,
        "lab_max_irmaa": max_irmaa_limit_val
    }
    
    json_string = json.dumps(current_profile, indent=4)
    col_save, col_load = st.columns(2)
    
    with col_save:
        st.write("### 💾 Export Profile")
        st.caption("Save your current retirement asset values and strategies to your computer.")
        st.download_button(
            label="📥 Download Profile (.json)",
            data=json_string,
            file_name="retirement_profile.json",
            mime="application/json"
        )
        
    with col_load:
        st.write("### 📂 Import Profile")
        st.caption("Upload a previously saved profile file to automatically populate all inputs.")
        #uploaded_file = st.file_uploader("Choose a profile JSON file", type=["json"])
        
        # Assign a key and an on_change callback
        st.file_uploader(
            "Choose a profile JSON file", 
            type=["json"], 
            key="profile_uploader", 
            on_change=process_profile_upload
        )
