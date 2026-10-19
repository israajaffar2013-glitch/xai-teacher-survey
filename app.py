# -*- coding: utf-8 -*-
"""
Educational XAI Decision Support System (EDSS) - Streamlit Application
=====================================================================
منصة التقييم والتنبؤ الأكاديمي والقرار التربوي للمعلمين بذكاء اصطناعي قابل للتفسير
"""

import os
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# -------------------------------------------------------------
# إعدادات الصفحة والواجهة الرسمية
# -------------------------------------------------------------
st.set_page_config(
    page_title="منصة التقييم والتنبؤ الأكاديمي (EDSS)",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# CSS مخصص يزيل نهائياً الخطوط المتحركة والأشرطة العلوية والشارات الحمراء
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 1. إخفاء كافة الأشرطة العلوية والخطوط المتحركة والشارات في Streamlit */
    #MainMenu, header, footer {
        visibility: hidden !important;
        display: none !important;
    }
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    div[class*="viewerBadge"], div[class*="stAppHeader"], [data-testid="stStatusWidget"], [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }
    .stProgress, div[data-baseweb="progress-bar"] {
        display: none !important;
    }

    /* 2. إلغاء أي خط فاصل مسطري أسود */
    hr, [data-testid="stDivider"] {
        display: none !important;
    }

    /* 3. اتجاه النص العربي وتوافق الجوال */
    html, body, [class*="css"], div, p, span, h1, h2, h3, h4, h5, h6, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        word-break: normal !important;
        white-space: normal !important;
    }

    /* 4. تنسيق التجاوب التام مع الجوال */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 12px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 8px !important;
        }
    }

    /* 5. تنسيق الأزرار والبطاقات */
    div.stButton > button, div.stFormSubmitButton > button {
        font-weight: 800 !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        border: none !important;
        width: 100% !important;
    }
    
    div[class*="st-key-start_btn"] button {
        background-color: #3182CE !important;
        color: #ffffff !important;
    }

    div[class*="st-key-agree"] button {
        background-color: #38A169 !important;
        color: #ffffff !important;
    }

    div[class*="st-key-edit"] button {
        background-color: #E53E3E !important;
        color: #ffffff !important;
    }

    .info-card {
        background-color: #F7FAFC;
        border-right: 5px solid #3182CE;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
    }

    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 15px;
        color: #4A5568;
        font-weight: bold;
    }
    .metric-val {
        font-size: 26px;
        color: #2B6CB0;
        font-weight: 800;
    }

    .status-badge-red {
        background-color: #FFF5F5;
        color: #C53030;
        padding: 12px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #FEB2B2;
    }
    .status-badge-green {
        background-color: #F0FFF4;
        color: #276749;
        padding: 12px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #9AE6B4;
    }
    </style>
""",
    unsafe_allow_html=True,
)

RESPONSES_FILE = "teachers_responses.csv"

# -------------------------------------------------------------
# تحميل بيانات الطلاب الاصطناعية (10 طلاب مع فخاخ الاكتشاف)
# -------------------------------------------------------------
@st.cache_data
def load_students():
    data = {
        "student_id": [f"S{i:02d}" for i in range(1, 11)],
        "name": [f"طالب {i}" for i in range(1, 11)],
        "quiz_score": [85, 42, 30, 78, 60, 95, 72, 50, 35, 88],
        "attendance_rate": [90, 50, 40, 85, 70, 98, 80, 60, 45, 92],
        "assignments": [88, 40, 25, 80, 65, 92, 75, 55, 30, 90],
        "platform_activity": [82, 35, 20, 75, 58, 96, 70, 48, 25, 85],
        "ai_prediction": [
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "معرض للتعثر الأكاديمي",  # فخ S03
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "مستقر أكاديمياً",  # فخ S06
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "معرض للتعثر الأكاديمي",  # فخ S09
            "مستقر أكاديمياً",
        ],
    }
    return pd.DataFrame(data)

df_students = load_students()

if "consent" not in st.session_state:
    st.session_state.consent = False
if "group" not in st.session_state:
    st.session_state.group = random.choice(["G1", "G2", "G3"])
if "current_student" not in st.session_state:
    st.session_state.current_student = 0
if "decisions" not in st.session_state:
    st.session_state.decisions = {}
if "survey_submitted" not in st.session_state:
    st.session_state.survey_submitted = False

# -------------------------------------------------------------
# 1️⃣ الشاشة الأولى: الموافقة والتعليمات
# -------------------------------------------------------------
if not st.session_state.consent:
    st.title("🎓 دراسة تجريبية: تقييم قرارات الذكاء الاصطناعي")

    st.markdown(
        """
        <div class="info-card">
            <h3 style="color: #2B6CB0; margin-top:0;">🎯 هدف الدراسة</h3>
            <p style="font-size: 16px; line-height: 1.7; color: #2D3748;">
                قياس مدى قدرة المدرس على تقييم توصيات الذكاء الاصطناعي واكتشاف القرارات غير المبررة إن وجدت لدعم اتخاذ القرار التربوي.
            </p>
        </div>
        <div class="info-card">
            <h4 style="color: #2B6CB0; margin-top:0;">📋 التعليمات:</h4>
            <ol style="font-size: 15px; line-height: 1.8; color: #2D3748; padding-right: 20px;">
                <li>ستعرض عليك بيانات <b>10 طلاب</b> متضمنة السجل الأكاديمي وتوصية الذكاء الاصطناعي.</li>
                <li>المطلوب مراجعة بيانات كل طالب واتخاذ قرارك: <b>أوافق</b> أو <b>أعدل القرار</b>.</li>
                <li>تعبئة استبيان قصير جداً في نهاية التجربة.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        exp_years = st.number_input("سنوات الخبرة في التدريس:", min_value=0, max_value=40, value=5)
    with col2:
        subject = st.selectbox(
            "التخصص / المادة الدراسية:",
            [
                "الحاسوب وتكنولوجيا المعلومات",
                "الرياضيات",
                "العلوم العامة / الفيزياء / الكيمياء / الأحياء",
                "اللغة العربية",
                "اللغة الإنجليزية",
                "المواد الاجتماعية والإنسانية",
                "تخصص آخر",
            ],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("أوافق وابدأ تقييم الطلاب", type="primary", key="start_btn", use_container_width=True):
        st.session_state.consent = True
        st.session_state.exp_years = exp_years
        st.session_state.subject = subject
        st.rerun()

# -------------------------------------------------------------
# 2️⃣ الشاشة الثانية: تقييم الطلاب
# -------------------------------------------------------------
else:
    with st.sidebar:
        st.subheader("خيارات المعاينة (الباحثة)")
        st.session_state.group = st.radio(
            "المجموعة:",
            ["G1", "G2", "G3"],
            format_func=lambda x: {
                "G1": "G1: بدون شرح (الصندوق الأسود)",
                "G2": "G2: شرح عام للنظام",
                "G3": "G3: شرح تفصيلي للطالب (SHAP)",
            }[x],
            index=["G1", "G2", "G3"].index(st.session_state.group),
        )

        if st.button("إعادة بدء التجربة"):
            st.session_state.consent = False
            st.session_state.current_student = 0
            st.session_state.decisions = {}
            st.session_state.survey_submitted = False
            st.rerun()

    group_code = st.session_state.group
    idx = st.session_state.current_student

    if idx < len(df_students):
        student = df_students.iloc[idx]

        # شارة نصية أنيقة للتقدم
        st.markdown(
            f'<div style="background-color: #E2E8F0; padding: 8px; border-radius: 8px; font-weight: bold; color: #2D3748; margin-bottom: 15px; text-align: center;">🎯 الطالب ({idx + 1} من {len(df_students)})</div>',
            unsafe_allow_html=True
        )

        st.info("اقرأ بيانات الطالب وقارنها بتوصية النظام في الأسفل، ثم اتخذ قرارك التربوي.")

        col_data, col_ai = st.columns(2)

        with col_data:
            st.subheader(f"سجل {student['name']}")

            st.markdown(
                f"""
                <div class="metric-card"><div class="metric-label">التقييم التكويني</div><div class="metric-val">{student["quiz_score"]}%</div></div>
                <div class="metric-card"><div class="metric-label">تسليم الواجبات</div><div class="metric-val">{student["assignments"]}%</div></div>
                <div class="metric-card"><div class="metric-label">نسبة الحضور</div><div class="metric-val">{student["attendance_rate"]}%</div></div>
                <div class="metric-card"><div class="metric-label">نشاط المنصة</div><div class="metric-val">{student["platform_activity"]}%</div></div>
                """,
                unsafe_allow_html=True,
            )

        with col_ai:
            st.subheader("تقييم الذكاء الاصطناعي")
            pred_status = student["ai_prediction"]

            if "تعثر" in pred_status or "خطر" in pred_status:
                st.markdown(f'<div class="status-badge-red">{pred_status}</div>', unsafe_allow_html=True)
                st.caption("معنى التقييم: احتمالية تعثر يتطلب التدخل.")
            else:
                st.markdown(f'<div class="status-badge-green">{pred_status}</div>', unsafe_allow_html=True)
                st.caption("معنى التقييم: أداء مستقر يتوافق مع النجاح.")

            st.markdown("<br>", unsafe_allow_html=True)

            if group_code == "G1":
                st.info("تنبؤ مباشر: يقدم النظام النتيجة النهائية فقط دون تفاصيل.")

            elif group_code == "G2":
                st.subheader("أهمية المؤشرات العامة")
                fig, ax = plt.subplots(figsize=(4, 2))
                features = ["التقييم التكويني", "الحضور", "الواجبات", "النشاط"]
                importance = [40, 25, 20, 15]
                ax.barh(features, importance, color="#3182bd")
                ax.set_xlabel("الأهمية (%)")
                fig.tight_layout()
                st.pyplot(fig)

            elif group_code == "G3":
                st.subheader("التفسير التفصيلي (SHAP)")
                fig, ax = plt.subplots(figsize=(4, 2))
                features = ["التقييم التكويني", "الحضور", "الواجبات", "النشاط"]
                vals = [
                    (student["quiz_score"] - 50) / 2,
                    (student["attendance_rate"] - 50) / 2,
                    (student["assignments"] - 50) / 2,
                    (student["platform_activity"] - 50) / 2,
                ]
                colors = ["#2ca02c" if v >= 0 else "#d62728" for v in vals]
                ax.barh(features, vals, color=colors)
                ax.axvline(0, color="black", linewidth=1, linestyle="--")
                ax.set_xlabel("التأثير مقارنة بحد النجاح 50%")
                fig.tight_layout()
                st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("قرارك التربوي كمدرس:")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("أوافق على قرار النظام", key=f"agree_{idx}", use_container_width=True):
                st.session_state.decisions[student["student_id"]] = "أوافق"
                st.session_state.current_student += 1
                st.rerun()

        with c2:
            if st.button("أعدل القرار (الذكاء الاصطناعي مخطئ)", key=f"edit_{idx}", use_container_width=True):
                st.session_state.decisions[student["student_id"]] = "أعدل"
                st.session_state.current_student += 1
                st.rerun()

    # -------------------------------------------------------------
    # 3️⃣ الشاشة الثالثة: الاستبيان النهائي
    # -------------------------------------------------------------
    else:
        st.success("أكملت تقييم الطلاب الـ 10 بنجاح.")
        st.subheader("الاستبيان النهائي:")

        st.markdown(
            """
            <div style="background-color: #FFF2E2; padding: 12px; border-radius: 8px; border-right: 4px solid #DD6B20; margin-bottom: 15px;">
                <b>دليل التقييم (من 1 إلى 5):</b><br>
                1 = غير موافق بشدة | 2 = غير موافق | 3 = محايد | 4 = موافق | 5 = موافق بشدة
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.survey_submitted:
            with st.form("survey_form"):
                st.markdown("#### وضوح الشرح والشفافية")
                ait1 = st.slider("1. كان الشرح المقدم من النظام واضحاً وسهل الفهم:", 1, 5, 3)
                ait2 = st.slider("2. ساعدني الشرح على معرفة سبب اتخاذ النظام لهذا القرار:", 1, 5, 3)

                st.markdown("#### الثقة والقدرة على الاكتشاف")
                tr1 = st.slider("1. أثق في القرارات التي يقدمها هذا النظام كإرشادات مساندة:", 1, 5, 3)
                tr2 = st.slider("2. شعرت بالتأكد عند اتخاذ قرار بتعديل أو موافقة رأي النظام:", 1, 5, 3)

                submitted = st.form_submit_button("إرسال نتائج التجربة")

                if submitted:
                    trap_correct = sum(1 for trap_id in ["S03", "S06", "S09"] if st.session_state.decisions.get(trap_id) == "أعدل")
                    trap_detection_score = round((trap_correct / 3) * 100, 2)

                    correct_answers = {
                        "S01": "أوافق", "S02": "أوافق", "S03": "أعدل", "S04": "أوافق", "S05": "أوافق",
                        "S06": "أعدل", "S07": "أوافق", "S08": "أوافق", "S09": "أعدل", "S10": "أوافق",
                    }
                    total_correct = sum(1 for sid, c_dec in correct_answers.items() if st.session_state.decisions.get(sid) == c_dec)
                    total_accuracy = round((total_correct / 10) * 100, 2)

                    res_data = {
                        "exp_years": [st.session_state.get("exp_years", 0)],
                        "subject": [st.session_state.get("subject", "")],
                        "group": [group_code],
                        "S01_decision": [st.session_state.decisions.get("S01", "")],
                        "S02_decision": [st.session_state.decisions.get("S02", "")],
                        "S03_decision": [st.session_state.decisions.get("S03", "")],
                        "S04_decision": [st.session_state.decisions.get("S04", "")],
                        "S05_decision": [st.session_state.decisions.get("S05", "")],
                        "S06_decision": [st.session_state.decisions.get("S06", "")],
                        "S07_decision": [st.session_state.decisions.get("S07", "")],
                        "S08_decision": [st.session_state.decisions.get("S08", "")],
                        "S09_decision": [st.session_state.decisions.get("S09", "")],
                        "S10_decision": [st.session_state.decisions.get("S10", "")],
                        "trap_detection_score": [trap_detection_score],
                        "total_accuracy": [total_accuracy],
                        "ait_score": [(ait1 + ait2) / 2],
                        "trust_score": [(tr1 + tr2) / 2],
                    }
                    res_df = pd.DataFrame(res_data)

                    if os.path.exists(RESPONSES_FILE):
                        res_df.to_csv(RESPONSES_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
                    else:
                        res_df.to_csv(RESPONSES_FILE, index=False, encoding="utf-8-sig")

                    st.success("تم حفظ إجابات المدرس بنجاح. شكراً لمشاركتك القيمة!")
                    st.session_state.survey_submitted = True
                    st.rerun()
        else:
            st.info("شكراً جزيلاً لمشاركتكم ووقتكم في دعم هذه الدراسة العلمية.")

        with st.expander("لوحة تحميل البيانات (خاص بالباحثة فقط)"):
            pwd = st.text_input("أدخلي رمز الدخول الخاص بالباحثة:", type="password", key="admin_pwd")
            if pwd == "1234":
                st.success("تم التحقق بنجاح")
                if os.path.exists(RESPONSES_FILE):
                    with open(RESPONSES_FILE, "rb") as f:
                        st.download_button(
                            label="تنزيل ملف استجابات المعلمين (CSV)",
                            data=f,
                            file_name=RESPONSES_FILE,
                            mime="text/csv",
                            key="download_csv_btn",
                        )
                else:
                    st.info("لا توجد استجابات مسجلة حتى الآن.")
            elif pwd != "":
                st.error("رمز الدخول غير صحيح")
