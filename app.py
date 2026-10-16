import os
from datetime import date, datetime, time
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MediPredict | AI Health Assistant", page_icon="🩺", layout="wide")

# ---------------------------- Theme / styling ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f4f7fb; }
[data-testid="stSidebar"] { background: #101c31; }
[data-testid="stSidebar"] * { color: #eef5ff !important; }
.hero { padding: 1.6rem 1.8rem; border-radius: 22px; color: white;
        background: linear-gradient(120deg,#0d9488,#2563eb); margin-bottom: 1.2rem; }
.hero h1 { font-family: Manrope,sans-serif; font-size: 2.2rem; margin: 0; }
.hero p { opacity:.93; margin:.4rem 0 0; }
.metric-card { background:white; padding:1.1rem; border:1px solid #e2e8f0;
               border-radius:16px; min-height:105px; }
.metric-label { color:#64748b; font-size:.88rem; }
.metric-value { color:#0f766e; font-family:Manrope,sans-serif; font-size:1.7rem;font-weight:800; }
.note { padding: .9rem 1rem; border-radius: 12px; background:#fff7ed;
        border:1px solid #fed7aa; color:#9a3412; margin:.8rem 0; }
.small-muted { color:#64748b; font-size:.9rem; }
div.stButton > button { border-radius:10px; font-weight:650; }
</style>
""", unsafe_allow_html=True)

SYMPTOMS = {
    "fever":"Fever", "cough":"Cough", "cold":"Runny nose", "sneeze":"Sneezing",
    "sore":"Sore throat", "head":"Headache", "body":"Body pain", "fat":"Fatigue",
    "chill":"Chills", "sweat":"Sweating", "nau":"Nausea", "vom":"Vomiting",
    "dia":"Diarrhea", "abd":"Stomach pain", "rash":"Skin rash", "itch":"Itching",
    "eye":"Red/itchy eyes", "breath":"Shortness of breath", "chest":"Chest pain",
    "joint":"Joint pain", "thirst":"Excess thirst", "urine":"Frequent urination",
    "blur":"Blurred vision", "dizz":"Dizziness", "light":"Light sensitivity",
    "appet":"Loss of appetite", "taste":"Loss of taste/smell", "weight":"Weight loss",
    "yellow":"Yellow skin/eyes", "pal":"Palpitations"
}
CONDITIONS = [
 {"name":"Common Cold","severity":"Usually mild","symptoms":{"cold":3,"sneeze":3,"sore":2,"cough":2,"head":1,"fat":1},"tips":["Rest and drink warm fluids.","Consider salt-water gargles for a sore throat.","Seek medical advice if symptoms persist or worsen."],"doctor":"Get medical advice for difficulty breathing, a persistent high fever, or symptoms lasting over 10 days."},
 {"name":"Influenza (Flu)","severity":"Needs attention","symptoms":{"fever":3,"body":3,"chill":2,"cough":2,"fat":2,"head":2,"sore":1},"tips":["Rest and stay hydrated.","Ask a clinician or pharmacist before taking medicine.","Limit close contact while unwell."],"doctor":"Seek prompt medical advice for breathing difficulty, dehydration, or worsening symptoms."},
 {"name":"COVID-19","severity":"Needs attention","symptoms":{"fever":2,"cough":2,"taste":4,"fat":2,"breath":2,"body":1,"sore":1},"tips":["Consider testing and follow current local guidance.","Stay hydrated and rest.","Reduce contact with others while symptomatic."],"doctor":"Breathing difficulty, confusion, blue/grey lips, or severe chest pain needs urgent help."},
 {"name":"Dengue (possibility)","severity":"Prompt evaluation","symptoms":{"fever":3,"head":2,"body":3,"joint":3,"rash":2,"nau":1,"fat":1,"eye":1},"tips":["Seek medical assessment if dengue is possible.","Drink fluids if you can keep them down.","Avoid aspirin or ibuprofen unless a clinician tells you otherwise."],"doctor":"Urgent assessment is important for severe abdominal pain, repeated vomiting, bleeding, faintness, or marked drowsiness."},
 {"name":"Malaria (possibility)","severity":"Prompt evaluation","symptoms":{"fever":3,"chill":4,"sweat":3,"head":2,"nau":1,"vom":1,"body":1},"tips":["Arrange prompt medical assessment and testing.","Do not self-start antimalarial medicines.","Prevent mosquito bites."],"doctor":"Fever with chills after possible mosquito exposure should be assessed promptly."},
 {"name":"Typhoid (possibility)","severity":"Prompt evaluation","symptoms":{"fever":3,"abd":3,"head":1,"appet":2,"fat":2,"dia":2,"nau":1},"tips":["Arrange medical assessment and appropriate testing.","Drink safe water and eat well-cooked food.","Do not take antibiotics without a prescription."],"doctor":"Seek prompt care for persistent fever, severe abdominal pain, confusion, or dehydration."},
 {"name":"Gastroenteritis","severity":"Needs attention","symptoms":{"dia":4,"vom":3,"nau":3,"abd":3,"fever":1,"fat":1},"tips":["Use oral rehydration solution (ORS) if appropriate.","Take small, frequent sips of fluid.","Avoid food or drinks that worsen symptoms."],"doctor":"Get medical help for blood in stool, severe pain, dehydration, or inability to keep fluids down."},
 {"name":"Migraine (possibility)","severity":"Usually mild","symptoms":{"head":4,"light":3,"nau":2,"vom":1,"dizz":1},"tips":["Rest in a quiet, dark room if this helps.","Drink water and maintain regular sleep.","Track possible triggers."],"doctor":"A sudden, unusually severe headache, weakness, confusion, or vision loss needs emergency assessment."},
 {"name":"Allergic Rhinitis","severity":"Usually mild","symptoms":{"sneeze":3,"itch":2,"eye":3,"cold":3,"cough":1},"tips":["Reduce exposure to dust or pollen where possible.","Wash your face after outdoor exposure.","Ask a clinician or pharmacist about suitable treatment."],"doctor":"Wheezing, trouble breathing, or swelling of the lips/tongue/throat is an emergency."},
 {"name":"Type 2 Diabetes (risk indicators)","severity":"Needs assessment","symptoms":{"thirst":3,"urine":3,"blur":2,"fat":2,"weight":2,"appet":1},"tips":["Arrange a blood glucose or HbA1c test with a healthcare professional.","Choose balanced meals and regular activity where suitable.","Do not use symptoms alone to determine blood sugar."],"doctor":"Seek urgent care for vomiting with deep/rapid breathing, confusion, or severe weakness."},
 {"name":"Jaundice / liver problem (possibility)","severity":"Prompt evaluation","symptoms":{"yellow":5,"fat":2,"appet":2,"nau":2,"abd":2,"itch":1,"fever":1},"tips":["Arrange prompt medical assessment.","Avoid alcohol until assessed.","A clinician may recommend liver blood tests."],"doctor":"Yellowing of the skin or eyes should be medically assessed promptly."}
]
FIRST_AID = [
 ("❤️","Cardiac arrest / CPR","Call India's emergency number 112 and follow the dispatcher's instructions. If the person is unresponsive and not breathing normally, begin chest compressions in the centre of the chest at 100–120/min if able. Use an AED if available."),
 ("🔥","Burns","Cool the burn under cool running water for 20 minutes. Do not use ice, butter, toothpaste, or creams. Seek urgent help for large, deep, chemical, electrical, or face/hand/genital burns."),
 ("🩸","Heavy bleeding","Call emergency services for severe bleeding. Apply firm, continuous pressure with clean cloth or dressing. Do not repeatedly lift it to check; follow emergency-dispatch instructions."),
 ("😮‍💨","Choking","Call emergency services if severe. For an adult who cannot speak, cough, or breathe, give 5 back blows then 5 abdominal thrusts; repeat. Use age-appropriate guidance for children/infants.")
]
TIPS = [
 "Keep water nearby and sip regularly through the day.",
 "Aim for regular movement that suits your health and ability.",
 "A consistent sleep schedule can support general wellbeing.",
 "Include a variety of vegetables, fruit, protein and whole grains.",
 "Short breathing breaks may help you reset during a busy day."
]

def init_state():
    defaults = {
        "profile": {"name":"Guest","age":None,"blood_group":""},
        "history": [], "readings": [], "medicines": [], "chat": [],
        "selected_symptoms": [], "page": "Dashboard"
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init_state()

def metric(label, value):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def predict_conditions(keys):
    results=[]
    for d in CONDITIONS:
        matched = sum(weight for k,weight in d["symptoms"].items() if k in keys)
        count = sum(1 for k in d["symptoms"] if k in keys)
        if count:
            # Relative matching score for demo ranking, not a clinical probability.
            score = round(100 * count / max(1, len(keys)) * (matched / max(1, sum(d["symptoms"].values()))), 1)
            results.append((score,d,count))
    return sorted(results, key=lambda x:x[0], reverse=True)[:3]

def ai_answer(prompt, history=None):
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY",""))
    if not api_key:
        return ("AI chat is not configured yet. Add OPENAI_API_KEY in Streamlit Cloud → App settings → Secrets. "
                "Meanwhile, use the symptom checker and health library. This app does not provide diagnosis.")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        messages=[{"role":"system","content":(
            "You are MediPredict, a health education assistant for users in India. "
            "Give general information only; never diagnose or prescribe. Use simple English and Hinglish when appropriate. "
            "Keep replies under 160 words. Mention emergency care for red flags. Never claim certainty. "
            "For emergencies, advise calling 112 in India. Do not tell users to stop prescribed medicines."
        )}]
        if history:
            messages.extend(history[-8:])
        messages.append({"role":"user","content":prompt})
        response=client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.3, max_tokens=250)
        return response.choices[0].message.content or "Sorry, I couldn't generate a response."
    except Exception as e:
        return "AI service could not respond. Check your API key and deployment logs. The non-AI tools remain available."

# ---------------------------- Sidebar navigation ----------------------------
with st.sidebar:
    st.markdown("## 🩺 MediPredict")
    st.caption("AI Health Assistant · Educational demo")
    page = st.radio("Navigation", [
        "Dashboard","Symptom Checker","AI Health Chat","Health Tracker",
        "Medicine List","Disease Library","Emergency & First Aid","History","Profile & Export"
    ], label_visibility="collapsed")
    st.divider()
    st.caption("For college demonstration only. Not a medical device.")
    if st.button("Clear this session's data", use_container_width=True):
        for k in ["history","readings","medicines","chat","selected_symptoms"]:
            st.session_state[k] = []
        st.success("Session data cleared.")

st.markdown('<div class="hero"><h1>🩺 MediPredict</h1><p>Your health-education companion — symptom matching, wellness tracking, and AI explanations.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="note"><b>Important:</b> MediPredict is an educational prototype, not a doctor or diagnostic tool. Symptom matches are illustrative and are not medical probabilities. For an emergency in India, call <b>112</b>.</div>', unsafe_allow_html=True)

# ---------------------------- Dashboard ----------------------------
if page == "Dashboard":
    st.subheader(f"Welcome, {st.session_state.profile.get('name') or 'Guest'} 👋")
    st.write(TIPS[date.today().day % len(TIPS)])
    c1,c2,c3,c4=st.columns(4)
    with c1: metric("Symptom checks", len(st.session_state.history))
    with c2: metric("Health readings", len(st.session_state.readings))
    with c3: metric("Medicines listed", len(st.session_state.medicines))
    with c4: metric("Chat messages", sum(1 for x in st.session_state.chat if x["role"]=="user"))
    st.subheader("Quick actions")
    cols=st.columns(3)
    for col,(emoji,title,desc) in zip(cols,[
        ("🩺","Symptom Checker","Explore possible symptom overlaps"),
        ("📈","Health Tracker","Record BMI, blood pressure or glucose"),
        ("🤖","AI Health Chat","Ask general health questions")]):
        with col:
            st.markdown(f"### {emoji} {title}")
            st.write(desc)
    st.subheader("Recent symptom checks")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).head(5), use_container_width=True, hide_index=True)
    else: st.info("No symptom checks yet. Start from Symptom Checker.")

# ---------------------------- Symptom checker ----------------------------
elif page == "Symptom Checker":
    st.subheader("Symptom Checker")
    st.write("Choose the symptoms you are experiencing. The output is a simple educational match, not a diagnosis.")
    selected_labels = st.multiselect("Symptoms", options=list(SYMPTOMS.values()), key="symptom_picker",
                                     placeholder="Search and select symptoms…")
    selected_keys=[k for k,v in SYMPTOMS.items() if v in selected_labels]
    if st.button("Check symptom overlaps", type="primary", disabled=len(selected_keys)<1):
        st.session_state.selected_symptoms=selected_keys
        ranked=predict_conditions(selected_keys)
        record={"Time":datetime.now().strftime("%Y-%m-%d %H:%M"),"Symptoms":", ".join(selected_labels),
                "Top match":ranked[0][1]["name"] if ranked else "No match"}
        st.session_state.history.insert(0,record)
        st.session_state.history=st.session_state.history[:50]
        st.session_state["last_results"]=[{"score":s,"condition":d,"count":n} for s,d,n in ranked]
    if "last_results" in st.session_state and st.session_state.get("selected_symptoms"):
        st.markdown("### Possible symptom overlaps")
        st.caption("The score is a demo ranking only. It is not the chance that you have a condition.")
        for i,item in enumerate(st.session_state.last_results,1):
            d=item["condition"]
            with st.container(border=True):
                st.markdown(f"#### {i}. {d['name']}")
                st.caption(f"{d['severity']} · Demo match score: {item['score']}")
                st.progress(min(100,max(0,int(item["score"]))))
                st.write("**General information / self-care:**")
                for tip in d["tips"]: st.write(f"- {tip}")
                st.info("**When to seek care:** " + d["doctor"])
        if st.button("Explain these matches with AI"):
            context = "Selected symptoms: " + ", ".join(SYMPTOMS[k] for k in st.session_state.selected_symptoms)
            context += ". Educational matches: " + ", ".join(x["condition"]["name"] for x in st.session_state.last_results)
            with st.spinner("Preparing a general explanation…"): st.write(ai_answer(context))

# ---------------------------- AI chat ----------------------------
elif page == "AI Health Chat":
    st.subheader("AI Health Chat")
    st.write("Ask general health-education questions. Do not use this for urgent symptoms or personal diagnosis.")
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    prompt=st.chat_input("For example: What is HbA1c?")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer=ai_answer(prompt, st.session_state.chat[:-1])
            st.markdown(answer)
        st.session_state.chat.append({"role":"assistant","content":answer})

# ---------------------------- Health tracker ----------------------------
elif page == "Health Tracker":
    st.subheader("Health Tracker")
    kind=st.selectbox("Choose a tracker",["BMI","Blood pressure","Blood glucose"])
    with st.form("reading_form"):
        if kind=="BMI":
            height=st.number_input("Height (cm)", min_value=50.0,max_value=250.0,value=170.0,step=0.5)
            weight=st.number_input("Weight (kg)",min_value=10.0,max_value=350.0,value=65.0,step=0.5)
            extra=""
        elif kind=="Blood pressure":
            systolic=st.number_input("Systolic / upper (mmHg)",min_value=50,max_value=300,value=120)
            diastolic=st.number_input("Diastolic / lower (mmHg)",min_value=30,max_value=200,value=80)
            extra=""
        else:
            glucose=st.number_input("Blood glucose (mg/dL)",min_value=1.0,max_value=1000.0,value=100.0,step=1.0)
            extra=st.selectbox("Reading type",["Fasting","After meal"])
        reading_date=st.date_input("Reading date",value=date.today())
        save=st.form_submit_button("Save reading",type="primary")
    if save:
        if kind=="BMI":
            value=round(weight/((height/100)**2),1)
            category="Below usual adult range" if value<18.5 else "Usual adult range" if value<25 else "Above usual adult range"
            detail=f"BMI {value} · {category}"
        elif kind=="Blood pressure":
            value=f"{systolic}/{diastolic}"
            category="Recorded — discuss with clinician if repeatedly high or concerning"
            detail=f"{value} mmHg"
        else:
            value=glucose
            category=f"{extra} reading — interpret with clinical context"
            detail=f"{glucose:g} mg/dL ({extra})"
        st.session_state.readings.insert(0,{"Date":str(reading_date),"Type":kind,"Reading":detail,"Note":category})
        st.success("Reading saved for this session.")
    if st.session_state.readings:
        df=pd.DataFrame(st.session_state.readings)
        st.markdown("### Your readings")
        st.dataframe(df,use_container_width=True,hide_index=True)
        if len(df)>1:
            chosen=st.selectbox("Visualise",df["Type"].unique())
            subset=df[df["Type"]==chosen].copy()
            numeric=[]
            for v in subset["Reading"]:
                try: numeric.append(float(v.split()[1] if chosen=="BMI" else v.split()[0]))
                except: numeric.append(None)
            subset["Value"]=numeric
            subset=subset.dropna(subset=["Value"])
            if not subset.empty: st.line_chart(subset.iloc[::-1].set_index("Date")["Value"])
    else: st.info("No readings saved yet.")

# ---------------------------- Medicine list ----------------------------
elif page == "Medicine List":
    st.subheader("Medicine List & Reminder Planner")
    st.caption("This is a list only; the app does not send push notifications or tell you what medicine to take.")
    with st.form("medicine_form",clear_on_submit=True):
        med_name=st.text_input("Medicine name (as prescribed)")
        med_time=st.time_input("Planned time",value=time(9,0))
        med_notes=st.text_input("Notes (optional)")
        add=st.form_submit_button("Add to list",type="primary")
    if add and med_name.strip():
        st.session_state.medicines.append({"Medicine":med_name.strip(),"Time":med_time.strftime("%H:%M"),"Notes":med_notes,"Added":str(date.today())})
        st.success("Added to your session list.")
    if st.session_state.medicines:
        st.dataframe(pd.DataFrame(st.session_state.medicines),use_container_width=True,hide_index=True)
        if st.button("Remove all listed medicines"):
            st.session_state.medicines=[]
            st.rerun()
    else: st.info("No medicines listed.")

# ---------------------------- Disease library ----------------------------
elif page == "Disease Library":
    st.subheader("Disease & Symptom Learning Library")
    query=st.text_input("Search a topic",placeholder="Try cold, dengue, migraine…")
    found=[d for d in CONDITIONS if query.lower() in d["name"].lower() or any(query.lower() in SYMPTOMS[k].lower() for k in d["symptoms"])]
    for d in found:
        with st.expander(f"{d['name']} · {d['severity']}"):
            st.write("**Common symptom overlaps:** " + ", ".join(SYMPTOMS[k] for k in d["symptoms"]))
            st.write("**General information:**")
            for tip in d["tips"]: st.write(f"- {tip}")
            st.warning(d["doctor"])
    if not found: st.info("No matching topic. Try another search.")

# ---------------------------- Emergency ----------------------------
elif page == "Emergency & First Aid":
    st.subheader("Emergency & First Aid")
    a,b,c=st.columns(3)
    with a: metric("India emergency","112")
    with b: metric("Ambulance","112 / local service")
    with c: metric("Action","Call for help")
    st.warning("For severe breathing difficulty, unconsciousness, stroke signs, severe bleeding, or severe chest pain, call emergency services immediately. Do not wait for an app response.")
    for emoji,title,body in FIRST_AID:
        with st.expander(f"{emoji} {title}"):
            st.write(body)
    st.caption("First-aid information is simplified for a student demo. Follow emergency-dispatcher instructions and certified training.")

# ---------------------------- History ----------------------------
elif page == "History":
    st.subheader("Symptom Check History")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history),use_container_width=True,hide_index=True)
        if st.button("Clear symptom history"):
            st.session_state.history=[]
            st.rerun()
    else: st.info("No symptom-check history in this session.")

# ---------------------------- Profile / export ----------------------------
elif page == "Profile & Export":
    st.subheader("Profile & Export")
    profile=st.session_state.profile
    with st.form("profile_form"):
        name=st.text_input("Display name",value=profile.get("name","Guest"))
        age=st.number_input("Age (optional)",min_value=0,max_value=120,value=int(profile.get("age") or 0))
        blood=st.selectbox("Blood group (optional)",["Not specified","A+","A-","B+","B-","AB+","AB-","O+","O-"],
                           index=(["Not specified","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(profile.get("blood_group")) if profile.get("blood_group") in ["A+","A-","B+","B-","AB+","AB-","O+","O-"] else 0))
        save=st.form_submit_button("Save profile",type="primary")
    if save:
        st.session_state.profile={"name":name.strip() or "Guest","age":age or None,"blood_group":"" if blood=="Not specified" else blood}
        st.success("Profile updated for this session.")
    export={
        "profile":st.session_state.profile,"symptom_history":st.session_state.history,
        "health_readings":st.session_state.readings,"medicine_list":st.session_state.medicines
    }
    st.download_button("⬇ Download my data (JSON)",data=json.dumps(export,indent=2,ensure_ascii=False),
                       file_name="medipredict_data.json",mime="application/json")
    st.caption("Data is stored in the current Streamlit session. This starter version does not provide secure accounts or permanent medical-record storage.")

st.divider()
st.caption("MediPredict · Student project prototype · Educational use only · Not a substitute for professional medical care.")
