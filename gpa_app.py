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
    if st.button("🗑️ 清空所有科目"):
        st.session_state.courses = []
        st.rerun()

# --- 4. 主畫面：版面配置 (置中處理) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
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
            <p style="margin:0; color: black; font-size: 18px; font-weight: 500;">總學分: {total_credits} | 總積分: {total_points:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 科目清單")
        st.caption("💡 點擊右側垃圾桶即可刪除單筆資料")

        # --- 模擬表格標題列 ---
        # 定義欄位比例：科目寬一點，數據窄一點，刪除鈕最小
        cols_ratio = [3, 1.5, 1.5, 1.5, 1.5, 1]
        h1, h2, h3, h4, h5, h6 = st.columns(cols_ratio)
        
        # 標題樣式 (置中 + 粗體)
        def header_txt(txt):
            return f"<div style='text-align: center; font-weight: bold; color: #555;'>{txt}</div>"
            
        h1.markdown(header_txt("科目"), unsafe_allow_html=True)
        h2.markdown(header_txt("學分"), unsafe_allow_html=True)
        h3.markdown(header_txt("成績"), unsafe_allow_html=True)
        h4.markdown(header_txt("GP"), unsafe_allow_html=True)
        h5.markdown(header_txt("總分"), unsafe_allow_html=True)
        h6.markdown(header_txt("刪除"), unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 5px 0; border-top: 2px solid #eee;'>", unsafe_allow_html=True)

        # --- 顯示每一行資料 ---
        # 使用 enumerate 取得 index，這樣我們才知道要刪除哪一筆
        for i, course in enumerate(st.session_state.courses):
            c1, c2, c3, c4, c5, c6 = st.columns(cols_ratio)
            
            # 內容樣式 (置中)
            def cell_txt(txt):
                return f"<div style='text-align: center; line-height: 2.5;'>{txt}</div>"

            c1.markdown(cell_txt(course["科目"]), unsafe_allow_html=True)
            c2.markdown(cell_txt(f"{course['學分']:.1f}"), unsafe_allow_html=True)
            c3.markdown(cell_txt(course["成績"]), unsafe_allow_html=True)
            c4.markdown(cell_txt(f"{course['積分 (GP)']:.1f}"), unsafe_allow_html=True)
            c5.markdown(cell_txt(f"{course['學分 × GP']:.1f}"), unsafe_allow_html=True)
            
            # 刪除按鈕
            with c6:
                # 每個按鈕都需要唯一的 key，我們用 index 來當 key
                if st.button("🗑️", key=f"del_{i}", help="刪除此科目"):
                    st.session_state.courses.pop(i) # 從清單中移除
                    st.rerun() # 重新整理頁面以更新顯示
            
            # 每一行下面加一條細線分隔
            st.markdown("<hr style='margin: 2px 0; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
        
    else:
        st.info("👈 請從左側欄位新增您的科目與成績")
        
        with st.expander("查看 105學年度 GP 對照表"):
            ref_df = pd.DataFrame(list(grade_map.items()), columns=["等第成績", "GP 值"])
            ref_df["GP 值"] = ref_df["GP 值"].apply(lambda x: f"{x:.1f}")
            # 保留原本的 Table 顯示方式
            st.table(ref_df)
