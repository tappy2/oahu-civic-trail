import streamlit as st
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Oahu Civic Trail - Simulator",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Courier New', Courier, monospace;
    }
    .metric-card {
        background-color: #1E222D;
        border: 1px solid #363B4E;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .status-badge {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 4px;
        display: inline-block;
    }
    .badge-a { background-color: #1E5128; color: #4E9F3D; }
    .badge-b { background-color: #1B4D3E; color: #76BA99; }
    .badge-c { background-color: #5C4033; color: #E5BA73; }
    .badge-d { background-color: #78290F; color: #FF7D00; }
    .badge-f { background-color: #4A0E17; color: #FF2E93; animation: blink 1s infinite; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
def init_game():
    st.session_state.month = 1
    st.session_state.om_coins = 40
    st.session_state.cip_coins = 400
    st.session_state.public_trust = 65
    st.session_state.pavement_rating = "C"  # A, B, C, D, F
    st.session_state.active_patches = 1
    st.session_state.subgrade_eroded = False
    st.session_state.om_cost = 50
    st.session_state.cip_cost = 400
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.event_log = [
        "🏁 Simulation initialized. Welcome to Fiscal Year Month 1. Road condition is Rating C."
    ]

if 'month' not in st.session_state:
    init_game()

# --- HELPER LOGIC ---
def get_rating_badge(rating):
    badges = {
        "A": '<span class="status-badge badge-a">🟢 RATING A (Newly Repaved)</span>',
        "B": '<span class="status-badge badge-b">🟢 RATING B (Good)</span>',
        "C": '<span class="status-badge badge-c">🟡 RATING C (Minor Cracks)</span>',
        "D": '<span class="status-badge badge-d">🟠 RATING D (Severe Potholes)</span>',
        "F": '<span class="status-badge badge-f">🔴 RATING F (Subgrade Failure)</span>'
    }
    return badges.get(rating, rating)

def trigger_next_month():
    if st.session_state.game_over or st.session_state.game_won:
        return

    st.session_state.month += 1
    m = st.session_state.month

    # Monthly tax revenue replenishment
    st.session_state.om_coins += 15
    st.session_state.event_log.append(f"📅 Month {m}: Received +15 O&M tax revenue.")

    # Random Roadblock Events
    event_chance = random.random()

    # Event 1: Tropical Storm / Kona Downpour (Higher chance in winter/mid months)
    if event_chance < 0.35:
        st.session_state.event_log.append("🌀 EVENT: Tropical Storm / Kona Downpour struck Oahu!")
        if st.session_state.active_patches > 0:
            st.session_state.active_patches = 0
            st.session_state.event_log.append("⚠️ Torrential runoff washed away all active O&M cold patches!")
        
        if st.session_state.pavement_rating in ["C", "D", "F"]:
            st.session_state.subgrade_eroded = True
            st.session_state.pavement_rating = "F"
            st.session_state.cip_cost = 600
            st.session_state.public_trust -= 15
            st.session_state.event_log.append("🚨 Base course saturated! Water intrusion caused SUBGRADE EROSION. Repaving cost inflated to 600 CIP!")
        else:
            st.session_state.pavement_rating = "D"
            st.session_state.public_trust -= 5

    # Event 2: Fed Rate Hike & Bond Yield Spike
    elif event_chance < 0.60:
        st.session_state.event_log.append("📈 EVENT: Federal Reserve Rate Hike & Bond Market Yield Spike.")
        st.session_state.cip_cost += 50
        st.session_state.event_log.append(f"💸 Municipal bond debt servicing surcharges increased CIP repaving cost to {st.session_state.cip_cost} CIP!")

    # Event 3: Maritime Bottleneck & Diesel Price Spike
    elif event_chance < 0.80:
        st.session_state.om_cost = 75
        st.session_state.event_log.append("🚢 EVENT: West Coast Maritime Bottleneck & Fuel Spike. Cold-mix asphalt cost increased to 75 O&M!")
    else:
        # Standard natural degradation
        st.session_state.om_cost = 50  # Reset temporary cost surge
        if st.session_state.active_patches > 0:
            st.session_state.event_log.append("ℹ️ Cold patches held off further road degradation this month.")
        else:
            if st.session_state.pavement_rating == "A":
                st.session_state.pavement_rating = "B"
            elif st.session_state.pavement_rating == "B":
                st.session_state.pavement_rating = "C"
            elif st.session_state.pavement_rating == "C":
                st.session_state.pavement_rating = "D"
                st.session_state.public_trust -= 8
            elif st.session_state.pavement_rating == "D":
                st.session_state.pavement_rating = "F"
                st.session_state.public_trust -= 15

    # Check Victory or Collapse Conditions
    if st.session_state.public_trust <= 30:
        st.session_state.game_over = True
        st.session_state.event_log.append("❌ SYSTEM COLLAPSE: Public Trust dropped to 30%. Voters passed a referendum stripping bond authority!")
    elif m >= 6 and st.session_state.pavement_rating in ["A", "B"]:
        st.session_state.game_won = True
        st.session_state.event_log.append("🎉 VICTORY: You survived 6 months and restored Oahu's transit corridor to optimal condition!")

# --- UI HEADER ---
st.title("🌴 OAHU CIVIC TRAIL")
st.caption("A First-Principles Civic Engineering Simulator | Maker Mixer Interactive Demo")

st.markdown("""
**Can you navigate Oahu's transit corridors through tropical storms and inflation without bankrupting the city or triggering Voter Rejection?**
""")

# --- TOP METRICS HUD ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📅 Month",
        value=f"{st.session_state.month} / 6"
    )

with col2:
    st.metric(
        label="🔵 O&M Wallet (Operating Cash)",
        value=f"{st.session_state.om_coins} Coins",
        delta=f"-{st.session_state.om_cost} per patch"
    )

with col3:
    st.metric(
        label="🟡 CIP Wallet (Capital Bond Funds)",
        value=f"{st.session_state.cip_coins} Coins",
        delta=f"Req: {st.session_state.cip_cost} Coins"
    )

with col4:
    trust_color = "normal" if st.session_state.public_trust > 40 else "inverse"
    st.metric(
        label="❤️ Public Trust Rating",
        value=f"{st.session_state.public_trust}%",
        delta="-15% threshold risk" if st.session_state.public_trust <= 40 else "Stable"
    )

st.divider()

# --- MAIN GAME PANEL ---
left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("🛣️ Oahu Commute Corridor Status")
    st.markdown(get_rating_badge(st.session_state.pavement_rating), unsafe_allow_html=True)
    st.write("")

    if st.session_state.subgrade_eroded:
        st.error("⚠️ CRITICAL STRUCTURAL FAILURE: Base course subgrade has eroded due to water intrusion. Temporary patches will no longer hold. Full CIP Repaving Bond required!")
    elif st.session_state.active_patches > 0:
        st.info(f"🔧 Active Maintenance: {st.session_state.active_patches} cold patch(es) currently applied.")

    st.write("### 🎮 Executive Actions")
    
    act_col1, act_col2 = st.columns(2)

    with act_col1:
        patch_btn = st.button(
            f"🔧 Apply O&M Cold Patch (-{st.session_state.om_cost} O&M)",
            disabled=st.session_state.game_over or st.session_state.game_won or st.session_state.om_coins < st.session_state.om_cost
        )
        if patch_btn:
            st.session_state.om_coins -= st.session_state.om_cost
            st.session_state.active_patches += 1
            if st.session_state.pavement_rating == "D":
                st.session_state.pavement_rating = "C"
            st.session_state.public_trust = min(100, st.session_state.public_trust + 5)
            st.session_state.event_log.append(f"🔧 Applied O&M Cold Patch. Public Trust slightly restored (+5%).")
            st.rerun()

    with act_col2:
        # CIP Bond requires Public Trust > 40%
        can_bond = st.session_state.public_trust > 40 and st.session_state.cip_coins >= st.session_state.cip_cost
        bond_btn = st.button(
            f"🏗️ Issue CIP Repaving Bond (-{st.session_state.cip_cost} CIP)",
            disabled=st.session_state.game_over or st.session_state.game_won or not can_bond
        )
        if bond_btn:
            st.session_state.cip_coins -= st.session_state.cip_cost
            st.session_state.pavement_rating = "A"
            st.session_state.subgrade_eroded = False
            st.session_state.active_patches = 0
            st.session_state.public_trust = min(100, st.session_state.public_trust + 25)
            st.session_state.event_log.append("🏗️ CIP Repaving Bond Approved! Corridor fully rehabilitated to Rating A.")
            st.rerun()

    st.write("")
    next_btn = st.button(
        "⏩ Advance to Next Month (Trigger Weather & Market Loop)",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.game_over or st.session_state.game_won
    )
    if next_btn:
        trigger_next_month()
        st.rerun()

    if st.session_state.game_over:
        st.error("💥 GAME OVER: System Collapse! Public Trust eroded below safety thresholds.")
        if st.button("🔄 Restart Simulation"):
            init_game()
            st.rerun()

    if st.session_state.game_won:
        st.balloons()
        st.success("🏆 VICTORY! You successfully navigated fiscal and weather crises to maintain Oahu's infrastructure!")
        if st.button("🔄 Play Again"):
            init_game()
            st.rerun()

with right_col:
    st.subheader("📜 Live Event Ticker & Ledger Log")
    log_box = "\n\n".join(reversed(st.session_state.event_log))
    st.text_area("Chronological System Log", value=log_box, height=350, disabled=True)

st.divider()

# --- SOCRATIC REVEAL & PODCAST SIDEBAR / FOOTER ---
with st.expander("💡 WHY DID WE BUILD THIS GAME? (The Socratic Reveal & Podcast Hook)", expanded=True):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        ### The Problem Isn't the Pothole—It's the System Architecture.
        Most people assume streets crumble because city workers are slow or asphalt is cheap. But as this simulation proves:
        1. **Decoupled Ledgers:** Municipalities run daily **311 work orders (O&M)** on one system and **long-term capital bonds (CIP)** on a completely separate ledger.
        2. **The Starvation Trap:** Cities are legally barred from using capital funds to fix a road *before* it breaks, forcing them to waste tax dollars on temporary cold patches that wash out during tropical storms.
        3. **Voter Rejection:** When short-term fixes fail, Public Trust drops—blocking the very bond funding needed to solve the root problem.
        """)
    with col_b:
        st.info("""
        ### 🎙️ The Problem Solvers Podcast
        Join **Host**, **Pua**, and **Shauna** as we deconstruct complex civic and technical challenges from first principles.

        *Stop asking 'Who is to blame?' and start asking 'What is the actual problem we need to define first?'*
        """)
