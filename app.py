import streamlit as st
import pandas as pd
import os


# ============================================================
# RecoverAI - Dark Neon Fintech Theme
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(89, 45, 170, 0.22), transparent 28%),
        radial-gradient(circle at 85% 15%, rgba(0, 150, 255, 0.16), transparent 25%),
        radial-gradient(circle at 50% 90%, rgba(120, 40, 220, 0.12), transparent 30%),
        #070b18;
    color: #f4f7ff;
}

/* Main content */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Headings */
h1 {
    color: #ffffff !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #f4f7ff !important;
}

/* Subtitle / normal text */
p, label, .stMarkdown {
    color: #b9c4e2;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(25, 32, 65, 0.95),
        rgba(12, 17, 38, 0.95)
    );
    border: 1px solid rgba(115, 90, 255, 0.35);
    border-radius: 18px;
    padding: 22px;
    box-shadow:
        0 0 25px rgba(70, 40, 180, 0.12),
        inset 0 1px 0 rgba(255,255,255,0.05);
}

[data-testid="stMetricLabel"] {
    color: #9ca9d0 !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(100, 120, 255, 0.25);
}

/* Info boxes */
[data-testid="stAlert"] {
    background: rgba(25, 35, 70, 0.85);
    border: 1px solid rgba(100, 120, 255, 0.3);
    border-radius: 14px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.6rem 1.2rem;
    box-shadow: 0 0 18px rgba(90, 70, 255, 0.25);
    transition: 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 28px rgba(120, 80, 255, 0.45);
}

/* Select box */
[data-baseweb="select"] > div {
    background-color: #11182d;
    border: 1px solid rgba(110, 120, 255, 0.35);
    border-radius: 12px;
}

/* Dividers */
hr {
    border-color: rgba(130, 140, 200, 0.18);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #080d20 0%,
            #0b1028 50%,
            #080b18 100%
        );
    border-right: 1px solid rgba(100, 80, 255, 0.25);
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #c7d2f2;
}

/* Glow effect around sections */
.element-container {
    border-radius: 12px;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RecoverAI",
    page_icon="💳",
    layout="wide"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

@st.cache_data
def load_data():

    transactions = pd.read_csv(
        "data/transactions.csv"
    )

    results = pd.read_csv(
        "data/recovery_results.csv"
    )

    return transactions, results


transactions, results = load_data()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("💳 RecoverAI")

st.subheader(
    "AI-Powered Revenue Recovery Agent"
)

st.caption(
    "Detect → Diagnose → Decide → Recover → Verify"
)

st.divider()


# --------------------------------------------------
# Business metrics
# --------------------------------------------------

total_revenue = results["amount"].sum()

recovered_revenue = results[
    "recovered_amount"
].sum()

recovery_rate = (
    recovered_revenue / total_revenue * 100
)

recovered_transactions = results[
    "recovered"
].sum()

retry_count = (
    results["recommended_action"] == "RETRY"
).sum()

message_count = (
    results["recommended_action"] == "MESSAGE"
).sum()

stop_count = (
    results["recommended_action"] == "STOP"
).sum()


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Revenue at Risk",
        f"₹{total_revenue:,.0f}"
    )


with col2:
    st.metric(
        "Recovered Revenue",
        f"₹{recovered_revenue:,.0f}"
    )


with col3:
    st.metric(
        "Recovery Rate",
        f"{recovery_rate:.2f}%"
    )


with col4:
    st.metric(
        "Transactions Recovered",
        f"{recovered_transactions}"
    )


st.divider()


# --------------------------------------------------
# Action distribution
# --------------------------------------------------

st.subheader("Recovery Strategy")


action_data = pd.DataFrame({
    "Action": [
        "Retry",
        "Message",
        "Stop"
    ],
    "Transactions": [
        retry_count,
        message_count,
        stop_count
    ]
})


col1, col2 = st.columns(2)


with col1:

    st.bar_chart(
        action_data.set_index("Action")
    )


with col2:

    st.write("### Agent decisions")

    st.write(
        f"🔄 **Retry:** {retry_count}"
    )

    st.write(
        f"💬 **Message:** {message_count}"
    )

    st.write(
        f"🛑 **Stop:** {stop_count}"
    )

    st.info(
        "The agent uses bounded recovery rules "
        "to avoid unlimited payment retries."
    )


st.divider()


# --------------------------------------------------
# Recovery queue
# --------------------------------------------------

st.subheader("Recovery Queue")


display_columns = [
    "transaction_id",
    "amount",
    "payment_method",
    "failure_reason",
    "recovery_probability",
    "recommended_action",
    "recovered"
]


queue = results[display_columns].copy()


queue["recovery_probability"] = (
    queue["recovery_probability"] * 100
).round(1)


queue["recovery_probability"] = (
    queue["recovery_probability"].astype(str)
    + "%"
)


queue["recovered"] = queue[
    "recovered"
].map({
    1: "✅ Recovered",
    0: "❌ Not recovered"
})


queue = queue.rename(
    columns={
        "transaction_id": "Transaction",
        "amount": "Amount",
        "payment_method": "Method",
        "failure_reason": "Failure",
        "recovery_probability": "Recovery Probability",
        "recommended_action": "Action",
        "recovered": "Outcome"
    }
)


st.dataframe(
    queue.head(50),
    use_container_width=True,
    hide_index=True
)


st.caption(
    "Showing first 50 transactions."
)


st.divider()


# --------------------------------------------------
# Transaction investigation
# --------------------------------------------------

st.subheader("🔎 Investigate a Transaction")


transaction_ids = results[
    "transaction_id"
].tolist()


selected_id = st.selectbox(
    "Select transaction",
    transaction_ids
)


selected = results[
    results["transaction_id"] == selected_id
].iloc[0]


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Amount",
        f"₹{selected['amount']:,.2f}"
    )


with col2:

    st.metric(
        "Recovery Probability",
        f"{selected['recovery_probability'] * 100:.1f}%"
    )


with col3:

    st.metric(
        "Previous Attempts",
        int(selected["previous_attempts"])
    )


st.write("### AI Diagnosis")

st.info(
    selected["diagnosis"]
)


st.write("### Recommended Action")

action = selected[
    "recommended_action"
]


if action == "RETRY":

    st.success(
        "🔄 RETRY — controlled payment retry recommended."
    )

elif action == "MESSAGE":

    st.warning(
        "💬 MESSAGE — customer intervention recommended."
    )

else:

    st.error(
        "🛑 STOP — further automated attempts should stop."
    )


st.write("### Decision Reason")

st.write(
    selected["decision_reason"]
)


st.write("### Recovery Outcome")

if selected["recovered"] == 1:

    st.success(
        f"₹{selected['recovered_amount']:,.2f} "
        "was recovered in the simulation."
    )

else:

    st.error(
        "The simulated recovery attempt failed."
    )


st.caption(
    "Synthetic demonstration only — no real payment was processed."
)


st.divider()


# --------------------------------------------------
# Safety / audit information
# --------------------------------------------------

st.subheader("🛡️ Agent Safety Controls")

safety_col1, safety_col2, safety_col3 = st.columns(3)


with safety_col1:

    st.write("**Retry limit**")

    st.write(
        "Maximum 3 previous attempts."
    )


with safety_col2:

    st.write("**Customer-action failures**")

    st.write(
        "Authentication and insufficient-funds "
        "cases prefer customer messaging."
    )


with safety_col3:

    st.write("**Auditability**")

    st.write(
        "Every recommendation and outcome "
        "is recorded in the recovery results."
    )


st.divider()


st.caption(
    "RecoverAI | AI Buildathon Prototype | "
    "Synthetic data and simulated payment outcomes"
)

# ------------------------------------------------------------
# Recovery Audit Trail
# ------------------------------------------------------------

st.divider()

st.subheader("🔐 Recovery Audit Trail")

audit_file = "data/audit_log.csv"

if os.path.exists(audit_file):

    audit = pd.read_csv(audit_file)

    audit_col1, audit_col2 = st.columns(2)

    with audit_col1:
        st.metric(
            "Audit Records",
            f"{len(audit):,}"
        )

    with audit_col2:
        recovered_audit = int(
            (audit["outcome"] == "Recovered").sum()
        )

        st.metric(
            "Recovered Decisions",
            f"{recovered_audit:,}"
        )

    st.caption(
        "Every recovery decision is recorded with probability, "
        "diagnosis, action, reason, and outcome."
    )

    audit_display = audit.tail(50).copy()

    st.dataframe(
        audit_display,
        width="stretch",
        hide_index=True
    )

else:

    st.warning(
        "Audit log not found. Run the recovery batch first."
    )

# ------------------------------------------------------------
# Recovery Analytics
# ------------------------------------------------------------

st.divider()

st.subheader("📊 Recovery Analytics")

# Recovery performance by payment method
method_data = (
    results.groupby("payment_method")
    .agg(
        Revenue=("amount", "sum"),
        Recovered=("recovered_amount", "sum")
    )
)

method_data["Recovery Rate"] = (
    method_data["Recovered"] / method_data["Revenue"] * 100
)

analytics_col1, analytics_col2 = st.columns(2)

with analytics_col1:
    st.write("### Recovery Rate by Payment Method")

    st.bar_chart(
        method_data["Recovery Rate"]
    )

with analytics_col2:
    st.write("### Recovered Revenue by Action")

    action_revenue = (
        results.groupby("recommended_action")["recovered_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(action_revenue)

st.write("### Failure Reason Analysis")

failure_data = (
    results.groupby("failure_reason")
    .agg(
        Transactions=("transaction_id", "count"),
        Revenue=("amount", "sum"),
        Recovered=("recovered_amount", "sum")
    )
    .sort_values("Revenue", ascending=False)
)

st.dataframe(
    failure_data,
    width="stretch"
)

st.caption(
    "Analytics are based on synthetic transactions and simulated recovery outcomes."
)