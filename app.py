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
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# CSS مخصص يزيل نهائياً الخطوط المتحركة والأشرطة العلوية على الهاتف
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 1. إخفاء كافة الأشرطة العلوية والخطوط المتحركة الخاصة بـ Streamlit (Loading Bar & Decoration) */
    #MainMenu, header, footer {visibility: hidden !important; display: none !important;}
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    div[class*="viewerBadge"], div[class*="stAppHeader"], [data-testid="stStatusWidget"] {
        display: none !important;
    }
    .stProgress > div > div > div > div {
        display: none !important;
    }
    div[data-baseweb="progress-bar"] {
        display: none !important;
    }

    /* 2. ضبط الفواصل والخطوط الأفقية حتى لا تظهر كمسطرة سوداء متحركة */
    hr {
        border: none !important;
        height: 1px !important;
        background-color: #E2E8F0 !important;
        margin: 15px 0 !important;
    }

    /* 3. الاتجاه والخطوط العامة والتوافق مع اللغة العربية */
    html, body, [class*="css"], div, p, span, h1, h2, h3, h4, h5, h6, label {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        word-break: normal !important;
        white-space: normal !important;
        writing-mode: horizontal-tb !important;
    }

    /* 4. إصلاح التجاوب مع الشاشات الصغيرة وتصفية الانضغاط على الجوال */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 0.5rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 10px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 6px !important;
        }
        .instructions-card, .scale-guide-box {
            border-right: none !important;
            border-top: 4px solid #2b6cb0 !important;
            padding: 14px !important;
        }
        .metric-value {
            font-size: 24px !important;
        }
        .metric-title {
            font-size: 14px !important;
        }
        div.stButton > button, div.stFormSubmitButton > button {
            font-size: 16px !important;
            padding: 10px 14px !important;
        }
    }
    
    /* 5. تنسيق الأزرار */
    div.stButton > button, div.stFormSubmitButton > button {
        font-weight: 800 !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[class*="st-key-start_btn"] button, button[data-testid="baseButton-primary"] {
        background-color: #3182CE !important;
        color: #ffffff !important;
        width: 100% !important;
    }

    div[class*="st-key-agree"] button {
        background-color: #38A169 !important;
        color: #ffffff !important;
        width: 100% !important;
    }

    div[class*="st-key-edit"] button {
        background-color: #E53E3E !important;
        color: #ffffff !important;
        width: 100% !important;
    }

    .instructions-card {
        background-color: #f7fafc;
        border-right: 5px solid #2b6cb0;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .instructions-title {
        color: #2b6cb0;
        font-size: 20px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
    }
    .instructions-list {
        font-size: 16px !important;
        color: #2d3748 !important;
        line-height: 1.8 !important;
    }
    
    .big-metric-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 16px !important;
        color: #4a5568 !important;
        font-weight: bold !important;
    }
    .metric-value {
        font-size: 30px !important;
        color: #2b6cb0 !important;
        font-weight: 800 !important;
    }
    
    .status-badge-red {
        background-color: #fff5f5;
        color: #c53030;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #feb2b2;
    }
    .status-badge-green {
        background-color: #f0fff4;
        color: #276749;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #9ae6b4;
    }
    
    .scale-guide-box {
        background-color: #fffaf0;
        border: 1px solid #fbd38d;
        border-right: 5px solid #dd6b20;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

RESPONSES_FILE = "teachers_responses.csv"

# -------------------------------------------------------------
# تحميل بيانات الطلاب الاصطناعية (10 طلاب)
# -------------------------------------------------------------
@st.cache_data
def load_students():
    data = {
        "student_id": [f"S{i:02d}" for i in range(1, 11)],
        "name": [f"طالب {i}" for i in range(1, 11)],
        "quiz_score": [85, 40, 92, 78, 35, 42, 88, 30, 95, 82],
        "attendance_rate": [90, 50, 95, 85, 45, 50, 90, 40, 98, 85],
        "assignments": [88, 45, 90, 80, 40, 48, 85, 35, 92, 80],
        "platform_activity": [82, 55, 91, 75, 50, 40, 89, 45, 94, 84],
        "ai_prediction": [
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "معرض للتعثر الأكاديمي",  # فخ
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "مستقر أكاديمياً",  # فخ
            "مستقر أكاديمياً",
            "معرض للتعثر الأكاديمي",
            "معرض للتعثر الأكاديمي",  # فخ
            "مستقر أكاديمياً",
        ],
    }
    return pd.DataFrame(data)

df_students = load_students()

# تهيئة متطلبات الجلسة (Session State)
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
    st.title("دراسة تجريبية: تقييم قرارات الذكاء الاصطناعي في التعليم")

    st.info("هدف الدراسة: قياس مدى قدرة المدرس على تقييم توصيات الذكاء الاصطناعي واكتشاف الأخطاء إن وجدت.")

    st.markdown(
        """
        <div class="instructions-card">
            <div class="instructions-title">ما المطلوب منك في هذه التجربة؟</div>
            <ol class="instructions-list">
                <li>ستعرض عليك بطاقات لـ <b>10 طلاب</b>.</li>
                <li>كل بطاقة تحتوي على <b>البيانات الأكاديمية للطالب</b> + <b>توصية نظام الذكاء الاصطناعي</b>.</li>
                <li>مهمتك هي قراءة البيانات والتدقيق فيها، ثم اتخاذ قرارك التربوي:
                    <ul>
                        <li><b>أوافق:</b> إذا كان تقييم الذكاء الاصطناعي صحيحاً ومطابقاً لبيانات الطالب.</li>
                        <li><b>أعدل القرار:</b> إذا شعرت أن الذكاء الاصطناعي أخطأ في التقييم وبحاجة للتعديل.</li>
                    </ul>
                </li>
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
        st.subheader("خيارات المعاينة")
        st.session_state.group = st.radio(
            "اختر المجموعة للمعاينة:",
            ["G1", "G2", "G3"],
            format_func=lambda x: {
                "G1": "G1: بدون شرح (الصندوق الأسود)",
                "G2": "G2: شرح عام للنظام",
                "G3": "G3: شرح تفصيلي للطالب (SHAP)",
            }[x],
            index=["G1", "G2", "G3"].index(st.session_state.group),
        )

        if st.button("إعادة بدء التجربة من البداية"):
            st.session_state.consent = False
            st.session_state.current_student = 0
            st.session_state.decisions = {}
            st.session_state.survey_submitted = False
            st.rerun()

    group_code = st.session_state.group
    idx = st.session_state.current_student

    if idx < len(df_students):
        student = df_students.iloc[idx]

        # شارة نصية أنيقة بدلاً من شريط التقدم الرسومي لتفادي أي خط أسود على الهواتف
        st.markdown(
            f'<div style="background-color: #E2E8F0; padding: 6px 12px; border-radius: 6px; font-weight: bold; color: #2D3748; margin-bottom: 12px; text-align: center;">🎯 التقدم: الطالب ({idx + 1} من {len(df_students)})</div>',
            unsafe_allow_html=True
        )

        st.warning(f"اقرأ أرقام الطالب وقارنها بتوصية النظام، ثم اتخذ قرارك في الأسفل.")

        col_data, col_ai = st.columns(2)

        with col_data:
            st.subheader(f"سجل الطالب: {student['name']}")

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f'<div class="big-metric-box"><div class="metric-title">التقييم التكويني</div><div class="metric-value">{student["quiz_score"]}%</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="big-metric-box"><div class="metric-title">تسليم الواجبات</div><div class="metric-value">{student["assignments"]}%</div></div>',
                    unsafe_allow_html=True,
                )

            with m2:
                st.markdown(
                    f'<div class="big-metric-box"><div class="metric-title">نسبة الحضور</div><div class="metric-value">{student["attendance_rate"]}%</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="big-metric-box"><div class="metric-title">نشاط المنصة</div><div class="metric-value">{student["platform_activity"]}%</div></div>',
                    unsafe_allow_html=True,
                )

        with col_ai:
            st.subheader("تقييم وتنبؤ الذكاء الاصطناعي")
            pred_status = student["ai_prediction"]

            if "تعثر" in pred_status or "خطر" in pred_status:
                st.markdown(f'<div class="status-badge-red">{pred_status}</div>', unsafe_allow_html=True)
                st.caption("معنى التقييم: تشير التنبؤات إلى احتمالية انخفاض تحصيل الطالب وتطلبه تدخلاً.")
            else:
                st.markdown(f'<div class="status-badge-green">{pred_status}</div>', unsafe_allow_html=True)
                st.caption("معنى التقييم: يسير الطالب بمعدل جيد يتوافق مع متطلبات النجاح.")

            st.markdown("<br>", unsafe_allow_html=True)

            if group_code == "G1":
                st.info("تنبؤ مباشر: يقدم النظام النتيجة النهائية فقط دون تفاصيل خوارزمية.")

            elif group_code == "G2":
                st.subheader("أهمية المؤشرات العامة للنظام")
                fig, ax = plt.subplots(figsize=(4.5, 2.2))
                features = ["التقييم التكويني", "الحضور", "الواجبات", "نشاط المنصة"]
                importance = [35, 25, 20, 20]
                ax.barh(features, importance, color="#3182bd")
                ax.set_xlabel("الأهمية العامة (%)")
                fig.tight_layout()
                st.pyplot(fig)

            elif group_code == "G3":
                st.subheader("الشرح التفصيلي لقرار هذا الطالب (SHAP)")
                fig, ax = plt.subplots(figsize=(4.5, 2.2))
                features = ["التقييم التكويني", "الحضور", "الواجبات", "المنصة"]

                vals = [
                    (student["quiz_score"] - 50) / 2,
                    (student["attendance_rate"] - 50) / 2,
                    (student["assignments"] - 50) / 2,
                    (student["platform_activity"] - 50) / 2,
                ]
                colors = ["#2ca02c" if v >= 0 else "#d62728" for v in vals]

                ax.barh(features, vals, color=colors)
                ax.axvline(0, color="black", linewidth=1, linestyle="--")
                ax.set_xlabel("تأثير المؤشر مقارنة بحد النجاح 50%")
                fig.tight_layout()
                st.pyplot(fig)

                st.markdown("""
                **كيف تقرأ هذا الرسم؟**
                * **العمود الأخضر (+):** أداء أعلى من حد النجاح (50%) يدعم استقرار الطالب.
                * **العمود الأحمر (-):** أداء أدنى من حد النجاح (50%) يرفع احتمالية التعثر.
                """)

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
    # 3️⃣ الشاشة الثالثة: الاستبيان البعدي والتسجيل الشامل
    # -------------------------------------------------------------
    else:
        st.success("أكملت تقييم الطلاب الـ 10 بنجاح.")
        st.subheader("الاستبيان النهائي (3 دقائق):")

        st.markdown(
            """
            <div class="scale-guide-box">
                <div style="color: #c05621; font-weight: 800; font-size: 17px; margin-bottom: 4px;">دليل التقييم من 1 إلى 5 لمعلم الدراسة:</div>
                <div style="font-size: 15px; font-weight: 700; color: #7b341e; margin: 0; line-height: 1.8;">
                    1 = غير موافق بشدة &nbsp;|&nbsp; 2 = غير موافق &nbsp;|&nbsp; 3 = محايد &nbsp;|&nbsp; 4 = موافق &nbsp;|&nbsp; 5 = موافق بشدة
                </div>
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

        st.markdown("<br><hr>", unsafe_allow_html=True)
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
