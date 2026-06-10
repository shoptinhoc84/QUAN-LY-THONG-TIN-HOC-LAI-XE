import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import re
from PIL import Image
import numpy as np

# ==========================================================================================
# CẤU HÌNH GIAO DIỆN CHỦ & PHONG CÁCH ĐỒ HỌA SANG TRỌNG
# ==========================================================================================
st.set_page_config(
    page_title="Hệ Thống Quản Lý Học Viên - Trung Tâm Lái Xe", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stDataFrame {
        border: 1px solid #E6EBF5;
        border-radius: 8px;
        overflow: hidden;
    }
    .main-title {
        font-size: 2.2rem;
        color: #1F4E78;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429215.png", width=80)
    st.markdown("### **HỆ THỐNG TRUNG TÂM**")
    st.caption("Phiên bản quản lý chuyên nghiệp năm 2026")
    st.markdown("---")
    DATA_FILE = st.text_input("Tên file lưu trữ gốc", value="database_khachhang.xlsx")
    st.markdown("---")
    st.info("💡 **Mẹo nhỏ:** Nếu ảnh CCCD chụp bằng điện thoại quá nặng, hãy cắt bớt phần thừa xung quanh thẻ trước khi tải lên để AI đọc nhanh và chuẩn nhất.")

st.markdown('<p class="main-title">HỆ THỐNG QUẢN LÝ & CƠ SỞ DỮ LIỆU HỌC VIÊN LÁI XE</p>', unsafe_allow_html=True)
st.caption("🔹 Nền tảng nghiệp vụ lưu trữ đồng bộ hành chính — Cập nhật Luật Sát hạch 2026")
st.markdown("---")

COLUMNS_LIST = ["STT", "Họ tên", "Ngày sinh", "CCCD", "Số báo danh", "Số điện thoại", "Hạng xe", "Lựa xe", "Ngày thi", "Ghi chú"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            df = df.fillna("")
            for col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            for col in COLUMNS_LIST:
                if col not in df.columns:
                    df[col] = "Chưa có" if col != "Ghi chú" else ""
            return df[COLUMNS_LIST]
        except Exception:
            return pd.DataFrame(columns=COLUMNS_LIST)
    else:
        return pd.DataFrame(columns=COLUMNS_LIST)

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

@st.cache_resource(show_spinner=False)
def get_ocr_reader():
    try:
        import easyocr
        return easyocr.Reader(['vi', 'en'], gpu=False)
    except Exception:
        return None

# --- BỘ NÃO QUÉT ẢNH CCCD THÔNG MINH MỚI ---
def extract_cccd_info(image_bytes):
    reader = get_ocr_reader()
    if reader is None:
        return "CHƯA CÀI THƯ VIỆN OCR", None, ""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Đọc chi tiết để lấy text kèm vị trí dòng giải quyết bài toán lệch hàng
        results = reader.readtext(image_np, detail=0)
        
        # Làm sạch mảng ký tự nhận diện được
        cleaned_results = [text.strip() for text in results if text.strip()]
        full_text_combined = " ".join(cleaned_results)
        
        cccd_number = ""
        fullname = ""
        dob = None
        
        # 1. CHIẾN LƯỢC QUÉT SỐ CCCD (Tìm chuỗi 12 chữ số, lọc bỏ dấu cách nhiễu)
        # Quét diện rộng loại bỏ khoảng trắng giả do lóa sáng
        collapsed_text = re.sub(r'\s+', '', full_text_combined)
        match_cccd = re.search(r'\b\d{12}\b', collapsed_text)
        if match_cccd:
            cccd_number = match_cccd.group(0)
        else:
            # Tìm kiếm dự phòng nếu dính chữ
            match_loose = re.search(r'\d{12}', collapsed_text)
            if match_loose:
                cccd_number = match_loose.group(0)
            
        # 2. CHIẾN LƯỢC QUÉT NGÀY SINH (dd/mm/yyyy)
        match_dob = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', full_text_combined)
        if match_dob:
            try:
                dob = datetime.strptime(match_dob.group(1), "%d/%m/%Y")
            except ValueError:
                pass

        # 3. CHIẾN LƯỢC QUÉT HỌ TÊN NÂNG CAO (Quét mốc tọa độ từ khóa văn bản)
        # Bước A: Tìm vị trí dòng tiêu đề liên quan đến Tên
        name_anchor_idx = -1
        for idx, text in enumerate(cleaned_results):
            t_upper = text.upper()
            if "HỌ VÀ TÊN" in t_upper or "FULL NAME" in t_upper or "TÊN /" in t_upper:
                name_anchor_idx = idx
                break
                
        # Bước B: Nếu tìm thấy mốc tiêu đề, người đó thường nằm ở 1 hoặc 2 dòng ngay kế dưới
        if name_anchor_idx != -1:
            for offset in [1, 2]:
                if name_anchor_idx + offset < len(cleaned_results):
                    candidate = cleaned_results[name_anchor_idx + offset]
                    # Tên phải viết HOA hoàn toàn và không được chứa số
                    if candidate.isupper() and len(candidate.split()) >= 2 and not any(c.isdigit() for c in candidate):
                        if "CỘNG HÒA" not in candidate and "ĐỘC LẬP" not in candidate:
                            fullname = candidate
                            break
                            
        # Bước C: Phương án dự phòng (Nếu không tìm thấy mốc chữ, quét toàn bộ dòng viết HOA giống bản cũ)
        if not fullname:
            for text in cleaned_results:
                if text.isupper() and len(text.split()) >= 2 and not any(c.isdigit() for c in text):
                    # Khử từ khóa hệ thống quốc hiệu tiêu đề hành chính
                    if not any(k in text for k in ["CỘNG HÒA", "ĐỘC LẬP", "CĂN CƯỚC", "CHỨNG NHẬN", "CỤC TRƯỞNG", "GIÁM ĐỐC"]):
                        fullname = text
                        break
                        
        return fullname, dob, cccd_number
    except Exception:
        return "", None, ""

# Khởi tạo dữ liệu vào bộ nhớ trang
if 'df_data' not in st.session_state:
    st.session_state.df_data = load_data()

if 'ocr_name' not in st.session_state: st.session_state.ocr_name = ""
if 'ocr_id' not in st.session_state: st.session_state.ocr_id = ""
if 'ocr_dob' not in st.session_state: st.session_state.ocr_dob = datetime(2000, 1, 1)

HANG_XE_2026 = ["A1", "A", "B", "C1", "C", "D1", "D2", "D", "BE", "C1E", "CE", "D1E", "D2E", "DE"]
LOAI_XE_LIST = ["Xe số - Xe côn (Loại 1)", "Xe tay ga (Loại 2)"]

tab1, tab2, tab3 = st.tabs([
    "📥 THÊM HỌC VIÊN LÀM HỒ SƠ", 
    "📝 TRA CỨU & CẬP NHẬT NHANH", 
    "📊 QUẢN LÝ TRÍCH XUẤT FILE IN"
])

# ==========================================================================================
# TAB 1: THÊM MỚI HỌC VIÊN
# ==========================================================================================
with tab1:
    with st.expander("📸 CÔNG CỤ XỬ LÝ NHANH: QUÉT THÔNG TIN TỪ ẢNH CĂN CƯỚC CÔNG DÂN (CCCD)", expanded=True):
        st.markdown("<small style='color: gray;'>Hệ thống AI tích hợp hỗ trợ đọc file ảnh mặt trước của thẻ căn cước để tự động điền biểu mẫu, tiết kiệm thời gian nhập tay.</small>", unsafe_allow_html=True)
        st.write("")
        
        col_file, col_preview = st.columns([2, 1])
        with col_file:
            uploaded_card = st.file_uploader("Kéo thả hoặc chọn file ảnh chụp thẻ CCCD học viên...", type=["jpg", "jpeg", "png"], key="cccd_scanner")
            st.write("")
            if uploaded_card:
                if st.button("⚡ TIẾN HÀNH QUÉT ẢNH TỰ ĐỘNG", use_container_width=True, type="primary"):
                    with st.spinner("Đang chạy thuật toán AI phân tích hình ảnh..."):
                        img_bytes = uploaded_card.read()
                        ocr_name, ocr_dob, ocr_id = extract_cccd_info(img_bytes)
                        
                        if ocr_name or ocr_id:
                            if ocr_name: st.session_state.ocr_name = ocr_name
                            if ocr_id: st.session_state.ocr_id = ocr_id
                            if ocr_dob: st.session_state.ocr_dob = ocr_dob
                            st.success("🎉 Đã bóc tách dữ liệu ảnh thành công! Các ô nhập liệu ở dưới đã sẵn sàng.")
                            st.rerun()
                        else:
                            st.error("⚠️ Không tìm thấy thông tin hợp lệ trên ảnh! Xin vui lòng kiểm tra lại góc chụp thẳng, đủ sáng hoặc tự nhập tay vào biểu mẫu bên dưới.")
        with col_preview:
            if uploaded_card:
                st.image(uploaded_card, caption="Ảnh CCCD đã chọn", width=200)
            else:
                st.markdown("<div style='border: 2px dashed #D9D9D9; border-radius: 8px; padding: 30px; text-align: center; color: #A0A0A0; font-size: 13px;'>Chưa có ảnh tải lên</div>", unsafe_allow_html=True)

    st.write("")
    
    with st.form("form_them_moi", clear_on_submit=False):
        st.markdown("#### 👤 1. HỒ SƠ LÝ LỊCH CÁ NHÂN")
        c1_1, c1_2, c1_3 = st.columns([2, 1, 1.5])
        with c1_1:
            ho_ten = st.text_input("Họ và tên học viên *", value=st.session_state.ocr_name, placeholder="VÍ DỤ: NGUYỄN VĂN A")
        with c1_2:
            ngay_sinh_dt = st.date_input("Ngày sinh", value=st.session_state.ocr_dob, min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
        with c1_3:
            cccd = st.text_input("Số thẻ CCCD *", value=st.session_state.ocr_id, max_chars=12, placeholder="Nhập chuẩn đủ 12 chữ số")
        
        st.markdown("---")
        
        st.markdown("#### 🚗 2. THÔNG TIN ĐĂNG KÝ HẠNG XE & ĐÀO TẠO")
        c2_1, c2_2, c2_3, c2_4 = st.columns(4)
        with c2_1:
            sdt = st.text_input("Số điện thoại liên hệ *", max_chars=10, placeholder="Nhập 10 số di động")
        with c2_2:
            hang_xe = st.selectbox("Hạng xe đào tạo đăng ký", HANG_XE_2026)
        with c2_3:
            lura_xe = st.selectbox("Phân loại dòng xe thi", LOAI_XE_LIST)
        with c2_4:
            ngay_thi_dt = st.date_input("Ngày thi sát hạch dự kiến", min_value=datetime.today(), format="DD/MM/YYYY")
                
        st.markdown("---")
        
        st.markdown("#### 📝 3. THÔNG TIN BỔ SUNG KHÁC")
        c3_1, c3_2 = st.columns([3, 1])
        with c3_1:
            ghi_chu = st.text_area("Ghi chú nội bộ của trung tâm", placeholder="Ví dụ: Đã nộp đầy đủ hồ sơ ảnh chụp, thu trước học phí đợt 1...", height=80)
        with c3_2:
            sbd = st.text_input("Số báo danh cấp (SBD)", placeholder="Chưa cấp để trống")
        
        st.write("")
        col_space, col_save_btn = st.columns([4, 1])
        with col_save_btn:
            submit_btn = st.form_submit_button("💾 LƯU CHỨNG HỒ SƠ", use_container_width=True)
        
        if submit_btn:
            ho_ten_clean = ho_ten.strip().upper()  
            cccd_clean = cccd.strip()
            sdt_clean = sdt.strip()
            ghi_chu_clean = ghi_chu.strip()
            sbd_clean = sbd.strip() if sbd else "Chưa có"
            
            if not ho_ten_clean or not sdt_clean or not cccd_clean:
                st.error("❌ THẤT BẠI: Vui lòng điền đầy đủ 3 trường thông tin cốt lõi bắt buộc (*): Họ tên, Số CCCD và Số điện thoại.")
            elif not sdt_clean.isdigit() or len(sdt_clean) != 10 or not sdt_clean.startswith('0'):
                st.error(f"⚠️ SAI ĐỊNH DẠNG SĐT: Yêu cầu nhập đúng chuỗi 10 ký số di động.")
            elif not cccd_clean.isdigit() or len(cccd_clean) != 12:
                st.error(f"⚠️ SAI ĐỊNH DẠNG CCCD: Yêu cầu chuỗi nhập vào phải đúng cấu trúc định danh 12 số định danh công dân gốc.")
            else:
                if len(st.session_state.df_data) == 0:
                    next_stt = 1
                else:
                    next_stt = int(st.session_state.df_data["STT"].max()) + 1
                
                ngay_sinh_str = ngay_sinh_dt.strftime("%d/%m/%Y")
                ngay_thi_str = ngay_thi_dt.strftime("%d/%m/%Y")
                
                new_row = {
                    "STT": next_stt, "Họ tên": ho_ten_clean, "Ngày sinh": ngay_sinh_str, "CCCD": cccd_clean,
                    "Số báo danh": sbd_clean, "Số điện thoại": sdt_clean, "Hạng xe": hang_xe, "Lựa xe": lura_xe,
                    "Ngày thi": ngay_thi_str, "Ghi chú": ghi_chu_clean
                }
                
                st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df_data)
                
                st.session_state.ocr_name = ""
                st.session_state.ocr_id = ""
                st.session_state.ocr_dob = datetime(2000, 1, 1)
                
                st.session_state.luu_thanh_cong = f"🎉 ĐÃ ĐỒNG BỘ THÀNH CÔNG: Hồ sơ học viên {ho_ten_clean} đã xếp gọn vào hệ thống Excel (STT: {next_stt})"
                st.rerun()

    if 'luu_thanh_cong' in st.session_state:
        st.success(st.session_state.luu_thanh_cong)
        st.toast(st.session_state.luu_thanh_cong, icon="🎉")
        del st.session_state.luu_thanh_cong

# ==========================================================================================
# TAB 2: TÌM KIẾM VÀ CHỈNH SỬA TRỰC TIẾP
# ==========================================================================================
with tab2:
    st.subheader("🔍 Thanh Tra Cứu Bộ Lọc Hồ Sơ Toàn Hệ Thống")
    
    df_current = st.session_state.df_data
    search_keyword = st.text_input("🔎 Bộ lọc thông minh nhanh (Tìm theo Tên, CCCD, Số điện thoại hoặc Hạng xe):", placeholder="Gõ tên hoặc số thẻ căn cước cần chỉnh sửa...")
    
    if search_keyword:
        df_filtered = df_current[
            df_current["Họ tên"].str.contains(search_keyword, case=False, na=False) |
            df_current["CCCD"].astype(str).str.contains(search_keyword, na=False) |
            df_current["Số điện thoại"].astype(str).str.contains(search_keyword, na=False) |
            df_current["Hạng xe"].str.contains(search_keyword, case=False, na=False)
        ]
    else:
        df_filtered = df_current

    st.write("<small style='color: #1F4E78;'>💡 <b>Mẹo thao tác nhanh:</b> Nhấp đúp trực tiếp vào ô để sửa dữ liệu văn bản. Để xóa toàn bộ một hàng học viên, hãy nhấp chọn ô đầu dòng đó rồi bấm nút <b>Delete</b> trên bàn phím của bạn.</small>", unsafe_allow_html=True)
    st.write("")
    
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic",
        key="data_editor_key",
        use_container_width=True
    )
    
    st.write("")
    col_save_1, col_save_2 = st.columns([5, 1])
    with col_save_2:
        btn_save_changes = st.button("💾 ĐỒNG BỘ BẢNG SỬA ĐỔI", use_container_width=True, type="primary")
        
    if btn_save_changes:
        if search_keyword:
            deleted_indices = df_filtered.index.difference(edited_df.index)
            df_current = df_current.drop(deleted_indices)
            df_current.update(edited_df)
            st.session_state.df_data = df_current
        else:
            st.session_state.df_data = edited_df
            
        st.session_state.df_data["Họ tên"] = st.session_state.df_data["Họ tên"].astype(str).str.upper().str.strip()
        st.session_state.df_data = st.session_state.df_data.reset_index(drop=True)
        st.session_state.df_data["STT"] = range(1, len(st.session_state.df_data) + 1)
        
        save_data(st.session_state.df_data)
        st.success("✅ THÀNH CÔNG: Toàn bộ dữ liệu chỉnh sửa đã được đồng bộ chuẩn hóa vào file gốc!")
        st.rerun()

# ==========================================================================================
# TAB 3: XUẤT FILE EXCEL ĐẸP IN ẤN
# ==========================================================================================
with tab3:
    st.subheader("📋 Xuất Danh Sách Hồ Sơ In Ấn Hành Chính")
    
    if len(st.session_state.df_data) > 0:
        base_df = st.session_state.df_data.fillna("")
        
        col_select_1, col_select_2 = st.columns([1.2, 4])
        with col_select_1:
            st.write("")
            st.write("")
            select_all = st.checkbox("Chọn in toàn bộ danh sách hiện tại", value=True)
            
        with col_select_2:
            student_options = [f"{row['Họ tên']} - CCCD: {row['CCCD']}" for _, row in base_df.iterrows()]
            selected_students = st.multiselect(
                "💡 Chọn lọc riêng danh sách từng học viên cần in file:",
                options=student_options,
                default=student_options if select_all else []
            )
            
        if selected_students:
            selected_cccds = [item.split(" - CCCD: ")[1] for item in selected_students]
            display_df = base_df[base_df["CCCD"].isin(selected_cccds)].copy()
        else:
            display_df = pd.DataFrame(columns=COLUMNS_LIST)
            
        st.markdown(f"📊 **Tổng số lượng bản ghi trích xuất dữ liệu: `{len(display_df)}` học viên**")
        st.dataframe(display_df, use_container_width=True)
        
        if len(display_df) > 0:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                display_df.to_excel(writer, index=False, sheet_name='DANH SÁCH CHỌN IN')
                
                workbook  = writer.book
                worksheet = writer.sheets['DANH SÁCH CHỌN IN']
                
                header_format = workbook.add_format({
                    'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center',
                    'fg_color': '#1F4E78', 'font_color': '#FFFFFF', 'font_name': 'Times New Roman',
                    'font_size': 12, 'border': 1, 'border_color': '#D9D9D9'
                })
                
                cell_center_format = workbook.add_format({
                    'align': 'center', 'valign': 'vcenter', 'font_name': 'Times New Roman',
                    'font_size': 11, 'border': 1, 'border_color': '#D9D9D9'
                })
                
                cell_left_format = workbook.add_format({
                    'align': 'left', 'valign': 'vcenter', 'font_name': 'Times New Roman',
                    'font_size': 11, 'border': 1, 'border_color': '#D9D9D9'
                })
                
                worksheet.set_row(0, 30)
                for col_num, value in enumerate(display_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                for i, col in enumerate(display_df.columns):
                    if col in ["Họ tên", "Ghi chú"]:
                        current_format = cell_left_format
                    else:
                        current_format = cell_center_format
                    
                    for row_num in range(1, len(display_df) + 1):
                        val = display_df.iloc[row_num - 1, i]
                        val_str = "" if pd.isna(val) or str(val) == "nan" else str(val).strip()
                        worksheet.write(row_num, i, val_str, current_format)
                        worksheet.set_row(row_num, 24)
                    
                    col_series = display_df[col].astype(str).fillna("")
                    max_len = max(col_series.map(len).max() if not col_series.empty else 0, len(str(col))) + 5
                    worksheet.set_column(i, i, max_len)
                    
                worksheet.set_landscape()
                worksheet.set_paper(9)
                worksheet.fit_to_pages(1, 0)
                
            st.write("")
            st.download_button(
                label=f"📥 TẢI XUẤT FILE EXCEL PHÁT HÀNH ({len(display_df)} HỌC VIÊN)",
                data=buffer.getvalue(),
                file_name=f"Danh_sach_in_an_rut_gon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Vui lòng tick chọn ít nhất 1 học viên ở ô phía trên để tạo nút tải file Excel.")
    else:
        st.info("📊 Hiện tại hệ thống cơ sở dữ liệu trống. Vui lòng nhập học viên mới ở Tab đầu tiên.")
