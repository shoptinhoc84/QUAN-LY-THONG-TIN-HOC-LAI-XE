import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# ==========================================================================================
# CẤU HÌNH HỆ THỐNG & GIAO DIỆN CHỦ
# ==========================================================================================
st.set_page_config(
    page_title="Hệ Thống Quản Lý Học Viên - Trung Tâm Lái Xe", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tiêu đề giao diện gốc của Streamlit
with st.container():
    st.title("HỆ THỐNG QUẢN LÝ & CƠ SỞ DỮ LIỆU HỌC VIÊN LÁI XE")
    st.caption("🔹 Hỗ trợ nghiệp vụ Trung tâm — Cập nhật Luật Sát hạch mới nhất 2026")
    st.markdown("---")

# Tên file lưu trữ dữ liệu mặc định của hệ thống
DATA_FILE = "database_khachhang.xlsx"

# Khai báo các cột chuẩn của hệ thống
COLUMNS_LIST = ["STT", "Họ tên", "Ngày sinh", "CCCD", "Số báo danh", "Số điện thoại", "Hạng xe", "Lựa xe", "Ngày thi", "Ghi chú"]

# Hàm khởi tạo hoặc tải dữ liệu từ file Excel
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

# Hàm lưu dữ liệu vào file Excel gốc
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# Khởi tạo dữ liệu vào bộ nhớ trang
if 'df_data' not in st.session_state:
    st.session_state.df_data = load_data()

# Danh sách hạng xe áp dụng từ năm 2026
HANG_XE_2026 = ["A1", "A", "B", "C1", "C", "D1", "D2", "D", "BE", "C1E", "CE", "D1E", "D2E", "DE"]

# Danh sách phân loại lựa xe
LOAI_XE_LIST = ["Xe số - Xe côn (Loại 1)", "Xe tay ga (Loại 2)"]

# Chia giao diện thành các Tab chức năng bằng hệ thống Tab lớn rõ ràng
tab1, tab2, tab3 = st.tabs([
    "📂 THÊM HỌC VIÊN MỚI", 
    "📝 TÌM KIẾM & CHỈNH SỬA", 
    "📊 XUẤT DỮ LIỆU IN ẤN"
])

# ==========================================================================================
# TAB 1: THÊM MỚI HỌC VIÊN (ĐÃ SỬA CƠ CHẾ GIỮ CHỮ KHI CÓ LỖI)
# ==========================================================================================
with tab1:
    st.subheader("📌 Mẫu Nhập Liệu Hồ Sơ Học Viên")
    st.info("💡 Hướng dẫn: Điền chính xác thông tin hồ sơ gốc của học viên. Các trường có dấu (*) là bắt buộc phải nhập.")
    
    # ĐÃ SỬA: Chuyển clear_on_submit=False để giữ lại chữ cũ khi có lỗi nhập sai
    with st.form("form_them_moi", clear_on_submit=False):
        
        # Cụm 1: Khung Thông tin cá nhân cơ bản
        st.markdown("#### 👤 1. THÔNG TIN CÁ NHÂN HỌC VIÊN")
        c1_1, c1_2, c1_3 = st.columns([2, 1, 1.5])
        with c1_1:
            ho_ten = st.text_input("Họ và tên học viên *", placeholder="Ví dụ: NGUYỄN VĂN A")
        with c1_2:
            ngay_sinh_dt = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
        with c1_3:
            cccd = st.text_input("Số CCCD (Bắt buộc nhập đủ 12 số) *", max_chars=12, placeholder="Gõ 12 số căn cước")
            
        st.markdown("---")
        
        # Cụm 2: Khung Thông tin Đăng ký đào tạo & Sát hạch
        st.markdown("#### 🚗 2. THÔNG TIN ĐĂNG KÝ HẠNG XE & THI")
        c2_1, c2_2, c2_3, c2_4 = st.columns(4)
        with c2_1:
            sdt = st.text_input("Số điện thoại *", max_chars=10, placeholder="Gõ 10 số điện thoại")
        with c2_2:
            hang_xe = st.selectbox("Hạng xe đào tạo (2026)", HANG_XE_2026)
        with c2_3:
            lura_xe = st.selectbox("Lựa chọn loại xe thi", LOAI_XE_LIST)
        with c2_4:
            sbd = st.text_input("Số báo danh (Nếu có)", placeholder="Chưa có điền trống")
            
        st.markdown("---")
        
        # Cụm 3: Khung Ghi chú bổ sung lịch trình hoặc học phí
        st.markdown("#### 📝 3. THÔNG TIN BỔ SUNG & GHI CHÚ")
        ghi_chu = st.text_area("Ghi chú hồ sơ trung tâm", placeholder="Ví dụ: Đã nộp đủ hồ sơ gốc, học viên xin học thực hành cuối tuần, đã đóng phí đợt 1...", height=100)
        
        # Nút xác nhận lưu
        st.write("")
        col_btn_1, col_btn_2 = st.columns([5, 1])
        with col_btn_2:
            submit_btn = st.form_submit_button("💾 LƯU HỒ SƠ", use_container_width=True)
        
        # Xử lý Logic chốt chặn định dạng dữ liệu
        if submit_btn:
            ho_ten_clean = ho_ten.strip().upper()  
            cccd_clean = cccd.strip()
            sdt_clean = sdt.strip()
            ghi_chu_clean = ghi_chu.strip()
            
            if not ho_ten_clean or not sdt_clean or not cccd_clean:
                st.error("❌ KHÔNG THỂ LƯU! Vui lòng điền đầy đủ 3 thông tin bắt buộc: Họ tên, CCCD và Số điện thoại.")
            elif not sdt_clean.isdigit() or len(sdt_clean) != 10 or not sdt_clean.startswith('0'):
                st.error(f"⚠️ SỐ ĐIỆN THOẠI SAI ĐỊNH DẠNG! Hệ thống đếm được {len(sdt_clean)} ký tự. Vui lòng kiểm tra lại ô Số điện thoại (yêu cầu đúng 10 số và bắt đầu bằng số 0).")
            elif not cccd_clean.isdigit() or len(cccd_clean) != 12:
                st.error(f"⚠️ SỐ CCCD SAI ĐỊNH DẠNG! Hệ thống đếm được {len(cccd_clean)} ký tự. Vui lòng kiểm tra lại ô Số CCCD (yêu cầu đúng 12 chữ số).")
            else:
                # Nếu tất cả THÀNH CÔNG -> Tiến hành lưu
                if len(st.session_state.df_data) == 0:
                    next_stt = 1
                else:
                    next_stt = int(st.session_state.df_data["STT"].max()) + 1
                
                ngay_sinh_str = ngay_sinh_dt.strftime("%d/%m/%Y")
                ngay_thi_dt = st.date_input("Ngày thi dự kiến", min_value=datetime.today(), format="DD/MM/YYYY") if 'ngay_thi_dt' not in locals() else ngay_thi_dt
                ngay_thi_str = ngay_thi_dt.strftime("%d/%m/%Y")
                
                new_row = {
                    "STT": next_stt,
                    "Họ tên": ho_ten_clean,
                    "Ngày sinh": ngay_sinh_str,
                    "CCCD": cccd_clean,
                    "Số báo danh": sbd.strip() if sbd else "Chưa có",
                    "Số điện thoại": sdt_clean,
                    "Hạng xe": hang_xe,
                    "Lựa xe": lura_xe,
                    "Ngày thi": ngay_thi_str,
                    "Ghi chú": ghi_chu_clean if ghi_chu_clean else ""
                }
                
                st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df_data)
                
                # Đăng ký thông báo thành công
                st.session_state.luu_thanh_cong = f"🎉 ĐÃ LƯU HỒ SƠ THÀNH CÔNG! Học viên: {ho_ten_clean} (STT hệ thống: {next_stt})"
                
                # ĐÃ SỬA: Ép trang web tự reset xóa sạch dữ liệu cũ khi thành công bằng cách kích hoạt cơ chế rerun
                st.rerun()

    # Giữ thông báo hiển thị sau khi trang làm mới lại thành công
    if 'luu_thanh_cong' in st.session_state:
        st.success(st.session_state.luu_thanh_cong)
        st.toast(st.session_state.luu_thanh_cong, icon="🎉")
        del st.session_state.luu_thanh_cong

# ==========================================================================================
# TAB 2: TÌM KIẾM VÀ CHỈNH SỬA TRỰC TIẾP
# ==========================================================================================
with tab2:
    st.subheader("🔍 Tìm Kiếm Học Viên & Điều Chỉnh Hồ Sơ Nhanh")
    
    df_current = st.session_state.df_data
    search_keyword = st.text_input("🔎 Nhập từ khóa cần tìm (Họ tên, CCCD, Số điện thoại hoặc Hạng xe):", placeholder="Gõ nội dung tìm kiếm vào đây...")
    
    if search_keyword:
        df_filtered = df_current[
            df_current["Họ tên"].str.contains(search_keyword, case=False, na=False) |
            df_current["CCCD"].astype(str).str.contains(search_keyword, na=False) |
            df_current["Số điện thoại"].astype(str).str.contains(search_keyword, na=False) |
            df_current["Hạng xe"].str.contains(search_keyword, case=False, na=False)
        ]
    else:
        df_filtered = df_current

    st.write("💡 *Mẹo thao tác trung tâm: Bạn có thể click đúp chuột thẳng vào ô dưới bảng để sửa chữ trực tiếp giống như Excel.*")
    
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic",
        key="data_editor_key",
        use_container_width=True
    )
    
    col_save_1, col_save_2 = st.columns([5, 1])
    with col_save_2:
        btn_save_changes = st.button("💾 CẬP NHẬT THAY ĐỔI", use_container_width=True)
        
    if btn_save_changes:
        if search_keyword:
            df_current.update(edited_df)
            st.session_state.df_data = df_current
        else:
            st.session_state.df_data = edited_df
            
        st.session_state.df_data["STT"] = pd.to_numeric(st.session_state.df_data["STT"]).astype(int)
        save_data(st.session_state.df_data)
        st.success("✅ Hệ thống đã ghi nhận toàn bộ chỉnh sửa mới vào file dữ liệu!")
        st.rerun()

# ==========================================================================================
# TAB 3: XUẤT FILE EXCEL ĐẸP IN ẤN 
# ==========================================================================================
with tab3:
    st.subheader("📋 Tùy Chọn Học Viên Để Xuất Danh Sách In Ấn")
    
    if len(st.session_state.df_data) > 0:
        base_df = st.session_state.df_data.fillna("")
        
        col_select_1, col_select_2 = st.columns([1, 4])
        with col_select_1:
            st.write("")
            st.write("")
            select_all = st.checkbox("Chọn tất cả học viên", value=True)
            
        with col_select_2:
            student_options = [f"{row['Họ tên']} - CCCD: {row['CCCD']}" for _, row in base_df.iterrows()]
            selected_students = st.multiselect(
                "💡 Chọn những ai muốn xuất file (Tìm kiếm nhanh bằng cách gõ tên):",
                options=student_options,
                default=student_options if select_all else []
            )
            
        if selected_students:
            selected_cccds = [item.split(" - CCCD: ")[1] for item in selected_students]
            display_df = base_df[base_df["CCCD"].isin(selected_cccds)].copy()
        else:
            display_df = pd.DataFrame(columns=COLUMNS_LIST)
            
        st.markdown(f"**Danh sách tải xuống hiện tại gồm có: `{len(display_df)}` học viên**")
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
                label=f"📥 TẢI FILE EXCEL IN ẤN ({len(display_df)} HỌC VIÊN ĐÃ CHỌN)",
                data=buffer.getvalue(),
                file_name=f"Danh_sach_in_an_rut_gon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Vui lòng tích chọn ít nhất 1 học viên ở ô phía trên để tạo nút tải file Excel.")
    else:
        st.info("📊 Hiện tại hệ thống cơ sở dữ liệu đang trống. Hãy nhập học viên mới ở Tab đầu tiên để xuất danh sách.")
