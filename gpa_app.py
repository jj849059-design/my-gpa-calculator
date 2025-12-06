import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# CSS: 視覺優化 (強制對齊高度)
st.markdown("""
    <style>
    /* 1. 讓表格內容置中 */
    div[data-testid="column"] {
        text-align: center;
    }

    /* 2. 針對 sidebar 的按鈕進行高度強制統一 */
    /* 讓 + - 按鈕高度跟輸入框完全一樣 (標準是 42px) */
    div.stButton > button {
        height: 42px; 
        padding-top: 0px;
        padding-bottom: 0px;
        border-color: #494B55;
    }

    /* 3. 修改中間那個 "偽裝" 的文字輸入框 */
    /* 隱藏輸入框上面的小標籤空間 (以免它比按鈕低) */
    div[data-testid="stTextInput"] {
        margin-top: -5px; /* 微調讓它跟按鈕對齊 */
    }
    
    /* 4. 針對 "disabled" (唯讀) 的輸入框進行樣式覆寫 */
    /* 讓它看起來像正常的框，不要變灰 */
    div[data-testid="stTextInput"] input:disabled {
        background-color: #262730; /* 保持深色背景 */
        color: white;              /* 文字白色 */
        opacity: 1;                /* 取消透明度 (關鍵!) */
        text-align: center;        /* 文字置中 */
        font-weight: bold;
        font-size: 18px;
        -webkit-text-fill-color: white; /* 確保 Safari/Chrome 文字顏色正確 */
        border-color: #494B55;
        cursor: default;           /* 滑鼠游標改為預設 */
    }

    /* 隱藏 disabled 輸入框右邊可能出現的鎖頭圖示 */
    div[data-testid="stTextInput"] svg {
        display: none;
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
    
    # --- 🔥 完美高度對齊版 成績選擇器 ---
    st.write("學期成績")
    
    def prev_grade():
        if st.session_state.current_grade_index < len(grade_list) - 1:
            st.session_state.current_grade_index += 1
    def next_grade():
        if st.session_state.current_grade_index > 0:
            st.session_state.current_grade_index -= 1

    # 版面配置：使用 gap="small" 讓按鈕緊貼
    # vertical_alignment="top" 這裡很重要，因為我們要消掉 input 上方的 padding
    c_minus, c_display, c_plus = st.columns([1, 3, 1], gap="small", vertical_alignment="top")
    
    with c_minus:
        # 按鈕高度已被 CSS 強制設為 42px
        st.button("－", on_click=prev_grade, use_container_width=True)
        
    with c_display:
        current_grade = grade_list[st.session_state.current_grade_index]
        
        # 🌟 關鍵修改：直接使用原生 text_input
        # 1. label_visibility="collapsed" -> 隱藏標籤，節省空間
        # 2. disabled=True -> 禁止手動輸入 (避免手機鍵盤跳出來)
        # 3. key 每次都要變(或固定)，這裡用 key 固定配合 value 更新
        st.text_input(
            "hidden_label", 
            value=current_grade, 
            label_visibility="collapsed", 
            disabled=True, 
            key="grade_display_input"
        )
        
    with c_plus:
        st.button("＋", on_click=next_grade, use_container_width=True)
    
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
