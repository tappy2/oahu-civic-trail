import streamlit as st
import streamlit.components.v1 as components
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Oahu Civic Trail v5 - Oregon Trail Edition",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COMPACT HIGH-CONTRAST LIGHT STYLING (ZERO-SCROLL FIT) ---
st.markdown("""
<style>
    /* Zero-scroll fit overrides */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        max-width: 98% !important;
    }
    
    .stApp {
        background-color: #FBF9F1;
        color: #1A1C20;
        font-family: 'Courier New', Courier, monospace;
    }
    
    h1, h2, h3, h4, h5, h6, p, div, label, span {
        color: #1A1C20 !important;
    }
    
    /* Compact HUD Boxes */
    .hud-box {
        background-color: #EDF2F7;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: bold;
        text-align: center;
        font-size: 0.9rem;
        box-shadow: 2px 2px 0px #2D3748;
    }
    
    /* Focused Corridor Bar */
    .corridor-card {
        background-color: #FFFDF5;
        color: #1A202C !important;
        font-family: 'Courier New', monospace;
        padding: 10px 14px;
        border-radius: 6px;
        border: 2px solid #2D3748;
        box-shadow: 3px 3px 0px #2D3748;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }
    
    /* System Updates & Ledger Container */
    .system-updates-box {
        background-color: #FEFCBF;
        border: 2px solid #D69E2E;
        border-radius: 6px;
        padding: 10px 12px;
        color: #744210 !important;
        font-weight: bold;
        font-size: 0.88rem;
        margin-bottom: 8px;
    }

    .ledger-container {
        background-color: #FFFDF5;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 10px;
        box-shadow: 3px 3px 0px #2D3748;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        height: 180px;
        overflow-y: auto;
        line-height: 1.4;
    }

    .trail-card {
        background-color: #FFFFFF;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 3px 3px 0px #2D3748;
    }
    
    /* Status Badges */
    .badge-a { background-color: #C6F6D5; color: #22543D !important; border: 1px solid #38A169; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-b { background-color: #EBF8FF; color: #2B6CB0 !important; border: 1px solid #3182CE; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-c { background-color: #FEFCBF; color: #744210 !important; border: 1px solid #D69E2E; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-d { background-color: #FEEBC8; color: #7B341E !important; border: 1px solid #DD6B20; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-f { background-color: #FED7D7; color: #742A2A !important; border: 1px solid #E53E3E; padding: 2px 8px; border-radius: 4px; font-weight: bold; }

    /* Action Buttons */
    .stButton > button {
        background-color: #2B6CB0 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #1A365D !important;
        border-radius: 5px !important;
        padding: 6px 12px !important;
        box-shadow: 2px 2px 0px #1A365D !important;
        width: 100%;
        font-size: 0.85rem !important;
    }
    .stButton > button:hover {
        background-color: #2C5282 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
def init_game():
    st.session_state.step = "setup_location"
    st.session_state.home_base = None
    st.session_state.income = 75000
    st.session_state.month = 1
    st.session_state.om_coins = 50
    st.session_state.cip_coins = 300
    st.session_state.public_trust = 70
    st.session_state.road_scores = {
        "Kaneohe": 80,
        "Kapolei": 80,
        "Kakaako / Ward": 80,
        "Waikiki": 80
    }
    st.session_state.active_311_count = 14  # Live 311 count from Shauna's map integration
    st.session_state.active_issues = []
    st.session_state.active_patches = {}
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.last_action = "idle"  # idle, working, repaving, sleeping
    st.session_state.latest_event = "🏁 Fiscal Year Q1 Initialized. Choose your first action."
    st.session_state.event_log = [
        "🏁 Fiscal Year Q1 Initialized: Welcome to Oahu Civic Trail v5."
    ]

if 'step' not in st.session_state:
    init_game()

def get_rating_char(score):
    if score >= 90: return "A+", "badge-a"
    elif score >= 80: return "A", "badge-a"
    elif score >= 70: return "B", "badge-b"
    elif score >= 60: return "C", "badge-c"
    elif score >= 50: return "D", "badge-d"
    else: return "F", "badge-f"

# --- RETRO HTML5 CANVAS CHARACTER ANIMATION (OPTION 2 GRAPHICS) ---
def render_retro_scroller(action_state, score, om_coins):
    # Determines character animation state
    grade, _ = get_rating_char(score)
    is_out_of_money = om_coins < 50
    
    html_code = f"""
    <div style="background:#1A202C; border:3px solid #2D3748; border-radius:8px; padding:6px; box-shadow:3px 3px 0px #2D3748; text-align:center;">
        <canvas id="trailCanvas" width="700" height="70" style="background:#2D3748; width:100%; height:70px; border-radius:4px;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('trailCanvas');
        const ctx = canvas.getContext('2d');
        
        let frame = 0;
        let workerX = 40;
        let state = "{action_state}";
        let isLowFunds = {str(is_out_of_money).lower()};
        let grade = "{grade}";

        function drawPixelArt() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Sky & Road Layout
            ctx.fillStyle = '#1A202C';
            ctx.fillRect(0, 0, canvas.width, 42);
            
            // Road Bed
            ctx.fillStyle = (grade === 'A+' || grade === 'A') ? '#4A5568' : (grade === 'F' ? '#742A2A' : '#2D3748');
            ctx.fillRect(0, 42, canvas.width, 28);
            
            // Yellow Road Dashes
            ctx.fillStyle = '#E2E8F0';
            for(let i = 0; i < canvas.width; i += 40) {{
                ctx.fillRect((i - (frame * 2) % 40), 54, 20, 3);
            }}
            
            // Potholes if road score is degraded
            if (grade === 'D' || grade === 'F') {{
                ctx.fillStyle = '#1A202C';
                ctx.beginPath();
                ctx.ellipse(180, 56, 18, 6, 0, 0, Math.PI * 2);
                ctx.ellipse(450, 58, 24, 7, 0, 0, Math.PI * 2);
                ctx.fill();
            }}

            // 8-Bit Mini Scroller Character
            if (isLowFunds && state !== 'repaving') {{
                // Sleeping / Resting State on Chair
                ctx.fillStyle = '#E53E3E'; // Lawn chair
                ctx.fillRect(120, 32, 22, 14);
                ctx.fillStyle = '#F6AD55'; // Character head
                ctx.fillRect(124, 26, 10, 10);
                
                // Animated Zzz
                ctx.fillStyle = '#FFFFFF';
                ctx.font = '12px "Courier New", monospace';
                let zOffset = (frame % 30) * 0.8;
                ctx.fillText("Z z z...", 138, 22 - zOffset);
            }} else if (state === 'working') {{
                // Active Shoveling / Fixing Pothole
                workerX = (workerX + 1.5) % (canvas.width - 60);
                
                // Body & Hat
                ctx.fillStyle = '#DD6B20'; // High-vis vest
                ctx.fillRect(workerX, 28, 14, 18);
                ctx.fillStyle = '#ECC94B'; // Hard hat
                ctx.fillRect(workerX - 2, 22, 18, 6);
                ctx.fillStyle = '#F6AD55'; // Head
                ctx.fillRect(workerX + 2, 26, 10, 6);
                
                // Shovel Motion
                ctx.fillStyle = '#CBD5E0';
                let shovelAngle = (frame % 10 < 5) ? 4 : 0;
                ctx.fillRect(workerX + 14, 34 + shovelAngle, 12, 3);
            }} else if (state === 'repaving') {{
                // Heavy Steamroller Machine Rolling Across
                workerX = (workerX + 2) % (canvas.width - 80);
                ctx.fillStyle = '#ECC94B'; // Paving machine
                ctx.fillRect(workerX, 24, 45, 20);
                ctx.fillStyle = '#4A5568'; // Heavy roller wheel
                ctx.beginPath();
                ctx.arc(workerX + 10, 48, 10, 0, Math.PI * 2);
                ctx.arc(workerX + 35, 48, 10, 0, Math.PI * 2);
                ctx.fill();
            }} else {{
                // Normal Idle Patrol
                workerX = (workerX + 0.8) % (canvas.width - 50);
                ctx.fillStyle = '#3182CE'; // Blue shirt
                ctx.fillRect(workerX, 28, 12, 18);
                ctx.fillStyle = '#ECC94B'; // Hard hat
                ctx.fillRect(workerX - 2, 22, 16, 6);
                ctx.fillStyle = '#F6AD55'; // Head
                ctx.fillRect(workerX + 1, 26, 10, 6);
            }}

            frame++;
            requestAnimationFrame(drawPixelArt);
        }}
        
        drawPixelArt();
    </script>
    """
    components.html(html_code, height=85)

def advance_month(action_choice):
    if st.session_state.game_over or st.session_state.game_won:
        return

    m = st.session_state.month
    my_town = st.session_state.home_base["name"]
    
    # 1. Action Execution
    if action_choice == 1: # DFM In-House Cold Patch
        if st.session_state.om_coins >= 50:
            st.session_state.om_coins -= 50
            st.session_state.last_action = "working"
            if my_town in st.session_state.active_issues:
                st.session_state.active_issues.remove(my_town)
            st.session_state.active_patches[my_town] = True
            st.session_state.road_scores[my_town] = min(100, st.session_state.road_scores[my_town] + 15)
            st.session_state.public_trust = min(100, st.session_state.public_trust + 5)
            st.session_state.active_311_count = max(0, st.session_state.active_311_count - 3)
            msg = f"🔧 Month {m}: Dispatched DFM In-House Crew (-50 O&M Coins). Pothole patched; Public Trust +5%."
        else:
            st.session_state.last_action = "sleeping"
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            msg = f"❌ Month {m}: Insufficient O&M Coins for DFM work order! Road degraded."
            
    elif action_choice == 2: # CIP Repaving RFP
        if st.session_state.public_trust <= 40:
            st.session_state.last_action = "sleeping"
            msg = f"🚫 Month {m}: CIP Repaving RFP BLOCKED by Voters! Public Trust is too low ({st.session_state.public_trust}% <= 40%)."
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
        elif st.session_state.cip_coins >= 300:
            st.session_state.cip_coins -= 300
            st.session_state.last_action = "repaving"
            st.session_state.active_issues = []
            st.session_state.road_scores[my_town] = 100
            st.session_state.public_trust = min(100, st.session_state.public_trust + 20)
            st.session_state.active_311_count = 0
            msg = f"🎉 Month {m}: CIP Repaving RFP Awarded (-300 CIP Coins)! {my_town} corridor fully rehabilitated with Hot-Mix Asphalt."
        else:
            st.session_state.last_action = "sleeping"
            msg = f"❌ Month {m}: Insufficient CIP Coins to fund repaving RFP!"
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            
    elif action_choice == 3: # File 311 & Wait
        st.session_state.last_action = "idle"
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 12)
        if my_town not in st.session_state.active_issues:
            st.session_state.active_issues.append(my_town)
        st.session_state.public_trust -= 8
        st.session_state.active_311_count += 4
        msg = f"📝 Month {m}: Filed HNL 311 Ticket. Request placed in 45-day DFM backlog. Road degraded."
        
    elif action_choice == 4: # Pass Turn
        st.session_state.last_action = "idle"
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 8)
        msg = f"⏳ Month {m}: No maintenance action taken."

    st.session_state.event_log.append(msg)
    
    # 2. Tax Replenishment
    tax_om = max(15, int(st.session_state.income * 0.0002))
    st.session_state.om_coins += tax_om
    st.session_state.event_log.append(f"💵 Tax Allocation: Received +{tax_om} O&M operating revenue.")

    # 3. Dynamic Weather & Macro Events
    event_chance = random.random()
    if event_chance < 0.28: # Hurricane Rains
        was_patched = st.session_state.active_patches.get(my_town, False)
        st.session_state.active_patches[my_town] = False
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 18)
        st.session_state.active_311_count += 5
        event_msg = f"🌀 HURRICANE RAINS & KONA STORM: Severe downpour flooded {my_town}!"
        if was_patched:
            event_msg += " Previous month's cold patch WASHED AWAY, causing subgrade erosion!"
        else:
            event_msg += " Rain infiltrated cracks, expanding road damage!"
        st.session_state.latest_event = event_msg
        st.session_state.event_log.append(event_msg)

    elif event_chance < 0.48: # Rail Windfall / Realignment
        if random.random() < 0.5:
            siphoned = min(st.session_state.cip_coins, 40)
            st.session_state.cip_coins -= siphoned
            event_msg = f"🚧 TRANSIT DEFICIT: Dillingham utility realignment siphoned -{siphoned} CIP Coins from capital pool!"
        else:
            windfall = 50
            st.session_state.cip_coins += windfall
            event_msg = f"🎉 RAIL WINDFALL & FEDERAL MATCH: +{windfall} CIP Coins added to capital pool!"
        st.session_state.latest_event = event_msg
        st.session_state.event_log.append(event_msg)
    else:
        st.session_state.latest_event = msg

    # 4. Check End Conditions
    st.session_state.month += 1
    if st.session_state.public_trust <= 30:
        st.session_state.game_over = True
        st.session_state.step = "ended"
        st.session_state.event_log.append("💀 SYSTEM COLLAPSE: Public Trust dropped to 30%. Voters revoking capital bond authority!")
    elif st.session_state.month > 12:
        st.session_state.step = "ended"
        if st.session_state.road_scores[my_town] >= 75:
            st.session_state.game_won = True
            st.session_state.event_log.append("🏆 FISCAL YEAR SUCCESS: Navigated 12 months of weather and budget constraints!")
        else:
            st.session_state.game_over = True
            st.session_state.event_log.append("⚠️ FISCAL YEAR END: Neighborhood roads ended in failing condition due to budget starvation.")

# =============================================================================
# --- MAIN APP LAYOUT (v5 MASTER EDITION) ---
# =============================================================================

st.markdown("### 🌴 OAHU CIVIC TRAIL v5 <small style='font-size:0.8rem; font-weight:normal;'>| Master Oregon Trail Edition for Maker Mixer</small>", unsafe_allow_html=True)

# --- STEP 1: ONBOARDING ---
if st.session_state.step == "setup_location":
    st.info("Most citizens believe potholes exist because city crews are 'lazy'. This simulator deconstructs how municipal money **actually** flows under Honolulu's hood.")
    st.subheader("📍 STEP 1: Choose Your Home Base Area")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**[A] Kaneohe (Windward)**: Severe subtropical rain intrusion washes away subgrade base courses.")
        if st.button("Choose [A] Kaneohe"):
            st.session_state.home_base = {"name": "Kaneohe", "corridor": "Likelike Hwy Corridor", "vulnerability": "Subgrade Rain Intrusion"}
            st.session_state.step = "setup_income"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**[B] Kapolei (Second City)**: Heavy construction truck traffic accelerates surface cracking.")
        if st.button("Choose [B] Kapolei"):
            st.session_state.home_base = {"name": "Kapolei", "corridor": "Kapolei Pkwy / H-201", "vulnerability": "Construction Axle Load"}
            st.session_state.step = "setup_income"
            st.rerun()

    with c2:
        st.markdown("**[C] Kakaako / Ward (Urban Core)**: Dense utility line trenching & condo construction disrupt road beds.")
        if st.button("Choose [C] Kakaako / Ward"):
            st.session_state.home_base = {"name": "Kakaako / Ward", "corridor": "Ala Moana Blvd / Kapiolani", "vulnerability": "Utility Trenching & Development"}
            st.session_state.step = "setup_income"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**[D] Waikiki (Tourism Hub)**: High traffic volume & heavy tour bus axle load create wheel rutting.")
        if st.button("Choose [D] Waikiki"):
            st.session_state.home_base = {"name": "Waikiki", "corridor": "Kalakaua / Kuhio Ave", "vulnerability": "Tour Bus Axle Load"}
            st.session_state.step = "setup_income"
            st.rerun()

# --- STEP 2: SETUP INCOME ---
elif st.session_state.step == "setup_income":
    st.write(f"📍 **Selected Home Base:** {st.session_state.home_base['name']} ({st.session_state.home_base['corridor']})")
    st.subheader("💵 STEP 2: Choose Household Income Profile")
    st.caption("All taxes pool into the City Highway Fund, but income establishes your neighborhood's Civic Priority Token balance:")
    
    i1, i2 = st.columns(2)
    with i1:
        if st.button("💼 Civil Servant ($65,000/yr) -> 50 O&M / 300 CIP"):
            st.session_state.income = 65000
            st.session_state.om_coins = 50
            st.session_state.cip_coins = 300
            st.session_state.step = "playing"
            st.rerun()
            
        if st.button("🏫 Educator / Teacher ($75,000/yr) -> 60 O&M / 350 CIP"):
            st.session_state.income = 75000
            st.session_state.om_coins = 60
            st.session_state.cip_coins = 350
            st.session_state.step = "playing"
            st.rerun()

    with i2:
        if st.button("🛠️ Small Business Owner ($95,000/yr) -> 80 O&M / 450 CIP"):
            st.session_state.income = 95000
            st.session_state.om_coins = 80
            st.session_state.cip_coins = 450
            st.session_state.step = "playing"
            st.rerun()

# --- STEP 3: MAIN GAMEPLAY SCREEN (SINGLE-TOWN LOCKED MAP & SCROLLER) ---
elif st.session_state.step == "playing":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_cls = get_rating_char(score)
    
    # 1. RETRO 8-BIT SCROLLER GRAPHIC AT TOP
    render_retro_scroller(st.session_state.last_action, score, st.session_state.om_coins)
    
    # 2. TOP HUD STATS ROW
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown(f"<div class='hud-box'>📅 Month {st.session_state.month}/12 | 📍 {my_town}</div>", unsafe_allow_html=True)
    with h2:
        st.markdown(f"<div class='hud-box'>🔵 O&M: {st.session_state.om_coins} Coins <small>(DFM Budget)</small></div>", unsafe_allow_html=True)
    with h3:
        st.markdown(f"<div class='hud-box'>🟡 CIP: {st.session_state.cip_coins} Coins <small>(RFP Bonds)</small></div>", unsafe_allow_html=True)
    with h4:
        st.markdown(f"<div class='hud-box'>❤️ Trust: {st.session_state.public_trust}% <small>(Req > 40%)</small></div>", unsafe_allow_html=True)

    # 3. SINGLE-TOWN LOCKED CORRIDOR CARD (DISPLAYS SHAUNA'S LIVE 311 DATA REPRESENTATION)
    st.markdown(f"""
    <div class='corridor-card'>
        <b>📍 LOCKED CORRIDOR MAP ({my_town}):</b> <span class='{badge_cls}'>Grade {grade} ({score}/100)</span> 
        &nbsp;|&nbsp; <b>Primary Route:</b> {st.session_state.home_base['corridor']} 
        &nbsp;|&nbsp; <b>Live 311 Reports:</b> 🔴 {st.session_state.active_311_count} Active Tickets 
        &nbsp;|&nbsp; <a href='https://oahu-civic-trail-2mg5xyfydqejh44j47sppz.streamlit.app' target='_blank' style='color:#2B6CB0; font-weight:bold;'>[View Shauna's Live 311 Map 🔗]</a>
    </div>
    """, unsafe_allow_html=True)

    # 4. TWO-COLUMN GAMEPLAY PANEL
    col_act, col_log = st.columns([1.1, 0.9])
    
    with col_act:
        st.markdown(f"#### 🎮 Month {st.session_state.month} Action Choices")
        
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("**[1] 🔧 Dispatch DFM Crew**\n* *Cost:* 50 Blue O&M\n* *Outcome:* +15 Health, +5% Trust *(Temporary cold patch)*")
            if st.button("Select [1] Cold Patch"):
                advance_month(1)
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("**[2] 🏗️ Award CIP Repaving RFP**\n* *Cost:* 300 Gold CIP\n* *Outcome:* Restores to **Grade A+**, +20% Trust *(Req Trust > 40%)*")
            if st.button("Select [2] CIP RFP"):
                advance_month(2)
                st.rerun()

        with a2:
            st.markdown("**[3] 📝 File 311 & Wait**\n* *Cost:* 0 Coins\n* *Outcome:* -12 Health, -8% Trust *(45-day DFM backlog)*")
            if st.button("Select [3] 311 Ticket"):
                advance_month(3)
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**[4] ⏩ Pass Turn**\n* *Cost:* 0 Coins\n* *Outcome:* -8 Health *(Observe weather & traffic wear)*")
            if st.button("Select [4] Pass Turn"):
                advance_month(4)
                st.rerun()

    with col_log:
        st.markdown("#### 📢 System Updates & Weather Alert")
        st.markdown(f"<div class='system-updates-box'>⚠️ {st.session_state.latest_event}</div>", unsafe_allow_html=True)
        
        st.markdown("##### 📜 Chronological Event Ledger")
        log_reversed = "<br>".join([f"• {item}" for item in reversed(st.session_state.event_log)])
        st.markdown(f"<div class='ledger-container'>{log_reversed}</div>", unsafe_allow_html=True)

# --- STEP 4: ENDED ---
elif st.session_state.step == "ended":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_cls = get_rating_char(score)
    
    if st.session_state.game_won:
        st.balloons()
        st.success(f"🏆 VICTORY! Fiscal Year Complete. Final Grade for {my_town}: Grade {grade} ({score}/100)")
    else:
        st.error(f"💀 SYSTEM COLLAPSE! Final Grade for {my_town}: Grade {grade} ({score}/100)")

    st.subheader("📜 Final Fiscal Summary")
    log_reversed = "<br>".join([f"• {item}" for item in reversed(st.session_state.event_log)])
    st.markdown(f"<div class='ledger-container' style='height:240px;'>{log_reversed}</div>", unsafe_allow_html=True)
    
    if st.button("🔄 Restart Simulation"):
        init_game()
        st.rerun()

# --- FOOTER / PODCAST EXPANDER ---
with st.expander("🎙️ About the Problem Solvers Podcast", expanded=False):
    st.markdown("""
    Tune in to **Problem Solvers** as we deconstruct complex civic, technical, and economic challenges from first principles.
    
    **The Socratic Lesson:** Potholes aren't caused by 'lazy crews'—they exist because cities run daily 311 work orders (O&M) and long-term capital bonds (CIP) on separate, decoupled ledgers. Stop asking *'Who is to blame?'* and start asking *'What is the actual system problem we need to define first?'*
    """)
