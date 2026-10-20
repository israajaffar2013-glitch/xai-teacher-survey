# -*- coding: utf-8 -*-
"""
Educational XAI Decision Support System (EDSS) - Streamlit Application
=====================================================================
أثر توظيف نماذج الذكاء الاصطناعي القابلة للتفسير على شفافية نظم دعم القرار التعليمي لمدرسي المرحلة الثانوية
"""

import os
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -------------------------------------------------------------
# إعدادات الصفحة والواجهة الرسمية
# -------------------------------------------------------------
st.set_page_config(
    page_title="أثر توظيف نماذج الذكاء الاصطناعي القابلة للتفسير على شفافية نظم دعم القرار التعليمي لمدرسي المرحلة الثانوية",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# CSS مخصص لتحسين المظهر والقطع مع أي رموز تعبيرية
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, header, footer {
        visibility: hidden !important;
        display: none !important;
    }
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"] {
        display: none !important;
    }

    html, body, [class*="css"], div, p, span, h1, h2, h3, h4, h5, h6, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 14px;
        color: #4A5568;
        font-weight: bold;
    }
    .metric-value {
        font-size: 22px;
        color: #1A365D;
        font-weight: 800;
    }

    .status-badge-red {
        background-color: #FFF5F5;
        color: #9B2C2C;
        padding: 12px;
        border-radius: 6px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #FEB2B2;
    }
    .status-badge-green {
        background-color: #F0FFF4;
        color: #22543D;
        padding: 12px;
        border-radius: 6px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #9AE6B4;
    }

    .info-card {
        background-color: #F7FAFC;
        border-right: 5px solid #2B6CB0;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 16px;
    }

    div.stButton > button {
        font-weight: 800 !important;
        font-size: 18px !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        border: none !important;
        width: 100% !important;
    }
    div[class*="st-key-start_btn"] button {
        background-color: #2B6CB0 !important;
        color: #ffffff !important;
    }
    div[class*="st-key-agree"] button {
        background-color: #2F855A !important;
        color: #ffffff !important;
    }
    div[class*="st-key-edit"] button {
        background-color: #C53030 !important;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

RESPONSES_FILE = "teachers_responses.csv"

# -------------------------------------------------------------
# بيانات الطلاب الاصطناعية (أسماء حيادية دون الإفصاح عن الفخ)
# -------------------------------------------------------------
STUDENTS_DATA = [
    {
        "id": "S01",
        "name": "الطالب (01)",
        "formative_score": 85,
        "assignments": 90,
        "attendance_rate": 95,
        "platform_activity": 88,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": False,
        "contributions": {"التقييم التكويني": 35, "نسبة الحضور": 30, "الواجبات": 20, "نشاط المنصة": 15},
        "shap_text": "مساهمة إيجابية مرتفعة لدرجة التقييم التكويني الحالية (85%) والحضور الممتاز (95%) تدعم استقرار مستوى الطالب.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S02",
        "name": "الطالب (02)",
        "formative_score": 42,
        "assignments": 50,
        "attendance_rate": 60,
        "platform_activity": 35,
        "ai_prediction": "معرض للتعثر الأكاديمي",
        "is_trap": False,
        "contributions": {"التقييم التكويني": -28, "نشاط المنصة": -22, "نسبة الحضور": -15, "الواجبات": -10},
        "shap_text": "انخفاض التقييم التكويني (42%) وضعف النشاط بالمنصة (35%) هما المساهمان الأكبر في التنبؤ بالتعثر الأكاديمي.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S03",
        "name": "الطالب (03)",
        "formative_score": 30,
        "assignments": 25,
        "attendance_rate": 40,
        "platform_activity": 20,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": True,
        "contributions": {"نشاط المنصة": 40, "نسبة الحضور": 25, "الواجبات": 15, "التقييم التكويني": 10},
        "shap_text": "يشير التفسير الداخلي للنظام إلى اعتماد التوصية بالاستقرار على مؤشرات تفاعل المنصة.",
        "ground_truth": "أعدل"
    },
    {
        "id": "S04",
        "name": "الطالب (04)",
        "formative_score": 78,
        "assignments": 82,
        "attendance_rate": 88,
        "platform_activity": 80,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": False,
        "contributions": {"تسليم الواجبات": 30, "نسبة الحضور": 28, "التقييم التكويني": 22, "نشاط المنصة": 20},
        "shap_text": "الانتظام في تسليم الواجبات (82%) مع نسبة الحضور (88%) يسهمان بشكل رئيسي في التوصية بالاستقرار.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S05",
        "name": "الطالب (05)",
        "formative_score": 48,
        "assignments": 45,
        "attendance_rate": 55,
        "platform_activity": 40,
        "ai_prediction": "معرض للتعثر الأكاديمي",
        "is_trap": False,
        "contributions": {"التقييم التكويني": -20, "الواجبات": -18, "نسبة الحضور": -12, "نشاط المنصة": -10},
        "shap_text": "تقارب نتائج التقييم التكويني (48%) والواجبات (45%) من الحد الحرج ينقل الطالب لفئة خطر التعثر.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S06",
        "name": "الطالب (06)",
        "formative_score": 92,
        "assignments": 95,
        "attendance_rate": 90,
        "platform_activity": 85,
        "ai_prediction": "معرض للتعثر الأكاديمي",
        "is_trap": True,
        "contributions": {"نشاط المنصة": -35, "نسبة الحضور": -25, "الواجبات": -20, "التقييم التكويني": -10},
        "shap_text": "يعزز نظام التفسير التوصية بالتعثر بناءً على وزن تأثير التفاعل الرقمي المحسوب بالنموذج.",
        "ground_truth": "أعدل"
    },
    {
        "id": "S07",
        "name": "الطالب (07)",
        "formative_score": 72,
        "assignments": 75,
        "attendance_rate": 80,
        "platform_activity": 70,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": False,
        "contributions": {"نسبة الحضور": 25, "الواجبات": 25, "التقييم التكويني": 25, "نشاط المنصة": 25},
        "shap_text": "توازن الأداء عبر كافة المؤشرات فوق مستوى 70% يضمن استقرار المستوى الأكاديمي.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S08",
        "name": "الطالب (08)",
        "formative_score": 45,
        "assignments": 50,
        "attendance_rate": 50,
        "platform_activity": 30,
        "ai_prediction": "معرض للتعثر الأكاديمي",
        "is_trap": False,
        "contributions": {"نشاط المنصة": -30, "نسبة الحضور": -20, "التقييم التكويني": -15, "الواجبات": -10},
        "shap_text": "ضعف التفاعل الرقمي بالمنصة (30%) والحضور (50%) يمثلان العامل التفسيري الأبرز للتعثر.",
        "ground_truth": "أوافق"
    },
    {
        "id": "S09",
        "name": "الطالب (09)",
        "formative_score": 35,
        "assignments": 30,
        "attendance_rate": 45,
        "platform_activity": 25,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": True,
        "contributions": {"نسبة الحضور": 35, "نشاط المنصة": 30, "الواجبات": 15, "التقييم التكويني": 10},
        "shap_text": "يعتمد التفسير المحلي للنظام على القيمة الترجيحية للحضور في تصنيف الطالب كمستقر.",
        "ground_truth": "أعدل"
    },
    {
        "id": "S10",
        "name": "الطالب (10)",
        "formative_score": 88,
        "assignments": 92,
        "attendance_rate": 96,
        "platform_activity": 90,
        "ai_prediction": "مستقر أكاديمياً",
        "is_trap": False,
        "contributions": {"نسبة الحضور": 35, "الواجبات": 30, "التقييم التكويني": 25, "نشاط المنصة": 10},
        "shap_text": "التفوق العالي في الحضور (96%) والواجبات (92%) يدفعان التوصية لأعلى درجات الاستقرار الأكاديمي.",
        "ground_truth": "أوافق"
    }
]

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
# لوحة التحكم للباحثة
# -------------------------------------------------------------
def render_researcher_controls(key_prefix="sidebar"):
    st.markdown("### لوحة المعاينة والتحكم (خاص بالباحثة)")
    
    selected_g = st.radio(
        "اختيار الشاشة / المجموعة التجريبية:",
        ["G1", "G2", "G3"],
        format_func=lambda x: {
            "G1": "الشاشة الأولى (G1): قرار مجرد دون أي شرح (الصندوق الأسود)",
            "G2": "الشاشة الثانية (G2): قرار + شرح عام لنظام الذكاء الاصطناعي",
            "G3": "الشاشة الثالثة (G3): قرار + مخطط وتفسير تفصيلي للطالب (SHAP)",
        }[x],
        index=["G1", "G2", "G3"].index(st.session_state.group),
        key=f"{key_prefix}_group_selector_radio"
    )
    st.session_state.group = selected_g

    if st.button("إعادة بدء التجربة وتعيين مجموعة جديدة عشوائياً", key=f"{key_prefix}_reset_exp_btn"):
        st.session_state.consent = False
        st.session_state.current_student = 0
        st.session_state.decisions = {}
        st.session_state.survey_submitted = False
        st.session_state.group = random.choice(["G1", "G2", "G3"])
        st.rerun()

with st.sidebar:
    render_researcher_controls(key_prefix="sb")

# -------------------------------------------------------------
# 1️⃣ الشاشة الأولى: الموافقة والتعليمات
# -------------------------------------------------------------
if not st.session_state.consent:
    st.title("دراسة تجريبية: أثر توظيف نماذج الذكاء الاصطناعي القابلة للتفسير على شفافية نظم دعم القرار التعليمي لمدرسي المرحلة الثانوية")

    st.markdown(
        """
        <div class="info-card">
            <h3 style="color: #1A365D; margin-top:0;">هدف الدراسة</h3>
            <p style="font-size: 16px; line-height: 1.7; color: #2D3748;">
                قياس مدى أثر توظيف نماذج الذكاء الاصطناعي القابلة للتفسير على تعزيز شفافية نظم دعم القرار التعليمي، وتمكين مدرسي المرحلة الثانوية من تقييم التوصيات الأكاديمية واكتشاف القرارات غير المبررة.
            </p>
        </div>
        <div class="info-card">
            <h4 style="color: #1A365D; margin-top:0;">التعليمات الرسمية:</h4>
            <ol style="font-size: 15px; line-height: 1.8; color: #2D3748; padding-right: 20px;">
                <li>ستعرض عليك بيانات <b>10 طلاب</b> متضمنة السجل الأكاديمي وتوصية الذكاء الاصطناعي.</li>
                <li>المطلوب مراجعة بيانات كل طالب ثم اتخاذ قرارك التربوي: <b>أوافق</b> أو <b>أعدل القرار</b>.</li>
                <li>تعبئة استبيان قصير في نهاية التجربة.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        exp_years = st.number_input("سنوات الخبرة في التدريس الثانوي:", min_value=0, max_value=40, value=5)
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

    with st.expander("لوحة المعاينة والتحكم للباحثة (G1, G2, G3)"):
        render_researcher_controls(key_prefix="exp_welcome")

# -------------------------------------------------------------
# 2️⃣ الشاشة الثانية: تقييم الطلاب
# -------------------------------------------------------------
else:
    group_code = st.session_state.group
    idx = st.session_state.current_student

    if idx < len(STUDENTS_DATA):
        student = STUDENTS_DATA[idx]

        st.markdown(
            f'<div style="background-color: #E2E8F0; padding: 10px; border-radius: 6px; font-weight: bold; color: #1A202C; margin-bottom: 15px; text-align: center;">حالة الطالب ({idx + 1} من {len(STUDENTS_DATA)}) | المجموعة: ({group_code})</div>',
            unsafe_allow_html=True
        )

        st.info("يرجى قراءة بيانات الطالب ومقارنتها بتوصية النظام أدناه، ثم اتخاذ القرار التربوي المناسب.")

        col_data, col_ai = st.columns(2)

        with col_data:
            st.subheader(f"سجل {student['name']}")

            st.markdown(
                f"""
                <div class="metric-box"><div class="metric-title">التقييم التكويني</div><div class="metric-value">{student["formative_score"]}%</div></div>
                <div class="metric-box"><div class="metric-title">تسليم الواجبات</div><div class="metric-value">{student["assignments"]}%</div></div>
                <div class="metric-box"><div class="metric-title">نسبة الحضور</div><div class="metric-value">{student["attendance_rate"]}%</div></div>
                <div class="metric-box"><div class="metric-title">نشاط المنصة</div><div class="metric-value">{student["platform_activity"]}%</div></div>
                """,
                unsafe_allow_html=True,
            )

        with col_ai:
            st.subheader("توصية الذكاء الاصطناعي")
            pred_status = student["ai_prediction"]

            if "تعثر" in pred_status or "خطر" in pred_status:
                st.markdown(f'<div class="status-badge-red">{pred_status}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-badge-green">{pred_status}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -----------------------------------------------------
            # الشاشات الثلاث
            # -----------------------------------------------------
            if group_code == "G1":
                st.warning("تنبؤ مجرد (G1): يقدم النظام القرار النهائي فقط بدون أي تفاصيل أو شرح إضافي.")

            elif group_code == "G2":
                st.subheader("شرح عام عن معايير النظام (G2)")
                st.info("أهمية المؤشرات العامة في نموذج الذكاء الاصطناعي:\n- درجة التقييم التكويني: 40%\n- نسبة الحضور: 30%\n- تسليم الواجبات: 20%\n- نشاط المنصة الرقمية: 10%")
                
                fig, ax = plt.subplots(figsize=(4, 2.2))
                features = ["التقييم التكويني", "نسبة الحضور", "الواجبات", "نشاط المنصة"]
                importance = [40, 30, 20, 10]
                ax.barh(features, importance, color="#2B6CB0")
                ax.set_xlabel("نسبة الأهمية العامة (%)", fontsize=9)
                ax.tick_params(axis='both', labelsize=8)
                fig.tight_layout()
                st.pyplot(fig)

            elif group_code == "G3":
                st.subheader("التفسير التفصيلي الفردي للطالب (G3 - SHAP)")
                
                # رسم مخطط بياني لمساهمة مؤشرات هذا الطالب تحديداً
                fig, ax = plt.subplots(figsize=(4.2, 2.4))
                contrib_dict = student["contributions"]
                feats = list(contrib_dict.keys())
                vals = list(contrib_dict.values())
                colors = ["#2F855A" if v > 0 else "#C53030" for v in vals]
                
                ax.barh(feats, vals, color=colors)
                ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
                ax.set_xlabel("تأثير المؤشر على القرار الفردي (SHAP)", fontsize=8)
                ax.tick_params(axis='both', labelsize=8)
                fig.tight_layout()
                st.pyplot(fig)

                st.success(f"ملاحظة التفسير الفردي لـ {student['name']}:\n\n{student['shap_text']}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("القرار التربوي للمعلم:")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("أوافق على قرار النظام", key=f"agree_{idx}", use_container_width=True):
                st.session_state.decisions[student["id"]] = "أوافق"
                st.session_state.current_student += 1
                st.rerun()

        with c2:
            if st.button("أعدل القرار (الذكاء الاصطناعي مخطئ)", key=f"edit_{idx}", use_container_width=True):
                st.session_state.decisions[student["id"]] = "أعدل"
                st.session_state.current_student += 1
                st.rerun()

        with st.expander("لوحة المعاينة والتحكم للباحثة (تغيير G1, G2, G3)"):
            render_researcher_controls(key_prefix="exp_eval")

    # -------------------------------------------------------------
    # 3️⃣ الشاشة الثالثة: الاستبيان النهائي
    # -------------------------------------------------------------
    else:
        st.success("أكملت تقييم الطلاب الـ 10 بنجاح.")
        st.subheader("الاستبيان النهائي:")

        st.markdown(
            """
            <div style="background-color: #EDF2F7; padding: 12px; border-radius: 6px; border-right: 4px solid #4A5568; margin-bottom: 15px;">
                <b>دليل التقييم (من 1 إلى 5):</b><br>
                1 = غير موافق بشدة | 2 = غير موافق | 3 = محايد | 4 = موافق | 5 = موافق بشدة
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.survey_submitted:
            with st.form("survey_form"):
                st.markdown("#### وضوح الشرح والشفافية")
                ait1 = st.slider("1. كان الشرح والمخطط المقدم من النظام واضحاً وسهل الفهم:", 1, 5, 3)
                ait2 = st.slider("2. ساعدني التفسير على معرفة سبب اتخاذ النظام لهذا القرار:", 1, 5, 3)

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

                    st.success("تم حفظ إجابات المدرس بنجاح. شكراً لمشاركتك القيمة.")
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

