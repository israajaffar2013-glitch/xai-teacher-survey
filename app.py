import os
import random
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# -------------------------------------------------------------
# ⚙️ إعدادات الصفحة والواجهة
# -------------------------------------------------------------
st.set_page_config(
    page_title="منصة التقييم والتنبؤ الأكاديمي (EDSS)",
    page_icon="🎓",
    layout="wide",
)

# تنسيقات بصرية لتكبير الخطوط والأرقام
st.markdown(
    """
    <style>
    .big-metric-box {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .metric-title {
        font-size: 19px !important;
        color: #495057 !important;
        font-weight: bold !important;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 36px !important;
        color: #1d3557 !important;
        font-weight: 800 !important;
    }
    .status-badge-red {
        background-color: #ffe3e3;
        color: #c92a2a;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #ffa8a8;
    }
    .status-badge-green {
        background-color: #d3f9d8;
        color: #2b8a3e;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #8ce99a;
    }
    </style>
""",
    unsafe_allow_html=True,
)

CSV_FILE = "student_profiles.csv"
RESPONSES_FILE = "teachers_responses.csv"


# -------------------------------------------------------------
# 📁 تحميل بيانات الطلاب (تضمين بطاقات اختبار الوعي 3, 6, 9)
# -------------------------------------------------------------
@st.cache_data
def load_students():
  data = {
      "student_id": [f"S{i:02d}" for i in range(1, 11)],
      "name": [
          "طالب 1",
          "طالب 2",
          "طالب 3",
          "طالب 4",
          "طالب 5",
          "طالب 6",
          "طالب 7",
          "طالب 8",
          "طالب 9",
          "طالب 10",
      ],
      "quiz_score": [85, 40, 92, 78, 35, 42, 88, 30, 95, 82],
      "attendance_rate": [90, 50, 95, 85, 45, 50, 90, 40, 98, 85],
      "assignments": [88, 45, 90, 80, 40, 48, 85, 35, 92, 80],
      "platform_activity": [82, 55, 91, 75, 50, 40, 89, 45, 94, 84],
      "ai_prediction": [
          "مستقر أكاديمياً",
          "معرض للتعثر الأكاديمي",
          "معرض للتعثر الأكاديمي",  # متناقض (طالب ممتاز والنظام يصنفه تعثر)
          "مستقر أكاديمياً",
          "معرض للتعثر الأكاديمي",
          "مستقر أكاديمياً",  # متناقض (طالب ضعيف والنظام يصنفه مستقر)
          "مستقر أكاديمياً",
          "معرض للتعثر الأكاديمي",
          "معرض للتعثر الأكاديمي",  # متناقض (طالب ممتاز والنظام يصنفه تعثر)
          "مستقر أكاديمياً",
      ],
  }
  return pd.DataFrame(data)


df_students = load_students()

# تهيئة متطلبات الجلسة
if "consent" not in st.session_state:
  st.session_state.consent = False
if "group" not in st.session_state:
  st.session_state.group = random.choice(["G1", "G2", "G3"])
if "current_student" not in st.session_state:
  st.session_state.current_student = 0
if "decisions" not in st.session_state:
  st.session_state.decisions = {}

# -------------------------------------------------------------
# 1️⃣ الشاشة الأولى: الموافقة والتعليمات
# -------------------------------------------------------------
if not st.session_state.consent:
  st.title("🎓 دراسة تجريبية: تقييم قرارات الذكاء الاصطناعي في التعليم")
  st.info(
      "📌 **هدف الدراسة:** قياس مدى قدرة المدرس على تقييم توصيات الذكاء"
      " الاصطناعي واكتشاف الأخطاء إن وجدت."
  )

  st.markdown("""
    ### 📋 ما المطلوب منك في هذه التجربة؟
    1. ستعرض عليك بطاقات لـ **10 طلاب**.
    2. كل بطاقة تحتوي على **البيانات الأكاديمية للطالب** + **توصية نظام الذكاء الاصطناعي**.
    3. مهمتك هي قراءة البيانات والتدقيق فيها، ثم اتخاذ قرارك التربوي:
       * **🟢 أوافق:** إذا كان تقييم الذكاء الاصطناعي صحيحاً ومطابقاً لبيانات الطالب.
       * **🔴 أعدل القرار:** إذا شعرت أن الذكاء الاصطناعي أخطأ في التقييم وبحاجة للتعديل.
    """)

  st.divider()
  col1, col2 = st.columns(2)
  with col1:
    exp_years = st.number_input(
        "سنوات الخبرة في التدريس:", min_value=0, max_value=40, value=5
    )
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

  if st.button("✅ أوافق وابدأ تقييم الطلاب", type="primary"):
    st.session_state.consent = True
    st.session_state.exp_years = exp_years
    st.session_state.subject = subject
    st.rerun()

# -------------------------------------------------------------
# 2️⃣ الشاشة الثانية: تقييم الطلاب
# -------------------------------------------------------------
else:
  # شريط المعاينة للباحث
  with st.sidebar:
    st.subheader("⚙️ خيارات المعاينة")
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

    st.divider()
    if st.button("🔄 إعادة بدء التجربة من البداية"):
      st.session_state.consent = False
      st.session_state.current_student = 0
      st.session_state.decisions = {}
      st.rerun()

  group_code = st.session_state.group
  idx = st.session_state.current_student

  if idx < len(df_students):
    student = df_students.iloc[idx]

    # شريط توجيهي علوي
    st.warning(
        f"📍 **الطالب ({idx + 1} من {len(df_students)}):** اقرأ أرقام الطالب"
        " وقارنها بتوصية النظام في اليسار، ثم اتخذ قرارك في الأسفل."
    )

    col_data, col_ai = st.columns(2)

    # العمود الأول: سجل الطالب بأرقام بارزة
    with col_data:
      st.subheader(f"👤 سجل الطالب: {student['name']}")

      m1, m2 = st.columns(2)
      with m1:
        st.markdown(
            f'<div class="big-metric-box"><div'
            ' class="metric-title">📝 التقييم التكويني</div><div'
            f' class="metric-value">{student["quiz_score"]}%</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="big-metric-box"><div'
            ' class="metric-title">📚 تسليم الواجبات</div><div'
            f' class="metric-value">{student["assignments"]}%</div></div>',
            unsafe_allow_html=True,
        )

      with m2:
        st.markdown(
            f'<div class="big-metric-box"><div'
            ' class="metric-title">📅 نسبة الحضور</div><div'
            f' class="metric-value">{student["attendance_rate"]}%</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="big-metric-box"><div'
            ' class="metric-title">💻 نشاط المنصة</div><div'
            f' class="metric-value">{student["platform_activity"]}%</div></div>',
            unsafe_allow_html=True,
        )

    # العمود الثاني: تقييم وتفسير الذكاء الاصطناعي
    with col_ai:
      st.subheader("🤖 تقييم وتنبؤ الذكاء الاصطناعي")
      pred_status = student["ai_prediction"]

      if "تعثر" in pred_status or "خطر" in pred_status:
        st.markdown(
            f'<div class="status-badge-red">⚠️ {pred_status}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "📌 **معنى التقييم:** تشير التنبؤات إلى احتمالية انخفاض تحصيل"
            " الطالب وتطلبه تدخلاً."
        )
      else:
        st.markdown(
            f'<div class="status-badge-green">✅ {pred_status}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "📌 **معنى التقييم:** يسير الطالب بمعدل جيد يتوافق مع متطلبات"
            " النجاح."
        )

      st.markdown("<br>", unsafe_allow_html=True)

      # عرض التفسير المنسق
      if group_code == "G1":
        st.info(
            "ℹ️ **تنبؤ مباشر:** يقدم النظام النتيجة النهائية فقط دون تفاصيل"
            " خوارزمية."
        )

      elif group_code == "G2":
        st.subheader("📊 أهمية المؤشرات العامة للنظام")
        fig, ax = plt.subplots(figsize=(5, 2.2))
        features = ["التقييم التكويني", "الحضور", "الواجبات", "نشاط المنصة"]
        importance = [35, 25, 20, 20]
        ax.barh(features, importance, color="#3182bd")
        ax.set_xlabel("الأهمية العامة (%)")
        st.pyplot(fig)

      elif group_code == "G3":
        st.subheader("🔍 الشرح التفصيلي لقرار هذا الطالب (SHAP)")
        fig, ax = plt.subplots(figsize=(5, 2.2))
        features = ["التقييم التكويني", "الحضور", "الواجبات", "المنصة"]

        # الحساب بناءً على الحد المرجعي للنجاح (50%)
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
        st.pyplot(fig)

        st.markdown("""
                **💡 كيف تقرأ هذا الرسم؟**
                * 🟢 **العمود الأخضر (+):** أداء أعلى من حد النجاح (50%) يدعم استقرار الطالب.
                * 🔴 **العمود الأحمر (-):** أداء أدنى من حد النجاح (50%) يرفع احتمالية التعثر.
                """)

    st.divider()

    # أزرار اتخاذ القرار
    st.subheader("🎯 قرارك التربوي كمدرس:")
    c1, c2 = st.columns(2)

    with c1:
      if st.button("🟢 أوافق على قرار النظام", use_container_width=True):
        st.session_state.decisions[student["student_id"]] = "أوافق"
        st.session_state.current_student += 1
        st.rerun()

    with c2:
      if st.button(
          "🔴 أعدل القرار (الذكاء الاصطناعي مخطئ)", use_container_width=True
      ):
        st.session_state.decisions[student["student_id"]] = "أعدل"
        st.session_state.current_student += 1
        st.rerun()

# -------------------------------------------------------------
# 3️⃣ الشاشة الثالثة: الاستبيان البعدي والتسجيل الشامل
# -------------------------------------------------------------
  else:
    st.balloons()
    st.success("🎉 أحسنت! أكملت تقييم الطلاب الـ 10 بنجاح.")
    st.subheader("📝 الاستبيان النهائي (3 دقائق):")

    with st.form("survey_form"):
      st.markdown("#### 1️⃣ وضوح الشرح والشفافية")
      ait1 = st.slider(
          "1. كان الشرح المقدم من النظام واضحاً وسهل الفهم:", 1, 5, 3
      )
      ait2 = st.slider(
          "2. ساعدني الشرح على معرفة سبب اتخاذ النظام لهذا القرار:", 1, 5, 3
      )

      st.markdown("#### 2️⃣ الثقة والقدرة على الاكتشاف")
      tr1 = st.slider(
          "1. أثق في القرارات التي يقدمها هذا النظام كإرشادات مساندة:", 1, 5, 3
      )
      tr2 = st.slider(
          "2. شعرت بالتأكد عند اتخاذ قرار بتعديل أو موافقة رأي النظام:",
          1,
          5,
          3,
      )

      submitted = st.form_submit_button("إرسال نتائج التجربة")

      if submitted:
        # 1. حساب نسبة اكتشاف البطاقات المغلوطة (S03, S06, S09)
        trap_correct = 0
        for trap_id in ["S03", "S06", "S09"]:
          if st.session_state.decisions.get(trap_id) == "أعدل":
            trap_correct += 1
        trap_detection_score = round((trap_correct / 3) * 100, 2)

        # 2. حساب الدقة الكلية عبر كافة الطلاب الـ 10
        correct_answers = {
            "S01": "أوافق",
            "S02": "أوافق",
            "S03": "أعدل",
            "S04": "أوافق",
            "S05": "أوافق",
            "S06": "أعدل",
            "S07": "أوافق",
            "S08": "أوافق",
            "S09": "أعدل",
            "S10": "أوافق",
        }
        total_correct = sum(
            1
            for sid, c_dec in correct_answers.items()
            if st.session_state.decisions.get(sid) == c_dec
        )
        total_accuracy = round((total_correct / 10) * 100, 2)

        # 3. بناء الصف الشامل للاستجابة
        res_data = {
            "exp_years": [st.session_state.get("exp_years", 0)],
            "subject": [st.session_state.get("subject", "")],
            "group": [group_code],
            # تفاصيل قرارات الطلاب الـ 10
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
            # المؤشرات الإحصائية المحسوبة
            "trap_detection_score": [trap_detection_score],
            "total_accuracy": [total_accuracy],
            "ait_score": [(ait1 + ait2) / 2],
            "trust_score": [(tr1 + tr2) / 2],
        }
        res_df = pd.DataFrame(res_data)

       # حفظ البيانات في ملف CSV مع دعم اللغة العربية في Excel
        if os.path.exists(RESPONSES_FILE):
            res_df.to_csv(RESPONSES_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
        else:
            res_df.to_csv(RESPONSES_FILE, index=False, encoding="utf-8-sig")

        st.success("تم حفظ إجابات المدرس بنجاح. شكراً لمشاركتك القيمة!")
 # --- زر تنزيل النتائج المجمعة ---
    st.markdown("---")
    if os.path.exists('teachers_responses.csv'):
        with open('teachers_responses.csv', 'rb') as f:
            st.download_button(
                label="📥 تنزيل ملف استجابات المعلمين (CSV)",
                data=f,
                file_name="teachers_responses.csv",
                mime="text/csv",
                key="download_csv_btn"
            )