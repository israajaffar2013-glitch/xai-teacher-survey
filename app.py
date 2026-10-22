# -*- coding: utf-8 -*-
"""
Educational XAI Decision Support System (EDSS) - Streamlit Application
=====================================================================
دراسة تجريبية: أثر توظيف نماذج الذكاء الاصطناعي القابلة للتفسير على شفافية نظم دعم القرار التعليمي لمدرسي المرحلة الثانوية
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
    page_title="منصة دعم القرار التعليمي بالذكاء الاصطناعي",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# CSS مخصص لإخفاء عناصر Streamlit العلوية والسفلية والرموز تماماً
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
    [data-testid="stToolbar"] {display: none !important; visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important; visibility: hidden !important;}
    [data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
    #stDecoration {display: none !important; visibility: hidden !important;}
    .styles_viewerBadge__1yB5G {display: none !important; visibility: hidden !important;}
    button[title="View source"] {display: none !important; visibility: hidden !important;}
    a[href*="github.com"] {display: none !important; visibility: hidden !important;}
    
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
        padding: 14px;
        border-radius: 8px;
        font-size: 19px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #FEB2B2;
    }
    .status-badge-green {
        background-color: #F0FFF4;
        color: #22543D;
        padding: 14px;
        border-radius: 8px;
        font-size: 19px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #9AE6B4;
    }

    .info-card {
        background-color: #F7FAFC;
        border-right: 5px solid #2B6CB0;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 18px;
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
# بيانات الطلاب الـ 10 الاصطناعية
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
        "contributions": {"التقويم التكويني": 35, "نسبة الحضور": 30, "تسليم الواجبات": 20, "نشاط المنصة": 15},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن ارتفاع درجات التقويم التكويني (85%) ونسبة الحضور الممتازة (95%) هما العاملان الرئيسيان اللذان دفعت بهما الخوارزمية لتصنيف الطالب كـ 'مستقر أكاديمياً'.",
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
        "contributions": {"التقويم التكويني": -28, "نشاط المنصة": -22, "نسبة الحضور": -15, "تسليم الواجبات": -10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن تدني نتائج التقويم التكويني (42%) وانخفاض التفاعل بالمنصة (35%) شكلا مساهمة سلبية حادة أدت لتنبؤ النموذج بخطر التعثر الأكاديمي.",
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
        "contributions": {"نشاط المنصة": 40, "نسبة الحضور": 25, "تسليم الواجبات": 15, "التقويم التكويني": 10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن الخوارزمية أعطت وزناً إيجابياً غير مبرر (+40%) لعدد التفاعلات السطحية بالمنصة، مما أدى لانخداع النموذج وتصنيف الطالب كـ 'مستقر أكاديمياً'، متجاهلةً التراجع الحاد والخطير في التقويم التكويني (30%) والواجبات (25%).",
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
        "contributions": {"تسليم الواجبات": 30, "نسبة الحضور": 28, "التقويم التكويني": 22, "نشاط المنصة": 20},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن الانتظام العالي في تسليم الواجبات (82%) والمواظبة على الحضور (88%) يسهمان بشكل إيجابي مباشر في توصية الاستقرار الأكاديمي.",
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
        "contributions": {"التقويم التكويني": -20, "تسليم الواجبات": -18, "نسبة الحضور": -12, "نشاط المنصة": -10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن اقتراب نتائج التقويم التكويني (48%) والواجبات (45%) من الحد الحرج أدى لتأثير سلبي تراكمي ينقل الطالب لفئة التعثر.",
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
        "contributions": {"نشاط المنصة": -35, "نسبة الحضور": -25, "تسليم الواجبات": -20, "التقويم التكويني": -10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن الخوارزمية احتسبت انخفاض عدد المشاهدات الرقمية كعامل خطر سلبي حاد (-35%)، مما طغى بشكل خاطئ على التفوق والتميز الدراسي الحقيقي للطالب في التقويم التكويني (92%) والواجبات (95%)، فأصدرت توصية خاطئة بالتعثر.",
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
        "contributions": {"نسبة الحضور": 25, "تسليم الواجبات": 25, "التقويم التكويني": 25, "نشاط المنصة": 25},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن التوازن الإيجابي المعتدل عبر جميع المعايير (فوق 70%) يدعم استقرار المستوى الأكاديمي للطالب.",
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
        "contributions": {"نشاط المنصة": -30, "نسبة الحضور": -20, "التقويم التكويني": -15, "تسليم الواجبات": -10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن انخفاض التفاعل الرقمي بالمنصة (30%) وضعف الحضور (50%) هما العاملان السلبيان الأبرز لصدور قرار التعثر.",
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
        "contributions": {"نسبة الحضور": 35, "نشاط المنصة": 30, "تسليم الواجبات": 15, "التقويم التكويني": 10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن الخوارزمية اعتمدت بشكل خاطئ على نسبة الحضور والتصفح المظهرية (+35%) لتصنيف الطالب كـ 'مستقر أكاديمياً'، وهمّشت الرسوب والتراجع الفعلي في درجات التقويم التكويني (35%).",
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
        "contributions": {"نسبة الحضور": 35, "تسليم الواجبات": 30, "التقويم التكويني": 25, "نشاط المنصة": 10},
        "shap_text": "تحليل SHAP الفردي: أظهر التحليل أن نسبة الحضور العالية (96%) والتميز بالواجبات (92%) يقدمان مساهمة إيجابية قوية تضمن الاستقرار الأكاديمي.",
        "ground_truth": "أوافق"
    }
]

# تهيئة حالة الجلسة (Session State)
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "group" not in st.session_state:
    st.session_state.group = random.choice(["G1", "G2", "G3"])
if "current_student" not in st.session_state:
    st.session_state.current_student = 0
if "decisions" not in st.session_state:
    st.session_state.decisions = {}
if "survey_submitted" not in st.session_state:
    st.session_state.survey_submitted = False

query_params = st.query_params
is_researcher_mode = (query_params.get("admin") in ["1234", "true"]) or (query_params.get("mode") == "researcher")

def on_group_radio_change(key_name):
    if key_name in st.session_state:
        st.session_state.group = st.session_state[key_name]

# -------------------------------------------------------------
# 1️⃣ الشاشة الأولى: الموافقة والتعليمات (step == 'welcome')
# -------------------------------------------------------------
if st.session_state.step == "welcome":
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
                <li>تعبئة استبيان قصير في نهاية التجربة لقياس الشفافية والدقة والثقة.</li>
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
        st.session_state.exp_years = exp_years
        st.session_state.subject = subject
        st.session_state.current_student = 0
        st.session_state.step = "evaluating"
        st.rerun()

    if is_researcher_mode:
        st.markdown("---")
        st.subheader("لوحة تحكم الباحثة (تظهر لكِ فقط عند استخدام الرابط الخاص):")
        radio_key = "admin_group_welcome"
        if radio_key not in st.session_state or st.session_state[radio_key] != st.session_state.group:
            st.session_state[radio_key] = st.session_state.group

        st.radio(
            "اختيار المجموعة للتجربة والمعاينة المباشرة:",
            ["G1", "G2", "G3"],
            format_func=lambda x: {
                "G1": "الشاشة الأولى (G1): قرار مجرد دون شرح (الصندوق الأسود)",
                "G2": "الشاشة الثانية (G2): قرار + شرح عام لنظام الذكاء الاصطناعي (مخطط دائر الأهمية الكلية)",
                "G3": "الشاشة الثالثة (G3): قرار + مخطط وتفسير تفصيلي فردي للطالب (SHAP الانحرافي)",
            }[x],
            key=radio_key,
            on_change=on_group_radio_change,
            args=(radio_key,)
        )
        if st.button("إعادة تعيين وبدء تجربة جديدة", key="reset_welcome_admin"):
            st.session_state.step = "welcome"
            st.session_state.current_student = 0
            st.session_state.decisions = {}
            st.session_state.survey_submitted = False
            st.session_state.group = random.choice(["G1", "G2", "G3"])
            st.rerun()

# -------------------------------------------------------------
# 2️⃣ الشاشة الثانية: تقييم الطلاب (step == 'evaluating')
# -------------------------------------------------------------
elif st.session_state.step == "evaluating":
    group_code = st.session_state.group
    idx = st.session_state.current_student

    if idx >= len(STUDENTS_DATA):
        st.session_state.step = "survey"
        st.rerun()

    student = STUDENTS_DATA[idx]

    st.markdown(
        f'<div style="background-color: #E2E8F0; padding: 10px; border-radius: 6px; font-weight: bold; color: #1A202C; margin-bottom: 15px; text-align: center;">حالة الطالب ({idx + 1} من {len(STUDENTS_DATA)})</div>',
        unsafe_allow_html=True
    )
    st.progress((idx + 1) / len(STUDENTS_DATA))

    st.info("يرجى قراءة بيانات الطالب ومقارنتها بتوصية النظام أدناه، ثم اتخاذ القرار التربوي المناسب.")

    col_data, col_ai = st.columns(2)

    with col_data:
        st.subheader(f"سجل {student['name']}")

        st.markdown(
            f"""
            <div class="metric-box"><div class="metric-title">التقويم التكويني (الأنشطة والاختبارات المستمرة)</div><div class="metric-value">{student["formative_score"]}%</div></div>
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

        if group_code == "G1":
            st.warning("تنبؤ مجرد (G1): يقدم النظام القرار النهائي فقط بدون أي تفاصيل أو شرح إضافي.")

        elif group_code == "G2":
            st.subheader("شرح عام كلي للنظام (G2 - Global Importance)")
            st.info("المخطط أدناه يوضح وزن الأهمية النسبية العامة التي يعتمد عليها نموذج الذكاء الاصطناعي ككل لجميع الطلاب:")
            
            fig, ax = plt.subplots(figsize=(3.8, 2.6))
            labels = ["التقويم التكويني", "نسبة الحضور", "تسليم الواجبات", "نشاط المنصة"]
            sizes = [40, 25, 20, 15]
            colors = ["#1A365D", "#2B6CB0", "#4299E1", "#90CDF4"]
            
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.0f%%', startangle=90, 
                colors=colors, textprops=dict(fontsize=8, fontweight='bold')
            )
            centre_circle = plt.Circle((0,0), 0.55, fc='white')
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')
            fig.tight_layout()
            st.pyplot(fig)

        elif group_code == "G3":
            st.subheader("التفسير التفصيلي الفردي للطالب (G3 - Local SHAP)")
            st.info(f"المخطط أدناه يوضح تحليل المساهمة الفردية الخاصة بـ {student['name']} محلياً:")
            
            fig, ax = plt.subplots(figsize=(4.2, 2.4))
            contrib_dict = student["contributions"]
            feats = list(contrib_dict.keys())
            vals = list(contrib_dict.values())
            colors = ["#2F855A" if v > 0 else "#C53030" for v in vals]
            
            y_pos = range(len(feats))
            ax.barh(y_pos, vals, color=colors, height=0.5)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(feats, fontsize=8, fontweight='bold')
            ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
            ax.set_xlabel("تأثير المؤشر الفردي على القرار (+ إيجابي / - سلبي)", fontsize=8)
            ax.tick_params(axis='both', labelsize=8)
            fig.tight_layout()
            st.pyplot(fig)

            st.success(f"{student['shap_text']}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("القرار التربوي للمعلم:")
    c1, c2 = st.columns(2)

    with c1:
        if st.button("أوافق على قرار النظام", key=f"agree_{idx}", use_container_width=True):
            st.session_state.decisions[student["id"]] = "أوافق"
            if idx + 1 < len(STUDENTS_DATA):
                st.session_state.current_student += 1
            else:
                st.session_state.current_student = len(STUDENTS_DATA)
                st.session_state.step = "survey"
            st.rerun()

    with c2:
        if st.button("أعدل القرار (الذكاء الاصطناعي مخطئ)", key=f"edit_{idx}", use_container_width=True):
            st.session_state.decisions[student["id"]] = "أعدل"
            if idx + 1 < len(STUDENTS_DATA):
                st.session_state.current_student += 1
            else:
                st.session_state.current_student = len(STUDENTS_DATA)
                st.session_state.step = "survey"
            st.rerun()

    if is_researcher_mode:
        st.markdown("---")
        st.subheader("لوحة تحكم الباحثة (تظهر لكِ فقط عند استخدام الرابط الخاص):")
        radio_key = f"admin_group_eval_{idx}"
        if radio_key not in st.session_state or st.session_state[radio_key] != st.session_state.group:
            st.session_state[radio_key] = st.session_state.group

        st.radio(
            "تغيير المجموعة الحالية للمعاينة:",
            ["G1", "G2", "G3"],
            key=radio_key,
            on_change=on_group_radio_change,
            args=(radio_key,)
        )

# -------------------------------------------------------------
# 3️⃣ الشاشة الثالثة: الاستبيان النهائي لتعديل وقياس الشفافية والدقة (step == 'survey')
# -------------------------------------------------------------
elif st.session_state.step == "survey":
    st.title("📝 الاستبيان النهائي: قياس الشفافية والدقة والثقة")
    st.markdown("---")

    st.markdown(
        """
        <div style="background-color: #EDF2F7; padding: 14px; border-radius: 8px; border-right: 5px solid #2B6CB0; margin-bottom: 20px;">
            <h4 style="color: #1A365D; margin-top:0;">دليل الإجابة من (1 إلى 5):</h4>
            <p style="font-size: 15px; color: #2D3748; margin: 0;">
                <b>1</b> = غير موافق بشدة &nbsp;|&nbsp; 
                <b>2</b> = غير موافق &nbsp;|&nbsp; 
                <b>3</b> = محايد &nbsp;|&nbsp; 
                <b>4</b> = موافق &nbsp;|&nbsp; 
                <b>5</b> = موافق بشدة
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.survey_submitted:
        with st.form("survey_form"):
            st.markdown("### أولاً: وضوح الشرح وشفافية النظام (AIT)")
            ait1 = st.slider("1. كانت الشروحات والمخططات التفسيرية المقدمة واضحة وسهلة الفهم بالنسبة لي كمعلم:", 1, 5, 3)
            ait2 = st.slider("2. ساهمت التفسيرات في تبيان وتوضيح الأسباب الحقيقية وراء توصية النظام:", 1, 5, 3)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### ثانياً: الثقة والقدرة على اكتشاف القرارات الخاطئة (Trust & Trap Detection)")
            tr1 = st.slider("1. أثق في القرارات والتوصيات التي يقدمها هذا النظام كأداة مساندة للمعلم:", 1, 5, 3)
            tr2 = st.slider("2. شعرت بالاطمئنان واليقين عند اتخاذ قرار بتعديل توصية الذكاء الاصطناعي الخاطئة:", 1, 5, 3)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("📤 إرسال نتائج التجربة والإنهاء")

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
                    "group": [st.session_state.get("group", "G1")],
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

                st.session_state.survey_submitted = True
                st.session_state.step = "completed"
                st.rerun()

# -------------------------------------------------------------
# 4️⃣ الشاشة الأخيرة: شكر وتنزيل البيانات (step == 'completed')
# -------------------------------------------------------------
elif st.session_state.step == "completed":
    st.balloons()
    st.success("🎉 تم إرسال وحفظ نتائج التجربة بنجاح!")
    st.markdown("""
    ### شكر وتقدير 🌟
    شكراً جزيلاً لمشاركتكم الثمينة ووقتكم في دعم هذه الدراسة العلمية حول الذكاء الاصطناعي القابل للتفسير.
    """)

    if is_researcher_mode:
        st.markdown("---")
        with st.expander("لوحة تحميل البيانات (خاصة بالباحثة فقط)"):
            pwd = st.text_input("أدخلي رمز الدخول الخاص بالباحثة لتنزيل الملفات:", type="password", key="admin_pwd_download")
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
