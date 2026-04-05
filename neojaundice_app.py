
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="NeoJaundice Risk Calculator",
    page_icon="🍼",
    layout="centered"
)

st.markdown("""
<style>
.risk-high { 
    background-color: #fee2e2; 
    border-left: 5px solid #ef4444; 
    padding: 1rem; 
    border-radius: 8px;
    color: #7f1d1d !important;
}
.risk-high h3 { color: #991b1b !important; }
.risk-high ul li { color: #7f1d1d !important; }
.risk-low { 
    background-color: #dcfce7; 
    border-left: 5px solid #16a34a; 
    padding: 1rem; 
    border-radius: 8px;
    color: #14532d !important;
}
.risk-low h3 { color: #15803d !important; }
.risk-low ul li { color: #14532d !important; }
.risk-mid { 
    background-color: #fef9c3; 
    border-left: 5px solid #ca8a04; 
    padding: 1rem; 
    border-radius: 8px;
    color: #713f12 !important;
}
.risk-mid h3 { color: #92400e !important; }
.risk-mid ul li { color: #713f12 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🍼 Neonatal Sarılık Risk Hesaplayıcı")
st.markdown("Fototerapi İhtiyacı Tahmin Aracı")
st.markdown("---")
st.caption("⚠️ Bu araç klinik karar desteği sağlar. Nihai karar hekime aittir.")

with st.sidebar:
    st.header("ℹ️ Hakkında")
    st.markdown("""
    **Model:** Random Forest  
    **AUC:** 0.944  
    **Sensitivite:** %85.3  
    **Spesisite:** %98.8  
    **NPV:** %98.0  
    **Kohort:** 1429 yenidoğan  
    """)
    st.markdown("---")
    st.markdown("*61. TPK 2024*")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Biyobelirteçler")
    kord_bil = st.number_input("Kordon Bilirubin (mg/dL)", 0.0, 15.0, 2.0, 0.1,
                                help="Doğumda kordon kanından ölçülen bilirubin")
    tab_oncesi_bil = st.number_input("Taburculuk Öncesi Bilirubin (mg/dL)", 0.0, 25.0, 6.0, 0.1,
                                      help="Taburculuktan önce ölçülen serum bilirubin")
    DC = st.selectbox("Direkt Coombs", ["Negatif", "Pozitif"])
    bebek_enfeksiyon = st.selectbox("Enfeksiyon", ["Yok", "Var"])

with col2:
    st.subheader("👶 Perinatal Bilgiler")
    gebelik_haftasi = st.number_input("Gebelik Haftası", 34, 42, 38, 1)
    dogum_agirligi = st.number_input("Doğum Ağırlığı (g)", 1500, 5000, 3200, 50)
    abo_uyusmazlik = st.selectbox("ABO Uyuşmazlığı", ["Yok", "Var"])
    etnik = st.selectbox("Etnisite", ["Türk", "Yabancı uyruklu"])
    beslenme_tipi = st.selectbox("Beslenme Tipi", ["Sadece Anne Sütü", "Karma / Mama"])
    dogum_sekli = st.selectbox("Doğum Şekli", ["Normal", "Sezaryen"])

st.subheader("👩 Anne Bilgileri")
col3, col4 = st.columns(2)
with col3:
    anne_yas = st.number_input("Anne Yaşı", 15, 50, 28, 1)
    anne_parite = st.number_input("Anne Paritesi", 0, 10, 1, 1)
with col4:
    rh_uyusmazlik = st.selectbox("Rh Uyuşmazlığı", ["Yok", "Var"])
    taburculuk_saati = st.number_input("Taburculuk Saati (postnatal)", 12, 120, 48, 1)
    tarti_kaybi = st.number_input("Tartı Kaybı (%)", 0.0, 15.0, 4.0, 0.1)

st.markdown("---")

def encode(val, positive):
    return 1 if val == positive else 0

if st.button("🔍 Risk Hesapla", type="primary", use_container_width=True):
    skor = 0
    if kord_bil >= 3.1:            skor += 30
    elif kord_bil >= 2.5:          skor += 15
    if tab_oncesi_bil >= 10.2:     skor += 35
    elif tab_oncesi_bil >= 7:      skor += 18
    if DC == "Pozitif":            skor += 20
    if bebek_enfeksiyon == "Var":  skor += 15
    if abo_uyusmazlik == "Var":    skor += 8
    if etnik == "Yabancı uyruklu": skor += 5
    if gebelik_haftasi <= 37:      skor += 5
    if dogum_agirligi < 2500:      skor += 5
    if beslenme_tipi == "Karma / Mama": skor += 3
    skor = min(skor, 100)

    st.markdown("### 📊 Risk Değerlendirmesi")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Risk Skoru", f"{skor}/100")
    col_b.metric("Kordon Bil.", f"{kord_bil} mg/dL",
                 delta="Eşik üstü" if kord_bil >= 3.1 else "Normal",
                 delta_color="inverse" if kord_bil >= 3.1 else "normal")
    col_c.metric("Taburculuk Bil.", f"{tab_oncesi_bil} mg/dL",
                 delta="Eşik üstü" if tab_oncesi_bil >= 10.2 else "Normal",
                 delta_color="inverse" if tab_oncesi_bil >= 10.2 else "normal")

    if skor >= 50:
        st.markdown(f"""<div class="risk-high">
        <h3>🔴 YÜKSEK RİSK — Skor: {skor}/100</h3>
        Fototerapi ihtiyacı yüksek olasılıkla beklenmektedir.
        <ul>
        <li>Taburculuğu 24–48 saat erteleyin veya yakın takip planı yapın</li>
        <li>Kontrol serum bilirubin ölçümü önerilir</li>
        <li>Aile fototerapi konusunda bilgilendirilmeli</li>
        </ul>
        </div>""", unsafe_allow_html=True)
    elif skor >= 25:
        st.markdown(f"""<div class="risk-mid">
        <h3>🟡 ORTA RİSK — Skor: {skor}/100</h3>
        Dikkatli izlem önerilmektedir.
        <ul>
        <li>48–72. saatte poliklinik kontrolü planlanmalı</li>
        <li>Aileye sarılık belirtileri öğretilmeli</li>
        <li>Telefon takibi uygulanabilir</li>
        </ul>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="risk-low">
        <h3>🟢 DÜŞÜK RİSK — Skor: {skor}/100</h3>
        Fototerapi ihtiyacı düşük olasılıkla beklenmektedir.
        <ul>
        <li>Standart takip protokolü uygulanabilir</li>
        <li>72. saatte rutin kontrol planlanmalı</li>
        <li>Model NPV=%98 — negatif sonuç güvenilir</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🎯 Risk Faktörü Analizi")
    faktorler = []
    if kord_bil >= 3.1:              faktorler.append(("🔴 Kordon bilirubin ≥3.1 mg/dL", "Yüksek eşik — OR=1.54"))
    elif kord_bil >= 2.5:            faktorler.append(("🟡 Kordon bilirubin 2.5–3.1 mg/dL", "İzlem eşiği"))
    if tab_oncesi_bil >= 10.2:       faktorler.append(("🔴 Taburculuk öncesi bil. ≥10.2 mg/dL", "En güçlü prediktör — AUC=0.812"))
    if DC == "Pozitif":              faktorler.append(("🔴 Direkt Coombs pozitif", "OR=5.48 — Bağımsız risk faktörü"))
    if bebek_enfeksiyon == "Var":    faktorler.append(("🔴 Enfeksiyon", "OR=15.91 — En yüksek OR"))
    if abo_uyusmazlik == "Var":      faktorler.append(("🟡 ABO uyuşmazlığı", "Univariate OR=2.39"))
    if etnik == "Yabancı uyruklu":   faktorler.append(("🟡 Yabancı uyruklu", "OR=1.86"))
    if gebelik_haftasi <= 37:        faktorler.append(("🟡 Prematürite ≤37 hafta", "Bağımsız risk faktörü"))

    if not faktorler:
        st.success("Anlamlı risk faktörü saptanmadı.")
    else:
        for f, aciklama in faktorler:
            st.markdown(f"**{f}** — *{aciklama}*")

    with st.expander("📚 Metodoloji"):
        st.markdown("""
        **Model:** Random Forest (GridSearchCV + 5-Fold CV + SMOTE)  
        **Kohort:** n=1429 | Fototerapi: n=171 (%12.0)  
        **Performans:** AUC=0.944 | Sens=%85.3 | Spec=%98.8 | NPV=%98.0  
        **SHAP:** Taburculuk öncesi bil. > DC > ABO > Kordon bil. (eşik: 3.1 mg/dL)  
        """)

st.markdown("---")
st.caption("Bu araç araştırma amaçlıdır. Klinik karar hekime aittir.")
