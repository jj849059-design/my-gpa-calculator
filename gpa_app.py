import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# CSS: 修正 Streamlit 表格內容對齊
st.markdown("""
    <style>
    /* 強制修正表格標頭與內容的對齊 */
    th, td {
        text-align: center !important;
    }
    div[data-testid="stMetricValue"] {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 定義成績對照表 ---
grade_map = {
    "A+": 4.3, "A":  4.0, "A-": 3.7,
    "B+": 3.3, "B":  3.0, "B-": 2.7,
    "C+": 2.3, "C":  2.0, "C-": 1.7,
    "D":  1.0, "E":  0.0, "X":  0.0
}

# --- 2. 初始化 Session State ---
if 'courses' not in st.session_state:
    st.session_state.courses = []

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增科目")
    course_name = st.text_input("科目名稱 (選填)", placeholder="例如：微積分")
    credits = st.number_input("學分數", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    grade = st.selectbox("學期成績", options=list(grade_map.keys()))
    
    if st.button("➕ 加入清單", type="primary"):
        st.session_state.courses.append({
            "科目": course_name if course_name else f"科目 {len(st.session_state.courses)+1}",
            "學分": credits,
            "成績": grade,
            "積分 (GP)": grade_map[grade],
            "學分 × GP": credits * grade_map[grade]
        })
        st.success(f"已加入 {grade}")

    st.divider()
    # 這裡修正了：使用 st.rerun() 取代舊版指令
    if st.button("🗑️ 清空所有科目"):
        st.session_state.courses = []
        st.rerun()

# --- 4. 主畫面：版面配置 (置中處理) ---
# 使用 Columns 將內容夾在中間 [左空, 中間內容, 右空]
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 標題放在中間欄位才會置中
    st.markdown("<h1 style='text-align: center;'>🎓 大學 GPA 計算機</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.courses) > 0:
        # 原始數據 (用於計算)
        df = pd.DataFrame(st.session_state.courses)
        
        # --- 計算 GPA ---
        total_credits = df["學分"].sum()
        total_points = df["學分 × GP"].sum()
        gpa = total_points / total_credits if total_credits > 0 else 0.0
        
        # --- 顯示 GPA ---
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align: center;">
            <h2 style="margin:0; color:#555;">學期平均 GPA</h2>
            <h1 style="margin:0; color:#ff4b4b; font-size: 60px;">{gpa:.2f}</h1>
            <p style="margin:0;">總學分: {total_credits} | 總積分: {total_points:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 科目清單")

        # --- 建立顯示專用的 DataFrame ---
        display_df = df.copy()
        # 轉成字串確保對齊，並保留小數點位數
        display_df["學分"] = display_df["學分"].apply(lambda x: f"{x:.1f}")
        display_df["積分 (GP)"] = display_df["積分 (GP)"].apply(lambda x: f"{x:.1f}")
        display_df["學分 × GP"] = display_df["學分 × GP"].apply(lambda x: f"{x:.1f}")

        # 設定 Pandas Style (置中)
        styled_df = display_df.style.set_properties(**{'text-align': 'center'})\
                                    .set_table_styles([
                                        {'selector': 'th', 'props': [('text-align', 'center')]},
                                        {'selector': 'td', 'props': [('text-align', 'center')]}
                                    ])

        # 顯示表格
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
    else:
        # 空狀態顯示
        st.info("👈 請從左側欄位新增您的科目與成績")
        
        # --- 對照表 ---
        with st.expander("查看 105學年度 GP 對照表"):
            ref_df = pd.DataFrame(list(grade_map.items()), columns=["等第成績", "GP 值"])
            
            ref_df["GP 值"] = ref_df["GP 值"].apply(lambda x: f"{x:.1f}")
            
            styled_ref = ref_df.style.set_properties(**{'text-align': 'center'})\
                                     .set_table_styles([
                                         {'selector': 'th', 'props': [('text-align', 'center')]},
                                         {'selector': 'td', 'props': [('text-align', 'center')]}
                                     ])
            # 使用 st.table 讓對照表看起來更像靜態表格
            st.table(styled_ref)
