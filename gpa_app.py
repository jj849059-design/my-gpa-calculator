import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# CSS: 視覺優化 (讓成績選擇器長得像原生輸入框)
st.markdown("""
    <style>
    /* 讓所有表格內容置中 */
    div[data-testid="column"] {
        text-align: center;
    }
    
    /* 調整按鈕與輸入框的垂直對齊 */
    div.stButton > button {
        height: 42px; /* 強制設定按鈕高度與輸入框一致 */
        padding-top: 0px;
        padding-bottom: 0px;
        font-weight: bold;
        border-color: #494B55; /* 讓邊框顏色跟輸入框接近 */
    }

    /* 模擬 Streamlit 原生輸入框的樣式 */
    .grade-display-box {
        background-color: #262730; /* Streamlit 深色模式的輸入框背景色 */
        border: 1px solid #494B55; /* 邊框顏色 */
        border-radius: 0.5rem;     /* 圓角 */
        height: 42px;              /* 高度 */
        display: flex;
        align-items: center;       /* 垂直置中 */
        justify-content: center;   /* 水平置中 */
        font-size: 18px;
        font-weight: 600;
        color: white;              /* 文字顏色 */
        margin-bottom: 0px;
    }

    /* 調整分隔線距離 */
    hr {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
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
grade_list = list(grade_map.keys())

# --- 2. 初始化 Session State ---
if 'courses' not in st.session_state:
    st.session_state.courses = []
if 'current_grade_index' not in st.session_state:
    st.session_state.current_grade_index = 0

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增科目")
    course_name = st.text_input("科目名稱 (選填)", placeholder="例如：微積分")
    credits = st.number_input("學分數", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    
    # --- 🔥 超級擬真版 成績選擇器 ---
    st.write("學期成績") # 標題
    
    # 按鈕邏輯
    def prev_grade():
        if st.session_state.current_grade_index < len(grade_list) - 1:
            st.session_state.current_grade_index += 1
    def next_grade():
        if st.session_state.current_grade_index > 0:
            st.session_state.current_grade_index -= 1

    # 版面配置：使用 gap="small" 讓按鈕緊貼
    # 比例設為 [1, 3, 1] 讓中間寬一點，按鈕窄一點，看起來更像是一個整體
    c_minus, c_display, c_plus = st.columns([1, 3, 1], gap="small", vertical_alignment="center")
    
    with c_minus:
        st.button("－", on_click=prev_grade, use_container_width=True)
        
    with c_display:
        current_grade = grade_list[st.session_state.current_grade_index]
        # 使用自訂的 CSS class 畫出假輸入框
        st.markdown(f'<div class="grade-display-box">{current_grade}</div>', unsafe_allow_html=True)
        
    with c_plus:
        st.button("＋", on_click=next_grade, use_container_width=True)
    
    # 對接變數
    grade = current_grade
    # ------------------------------------
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("➕ 加入清單", type="primary", use_container_width=True):
        st.session_state.courses.append({
            "科目": course_name if course_name else f"科目 {len(st.session_state.courses)+1}",
            "學分": credits,
            "成績": grade,
            "積分 (GP)": grade_map[grade],
            "學分 × GP": credits * grade_map[grade]
        })
        st.success(f"已加入 {grade}")

    st.divider()
    if st.button("🗑️ 清空所有科目"):
        st.session_state.courses = []
        st.rerun()

# --- 4. 主畫面：版面配置 ---
col1, col2, col3 = st.columns([1, 2.5, 1]) 

with col2:
    st.markdown("<h1 style='text-align: center;'>🎓 大學 GPA 計算機</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.courses) > 0:
        # 原始數據
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
            <p style="margin:0; color: black; font-size: 18px; font-weight: 500;">總學分: {total_credits} | 總積分: {total_points:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 科目清單")

        # --- 表格標題列 ---
        cols_ratio = [3, 1, 1, 1, 1, 1.5]
        h1, h2, h3, h4, h5, h6 = st.columns(cols_ratio, vertical_alignment="bottom", gap="small")
        
        def header_txt(txt):
            return f"<div style='text-align: center; font-weight: bold; color: #555; margin-bottom: 5px;'>{txt}</div>"
            
        h1.markdown(header_txt("科目"), unsafe_allow_html=True)
        h2.markdown(header_txt("學分"), unsafe_allow_html=True)
        h3.markdown(header_txt("成績"), unsafe_allow_html=True)
        h4.markdown(header_txt("GP"), unsafe_allow_html=True)
        h5.markdown(header_txt("總分"), unsafe_allow_html=True)
        h6.markdown(header_txt("操作"), unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0 0 10px 0; border-top: 2px solid #ccc;'>", unsafe_allow_html=True)

        # --- 顯示每一行資料 ---
        for i, course in enumerate(st.session_state.courses):
            c1, c2, c3, c4, c5, c6 = st.columns(cols_ratio, vertical_alignment="center", gap="small")
            
            def cell_txt(txt):
                return f"<div style='text-align: center; font-size: 16px;'>{txt}</div>"

            c1.markdown(cell_txt(course["科目"]), unsafe_allow_html=True)
            c2.markdown(cell_txt(f"{course['學分']:.1f}"), unsafe_allow_html=True)
            c3.markdown(cell_txt(course["成績"]), unsafe_allow_html=True)
            c4.markdown(cell_txt(f"{course['積分 (GP)']:.1f}"), unsafe_allow_html=True)
            c5.markdown(cell_txt(f"{course['學分 × GP']:.1f}"), unsafe_allow_html=True)
            
            with c6:
                if st.button("刪除", key=f"del_{i}", use_container_width=True):
                    st.session_state.courses.pop(i)
                    st.rerun()
            
            st.markdown("<hr style='border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
    else:
        st.info("👈 請從左側欄位新增您的科目與成績")
        
        with st.expander("查看 105學年度 GP 對照表"):
            ref_df = pd.DataFrame(list(grade_map.items()), columns=["等第成績", "GP 值"])
            ref_df["GP 值"] = ref_df["GP 值"].apply(lambda x: f"{x:.1f}")
            st.table(ref_df)
