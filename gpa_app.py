import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# CSS: 視覺優化 (讓成績選擇器變身！)
st.markdown("""
    <style>
    /* 1. 讓表格內容置中 */
    div[data-testid="column"] {
        text-align: center;
    }

    /* 2. 針對 "學期成績" 的數字輸入框進行魔改 */
    /* 透過 aria-label 定位到這個特定的輸入框，把原本的數字變透明 */
    input[aria-label="grade_input_label"] {
        color: transparent !important; /* 隱藏數字 */
        caret-color: transparent;      /* 隱藏游標 */
        cursor: default;               /* 滑鼠游標不變 */
    }
    
    /* 禁止使用者點擊該輸入框文字區域 (防止跳出鍵盤)，但保留按鈕功能 */
    input[aria-label="grade_input_label"] {
        pointer-events: none; 
    }

    /* 3. 製作 "文字覆蓋層" 的樣式 */
    .grade-display-overlay {
        position: relative;
        top: -36px;       /* 向上移動覆蓋住原本的輸入框 */
        left: 10px;       /* 靠左對齊，模擬輸入框文字位置 */
        height: 0;        /* 設定高度為 0，避免佔用下方空間 */
        width: 70%;       /* 寬度限制，避免擋到右邊的按鈕 */
        overflow: visible;
        pointer-events: none; /* 關鍵！讓點擊穿透這層文字，直接點到底下的框框 */
        font-weight: 600;
        color: white;     /* 強制白色文字 */
        font-size: 16px;  /* 字體大小 */
        z-index: 5;
    }

    /* 調整分隔線距離 */
    hr {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* 調整側邊欄標題間距 */
    .sidebar-label {
        font-size: 14px;
        margin-bottom: 5px;
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
# 建立一個反向清單：從 [X, E, ..., A+]，這樣按 + 號時成績才會變高
grade_options = list(grade_map.keys())[::-1] 
max_grade_index = len(grade_options) - 1

# --- 2. 初始化 Session State ---
if 'courses' not in st.session_state:
    st.session_state.courses = []

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增科目")
    course_name = st.text_input("科目名稱 (選填)", placeholder="例如：微積分")
    credits = st.number_input("學分數", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    
    # --- 🔥 完美擬真版：直接使用 st.number_input ---
    
    # 1. 自己畫標題，模擬 st.number_input 的標題樣式
    st.markdown('<p class="sidebar-label">學期成績</p>', unsafe_allow_html=True)
    
    # 2. 使用 number_input 選擇 "索引值" (0 ~ 11)
    # label 設為 "grade_input_label" 以便 CSS 定位
    grade_idx = st.number_input(
        "grade_input_label", 
        min_value=0, 
        max_value=max_grade_index, 
        value=max_grade_index, # 預設選最下面的 (A+)
        step=1,
        label_visibility="collapsed" # 隱藏原本的標題
    )
    
    # 3. 根據索引值抓出對應的文字 (例如 "A+")
    selected_grade_text = grade_options[grade_idx]
    
    # 4. 用 HTML 覆蓋層把文字 "貼" 在輸入框上面
    st.markdown(f'<div class="grade-display-overlay">{selected_grade_text}</div>', unsafe_allow_html=True)

    # ------------------------------------
    
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    if st.button("➕ 加入清單", type="primary", use_container_width=True):
        st.session_state.courses.append({
            "科目": course_name if course_name else f"科目 {len(st.session_state.courses)+1}",
            "學分": credits,
            "成績": selected_grade_text,
            "積分 (GP)": grade_map[selected_grade_text],
            "學分 × GP": credits * grade_map[selected_grade_text]
        })
        st.success(f"已加入 {selected_grade_text}")

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
