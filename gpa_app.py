import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# CSS: 修正對齊 + 消除欄位多餘留白
st.markdown("""
    <style>
    /* 讓所有欄位內的文字預設置中 */
    div[data-testid="column"] {
        text-align: center;
    }
    
    /* 減少欄位左右的內縮留白，讓按鈕空間變大 */
    div[data-testid="column"] > div {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }

    /* 調整分隔線距離 */
    hr {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* 自訂成績顯示框的樣式 (模擬 Input 框) */
    .grade-display {
        border: 1px solid rgba(128, 128, 128, 0.5);
        border-radius: 4px;
        padding: 5px;
        margin-top: 0px; /* 對齊按鈕 */
        font-size: 18px;
        font-weight: bold;
        line-height: 1.6;
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
grade_list = list(grade_map.keys()) # 轉成清單方便用索引操作 ['A+', 'A', 'A-', ...]

# --- 2. 初始化 Session State ---
if 'courses' not in st.session_state:
    st.session_state.courses = []

# 初始化「目前選擇的成績索引」，預設為 0 (也就是 A+)
if 'current_grade_index' not in st.session_state:
    st.session_state.current_grade_index = 0

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增科目")
    course_name = st.text_input("科目名稱 (選填)", placeholder="例如：微積分")
    credits = st.number_input("學分數", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    
    # --- 🔥 改造成績選擇器 (模擬 - + 按鈕) ---
    st.write("學期成績")
    
    # 定義按鈕功能
    def prev_grade():
        # 按下 - 號：往後選 (成績變低, index + 1)，直到最後一個
        if st.session_state.current_grade_index < len(grade_list) - 1:
            st.session_state.current_grade_index += 1
            
    def next_grade():
        # 按下 + 號：往前選 (成績變高, index - 1)，直到第一個
        if st.session_state.current_grade_index > 0:
            st.session_state.current_grade_index -= 1

    # 建立三欄：[ 減號鈕 ] [ 顯示文字 ] [ 加號鈕 ]
    # 使用 vertical_alignment="bottom" 讓它們對齊底部
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1], vertical_alignment="bottom")
    
    with g_col1:
        st.button("－", on_click=prev_grade, use_container_width=True, help="降低成績")
        
    with g_col3:
        st.button("＋", on_click=next_grade, use_container_width=True, help="提高成績")

    with g_col2:
        # 取得當前成績文字
        current_grade = grade_list[st.session_state.current_grade_index]
        # 用 HTML 畫一個框框顯示成績
        st.markdown(f'<div class="grade-display">{current_grade}</div>', unsafe_allow_html=True)

    # 為了相容原本邏輯，把變數名稱對接回去
    grade = current_grade
    # ------------------------------------
    
    # 加入清單按鈕
    # 這裡加一點 margin-top 讓它不要貼太近
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
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
        
        # 標題強制置中
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
            # 建立欄位
            c1, c2, c3, c4, c5, c6 = st.columns(cols_ratio, vertical_alignment="center", gap="small")
            
            # HTML 強制置中
            def cell_txt(txt):
                return f"<div style='text-align: center; font-size: 16px;'>{txt}</div>"

            c1.markdown(cell_txt(course["科目"]), unsafe_allow_html=True)
            c2.markdown(cell_txt(f"{course['學分']:.1f}"), unsafe_allow_html=True)
            c3.markdown(cell_txt(course["成績"]), unsafe_allow_html=True)
            c4.markdown(cell_txt(f"{course['積分 (GP)']:.1f}"), unsafe_allow_html=True)
            c5.markdown(cell_txt(f"{course['學分 × GP']:.1f}"), unsafe_allow_html=True)
            
            # 按鈕
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
