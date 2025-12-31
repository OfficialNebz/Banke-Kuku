import streamlit as st
import requests
import json
import time
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="BANKE KUKU / INTELLIGENCE",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE VIBRANT ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Montserrat:wght@200;300;400;600&display=swap');

    html, body, .stApp { 
        background-color: #000000; 
        font-family: 'Montserrat', sans-serif !important; 
    }

    h1, h2, h3, h4 { 
        font-family: 'Playfair Display', serif !important; 
        letter-spacing: 1px; 
        color: #F4E7D3; /* Creamy Silk Color */
    }

    /* ACCENT COLOR: TROPICAL LIME */
    div.stButton > button {
        width: 100%;
        background-color: transparent;
        color: #dfff4f; /* Neon Lime */
        border: 1px solid #dfff4f;
        padding: 14px 24px;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.4s ease;
        border-radius: 0px;
    }

    div.stButton > button:hover {
        background-color: #dfff4f;
        color: #000000;
        transform: scale(1.02);
    }

    /* INPUT FIELDS */
    div[data-baseweb="input"] > div, textarea {
        background-color: #111;
        border: 1px solid #333 !important;
        color: #FFF !important;
        text-align: center;
        border-radius: 0px;
    }

    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }

    /* TOASTS */
    div[data-baseweb="toast"] {
        background-color: #dfff4f !important;
        color: #000000 !important;
    }

    header {visibility: visible !important; background-color: transparent !important;}
    [data-testid="stDecoration"] {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION & SECRETS ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "results" not in st.session_state: st.session_state.results = None
if "p_name" not in st.session_state: st.session_state.p_name = ""
if "gen_id" not in st.session_state: st.session_state.gen_id = 0

api_key = st.secrets.get("GEMINI_API_KEY")
notion_token = st.secrets.get("NOTION_TOKEN")
notion_db_id = st.secrets.get("NOTION_DB_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### DESIGN STUDIO")
    st.caption("Banke Kuku Intelligence v1.0")
    if st.button("🔄 RESET SYSTEM"):
        st.session_state.clear()
        st.rerun()
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 12px; margin-top: 5px;'><em>Tap to clear cache & start new analysis.</em></div>",
        unsafe_allow_html=True)


# --- 5. AUTHENTICATION ---
def login_screen():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #dfff4f;'>BANKE KUKU</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; letter-spacing: 3px; color: #888;'>OCCASION LOUNGEWEAR</p>",
                    unsafe_allow_html=True)

        password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        st.write("##")
        if st.button("UNLOCK"):
            if password == "neb123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("⚠️ ACCESS DENIED")


if not st.session_state.authenticated:
    login_screen()
    st.stop()


# --- 6. INTELLIGENCE ENGINE ---

def scrape_website(target_url):
    # Allow both main domain and shopify domain
    if "bankekuku" not in target_url:
        return None, "❌ ERROR: INVALID DOMAIN. Locked to Banke Kuku."

    headers = {'User-Agent': 'Mozilla/5.0'}
    clean_url = target_url.split('?')[0]
    json_url = f"{clean_url}.json"
    title = "Banke Kuku Piece"
    desc_text = ""

    # Strategy 1: Shopify JSON
    try:
        r = requests.get(json_url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json().get('product', {})
            title = data.get('title', title)
            raw_html = data.get('body_html', "")
            soup = BeautifulSoup(raw_html, 'html.parser')
            desc_text = soup.get_text(separator="\n", strip=True)
    except:
        pass

    # Strategy 2: HTML
    if not desc_text:
        try:
            r = requests.get(target_url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.content, 'html.parser')
            if soup.find('h1'): title = soup.find('h1').text.strip()
            # Selectors based on Shopify themes
            main_block = soup.find('div', class_='product-description') or \
                         soup.find('div', class_='rte') or \
                         soup.find('div', class_='product__description')
            if main_block: desc_text = main_block.get_text(separator="\n", strip=True)
        except Exception as e:
            return None, f"Scrape Error: {str(e)}"

    if not desc_text: return title, "[NO TEXT FOUND]"

    # Clean Text
    clean_lines = []
    for line in desc_text.split('\n'):
        upper = line.upper()
        if any(x in upper for x in ["SHIPPING", "RETURNS", "SIZE", "WHATSAPP", "ADD TO CART"]): continue
        if len(line) > 5: clean_lines.append(line)
    return title, "\n".join(clean_lines[:25])


def generate_campaign(product_name, description, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-flash-latest')

    prompt = f"""
    Role: Head of Digital Content for 'Banke Kuku'.
    Brand Voice: "Occasion Loungewear." Vibrant, Effortless, Lagos-to-London, Statement Prints.
    Product: {product_name}
    Specs: {description}

    TASK:
    1. Select TOP 3 Personas from the list.
    2. Write 3 Captions.
    3. Write 1 "Hybrid Vibe Caption".

    PERSONAS:
    1. The Lagos Socialite (Tone: 'Owambe ready', but make it comfortable. Life of the party.)
    2. The Notting Hill Expat (Tone: Global cool, wears pajamas to dinner, effortless wealth.)
    3. The Tropical Traveller (Tone: Ibiza, Zanzibar, sipping cocktails, vibrant life.)
    4. The 'Soft Life' Advocate (Tone: Rejects stress, embraces silk and ease.)

    CRITICAL INSTRUCTIONS:
    - FOCUS ON THE PRINT: Banke Kuku is about the print. Mention 'vibrancy', 'story', 'pattern'.
    - KEYWORD: 'Ease'. It must sound comfortable but expensive.
    - NO 'WORK' TALK: This woman is not working. She is living.

    Output JSON ONLY:
    [
        {{"persona": "Persona Name", "post": "Caption text..."}},
        ...
        {{"persona": "Banke Kuku Signature", "post": "The unified caption text..."}}
    ]
    """
    try:
        response = model.generate_content(prompt)
        txt = response.text
        if "```json" in txt: txt = txt.split("```json")[1].split("```")[0]
        return json.loads(txt.strip())
    except Exception as e:
        return [{"persona": "Error", "post": f"AI ERROR: {str(e)}"}]


def save_to_notion(p_name, post, persona, token, db_id):
    if not token or not db_id: return False, "Notion Secrets Missing"

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": db_id},
        "properties": {
            "Product Name": {"title": [{"text": {"content": str(p_name)}}]},
            "Persona": {"rich_text": [{"text": {"content": str(persona)}}]},
            "Generated Post": {"rich_text": [{"text": {"content": str(post)[:2000]}}]},
            "Status": {"status": {"name": "Draft"}}
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"Notion Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"System Error: {str(e)}"


# --- 7. UI LAYOUT ---
st.markdown("<br>", unsafe_allow_html=True)
st.title("BANKE KUKU / INTELLIGENCE")
st.markdown("---")

# --- MANUAL ADDED HERE ---
with st.expander("📖 SYSTEM MANUAL (CLICK TO OPEN)"):
    st.markdown("### OPERATIONAL GUIDE")
    st.markdown("---")

    # Step 1
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.markdown("**STEP 1: SOURCE**\n\nGo to the Banke Kuku site. Open a single product page.")
    with c2:
        try:
            st.image("Screenshot (572).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (572).png not found.")

    st.markdown("---")

    # Step 2
    c3, c4 = st.columns([1, 1.5])
    with c3:
        st.markdown("**STEP 2: ACQUIRE**\n\nCopy the URL from the browser bar.")
    with c4:
        try:
            st.image("Screenshot (573).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (573).png not found.")

    st.markdown("---")

    # Step 3
    c5, c6 = st.columns([1, 1.5])
    with c5:
        st.markdown("**STEP 3: EXECUTE**\n\nPaste the URL below and click 'GENERATE ASSETS'.")
    with c6:
        try:
            st.image("Screenshot (574).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (574).png not found.")

# INPUT
url_input = st.text_input("Product URL", placeholder="Paste Banke Kuku URL...")

if st.button("GENERATE ASSETS", type="primary"):
    if not api_key:
        st.error("API Key Missing.")
    elif not url_input:
        st.error("Paste a URL first.")
    else:
        with st.spinner("Analyzing Prints & Fabric..."):
            st.session_state.gen_id += 1
            p_name, p_desc = scrape_website(url_input)
            if p_name is None:
                st.error(p_desc)
            else:
                st.session_state.p_name = p_name
                st.session_state.results = generate_campaign(p_name, p_desc, api_key)

# --- 8. RESULTS DASHBOARD ---
if st.session_state.results:
    st.divider()
    st.subheader(st.session_state.p_name.upper())

    # BULK EXPORT
    if st.button("💾 EXPORT CAMPAIGN TO NOTION", type="primary", use_container_width=True):
        if not notion_token:
            st.error("Notion Config Missing")
        else:
            success = 0
            with st.spinner("Syncing to Notion..."):
                bar = st.progress(0)
                for i, item in enumerate(st.session_state.results):
                    p_val = item.get('persona', '')
                    final_post = st.session_state.get(f"editor_{i}_{st.session_state.gen_id}", item.get('post', ''))
                    if p_val and final_post:
                        s, m = save_to_notion(st.session_state.p_name, final_post, p_val, notion_token, notion_db_id)
                        if s: success += 1
                    bar.progress((i + 1) / len(st.session_state.results))

            if success > 0:
                st.success(f"Uploaded {success} Assets.")
                time.sleep(1)
                st.rerun()

    st.markdown("---")

    # EDITORS
    current_gen = st.session_state.gen_id
    for i, item in enumerate(st.session_state.results):
        persona = item.get('persona', 'Unknown')
        post = item.get('post', '')

        with st.container():
            c1, c2 = st.columns([0.75, 0.25])
            with c1:
                st.subheader(persona)
                edited = st.text_area(label=persona, value=post, height=200, key=f"editor_{i}_{current_gen}",
                                      label_visibility="collapsed")
            with c2:
                st.write("##");
                st.write("##")
                if st.button("SAVE", key=f"btn_{i}_{current_gen}"):
                    with st.spinner("Saving..."):
                        s, m = save_to_notion(st.session_state.p_name, edited, persona, notion_token, notion_db_id)
                        if s:
                            st.toast("✅ Saved")
                        else:
                            st.error(m)
        st.divider()