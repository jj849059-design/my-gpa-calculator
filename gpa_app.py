import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="GPA 計算機 (105學年度制)", page_icon="🎓", layout="wide")

# --- 1. 定義成績對照表 ---
grade_map = {
    "A+": 4.3, "A":  4.0, "A-": 3.7,
    "B+": 3.3, "B":  3.0, "B-": 2.7,
    "C+": 2.3, "C":  2.0, "C-": 1.7,
    "D":  1.0, "E":  0.0, "X":  0.0
}
# 建立反向清單：按 + 號時成績變高 (X -> E -> ... -> A+)
grade_options_reversed = list(grade_map.keys())[::-1] 
max_grade_index = len(grade_options_reversed) - 1

# --- 2. 初始化 Session State ---
if 'courses' not in st.session_state:
    st.session_state.courses = []

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增科目")
    
    course_name = st.text_input("科目名稱 (選填)", placeholder="例如：微積分")
    
    # 這是標準的學分數輸入框 (供對照用)
    credits = st.number_input("學分數", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    
    # --- 🔥 修正版：學期成績選擇器 ---
    
    # 使用 number_input 來當作「控制器」，數值代表 list 的 index
    # label="學期成績" 這是 CSS 定位的關鍵
    grade_idx = st.number_input(
        "學期成績",
        min_value=0, 
        max_value=max_grade_index, 
        value=max_grade_index, # 預設 A+
        step=1
    )
    
    # 取得對應的文字 (A+, A...)
    selected_grade_text = grade_options_reversed[grade_idx]
    
    # --- CSS 魔術區 (修正定位問題) ---
    st.markdown(f"""
    <style>
    /* 1. 隱藏原本的數字 (0, 1, 2...) */
    div[data-testid="stNumberInput"]:has(input[aria-label="學期成績"]) input {{
        color: transparent !important;
    }}

    /* 2. 關鍵修正：鎖定 base-input 容器，這是「不含按鈕」的純文字區 */
    div[data-testid="stNumberInput"]:has(input[aria-label="學期成績"]) div[data-baseweb="base-input"] {{
        position: relative !important; /* 強制設定為相對定位基準點 */
    }}

    /* 3. 在 base-input 裡面產生偽元素顯示文字 */
    div[data-testid="stNumberInput"]:has(input[aria-label="學期成績"]) div[data-baseweb="base-input"]::after {{
        content: "{selected_grade_text}";  /* 插入 Python 變數文字 */
        
        /* 絕對定位：填滿整個 base-input 區域 */
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        
        /* 彈性盒子：讓文字上下左右絕對置中 */
        display: flex;
        justify-content: center; /* 水平置中 */
        align-items: center;     /* 垂直置中 */
        
        /* 文字樣式：模仿原生外觀 */
        color: white;       /* 確保深色模式下看得到 */
        font-weight: 400;   /* 字體粗細跟上面學分數一致 */
        font-size: 1rem;    /* 字體大小 */
        pointer-events: none; /* 讓滑鼠點擊穿透文字，按得到輸入框 */
    }}
    
    /* 修正表格置中 */
    div[data-testid="column"] {{ text-align: center; }}
    
    /* 讓表格內的刪除按鈕填滿 */
    div.stButton > button {{ width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

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
        df = pd.DataFrame(st.session_state.courses)
        
        total_credits = df["學分"].sum()
        total_points = df["學分 × GP"].sum()
        gpa = total_points / total_credits if total_credits > 0 else 0.0
        
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align: center;">
            <h2 style="margin:0; color:#555;">學期平均 GPA</h2>
            <h1 style="margin:0; color:#ff4b4b; font-size: 60px;">{gpa:.2f}</h1>
            <p style="margin:0; color: black; font-size: 18px; font-weight: 500;">總學分: {total_credits} | 總積分: {total_points:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 科目清單")

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
