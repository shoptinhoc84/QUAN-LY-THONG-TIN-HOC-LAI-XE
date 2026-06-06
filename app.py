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

# Thiết lập phong cách hiển thị tiêu đề chính bằng màu sắc thương hiệu trung tâm
st.markdown("""
    <div style="background-color:#1F4E78; padding:20px; border-radius:10px; margin-bottom:25px">
        <h1 style="color:white; text-align:center; margin:0; font-family:'Times New Roman';">
            HỆ THỐNG QUẢN LÝ & CƠ SỞ DỮ LIỆU HỌC VIÊN LÁI XE
        </h1>
        <p style="color:#D9D9D9; text-align:center; margin:5px 0 0 0; font-size:14px;">
            Hỗ trợ nghiệp vụ Trung tâm - Cập nhật Luật Sát hạch mới nhất 2026
        </p>
    </div>
""", unsafe_allowed_html=True)

# Tên file lưu trữ dữ liệu mặc định của hệ thống
DATA_FILE = "database_khachhang.xlsx"

# Khai báo các cột chuẩn của hệ thống (Đã thêm cột Ghi chú)
COLUMNS_LIST = ["STT", "Họ tên", "Ngày sinh", "CCCD", "Số báo danh", "Số điện thoại", "Hạng xe", "Lựa xe", "Ngày thi", "Ghi chú"]

# Hàm khởi tạo hoặc tải dữ liệu từ file Excel
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            
            # Ép kiểu dữ liệu chuỗi text sạch để tránh Excel tự nhảy định dạng số
            for col in df.columns:
                if col in ["Ngày sinh", "Ngày thi", "CCCD", "Số điện thoại", "Số báo danh", "Lựa xe", "Ghi chú"]:
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Tự động đồng bộ cột mới nếu file cũ chưa có
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
# TAB 1: THÊM MỚI HỌC VIÊN (THIẾT KẾ PHONG CÁCH FORM CHUYÊN NGHIỆP)
# ==========================================================================================
with tab1:
    st.subheader("📌 Mẫu Nhập Liệu Hồ Sơ Học Viên")
    st.info("💡 Hướng dẫn: Điền chính xác thông tin hồ sơ gốc của học viên. Các trường có dấu (*) là bắt buộc phải nhập.")
    
    with st.form("form_them_moi", clear_on_submit=True):
        
        # Cụm 1: Khung Thông tin cá nhân cơ bản
        st.markdown("#### 👤 1. THÔNG TIN CÁ NHÂN HỌC VIÊN")
        c1_1, c1_2, c1_3 = st.columns([2, 1, 1.5])
        with c1_1:
            ho_ten = st.text_input("Họ và tên học viên *", placeholder="Ví dụ: NGUYỄN VĂN A")
        with c1_2:
            ngay_sinh_dt = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
        with c1_3:
            cccd = st.text_input("Số CCCD (Đủ 12 số) *", max_chars=12, placeholder="Gõ 12 số căn cước")
            
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
        ghi_chu = st.text_area("Ghi chú hồ sơ trung tâm", placeholder="Ví dụ: Đã nộp đủ hồ sơ gốc, học viên xin học thực hành cuối tuần, đã đóng phí đợt 1...", rows=3)
        
        # Nút xác nhận lưu được thiết kế căn lề phải gọn gàng, rõ nét
        st.write("")
        col_btn_1, col_btn_2 = st.columns([5, 1])
        with col_btn_2:
            submit_btn = st.form_submit_button("💾 LƯU HỒ SƠ", use_container_width=True)
        
        # Xử lý Logic và Chốt chặn định dạng dữ liệu
        if submit_btn:
            ho_ten_clean = ho_ten.strip().upper()  # Tự động viết hoa tên cho đẹp dữ liệu
            cccd_clean = cccd.strip()
            sdt_clean = sdt.strip()
            ghi_chu_clean = ghi_chu.strip()
            
            if not ho_ten_clean or not sdt_clean or not cccd_clean:
                st.error("❌ KHÔNG THỂ LƯU! Vui lòng điền đầy đủ 3 thông tin bắt buộc: Họ tên, CCCD và Số điện thoại.")
            elif not sdt_clean.isdigit() or len(sdt_clean) != 10 or not sdt_clean.startswith('0'):
                st.error(f"⚠️ SỐ ĐIỆN THOẠI SAI ĐỊNH DẠNG! Hệ thống đếm được {len(sdt_clean)} ký tự. Yêu cầu nhập đúng 10 số và bắt đầu bằng số 0.")
            elif not cccd_clean.isdigit() or len(cccd_clean) != 12:
                st.error(f"⚠️ SỐ CCCD SAI ĐỊNH DẠNG! Hệ thống đếm được {len(cccd_clean)} ký tự. Yêu cầu nhập đúng 12 chữ số.")
            else:
                # Tính số thứ tự tự động tăng liên tục
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
                
                st.session_state.luu_thanh_cong = f"🎉 ĐÃ LƯU HỒ SƠ THÀNH CÔNG! Học viên: {ho_ten_clean} (STT hệ thống: {next_stt})"
                st.rerun()

    # Giữ thông báo hiển thị sau khi trang reload
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
    
    # Bộ lọc tìm kiếm đa năng tích hợp bộ gõ thông minh
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
    
    # Hiển thị bảng dữ liệu tương tác thông minh
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
# TAB 3: XUẤT FILE EXCEL ĐẸP IN ẤN (TỐI ƯU CHO PHÒNG BAN VÀ GIÁO VIÊN)
# ==========================================================================================
with tab3:
    st.subheader("📋 Xem Trước & Tải Bảng Điểm/Danh Sách Sát Hạch")
    
    if len(st.session_state.df_data) > 0:
        st.dataframe(st.session_state.df_data, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_data.to_excel(writer, index=False, sheet_name='DANH SÁCH HỌC VIÊN')
            
            workbook  = writer.book
            worksheet = writer.sheets['DANH SÁCH HỌC VIÊN']
            
            # Định dạng cho Tiêu đề cột (Header) - Đậm đà, chuyên nghiệp
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#1F4E78',  # Xanh thẫm thương hiệu văn phòng
                'font_color': '#FFFFFF',
                'font_name': 'Times New Roman',
                'font_size': 12,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            # Định dạng ô căn giữa (STT, Ngày sinh, CCCD, SĐT, Ngày thi, Hạng, Loại xe)
            cell_center_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'font_size': 11,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            # Định dạng ô căn lề trái (Dành riêng cho Họ tên và Ghi chú dài)
            cell_left_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'font_size': 11,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            # Thiết lập độ cao dòng đầu tiêu đề
            worksheet.set_row(0, 30)
            
            for col_num, value in enumerate(st.session_state.df_data.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Duyệt cấu trúc kẻ bảng dữ liệu in ấn sạch sẽ
            for i, col in enumerate(st.session_state.df_data.columns):
                # Áp dụng căn lề logic: Tên và Ghi chú căn trái, còn lại căn giữa
                if col in ["Họ tên", "Ghi chú"]:
                    current_format = cell_left_format
                else:
                    current_format = cell_center_format
                
                for row_num in range(1, len(st.session_state.df_data) + 1):
                    val = st.session_state.df_data.iloc[row_num - 1, i]
                    # Xử lý tránh lưu giá trị rỗng/nan thành chữ lạ trên Excel
                    val_str = "" if pd.isna(val) or str(val) == "nan" else str(val)
                    worksheet.write(row_num, i, val_str, current_format)
                    worksheet.set_row(row_num, 24)  # Chiều cao hàng thoáng mát để ghi điểm hoặc ký tên
                
                # Tự động tính toán mở rộng cột dựa trên độ dài chuỗi chữ lớn nhất
                max_len = max(
                    st.session_state.df_data[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 5
                worksheet.set_column(i, i, max_len)
                
            # Thiết lập chế độ trang in tối ưu sẵn
            worksheet.set_landscape()     # In ngang khổ giấy để chứa hết tất cả các cột
            worksheet.set_paper(9)         # Chuẩn khổ giấy A4 văn phòng Việt Nam
            worksheet.fit_to_pages(1, 0)   # Tự động co giãn theo chiều ngang vừa khít 1 trang giấy
            
        st.write("")
        st.download_button(
            label="📥 TẢI FILE EXCEL IN ẤN (BẢN CHUẨN TRUNG TÂM)",
            data=buffer.getvalue(),
            file_name=f"Danh_sach_hoc_vien_trung_tam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("📊 Hiện tại hệ thống cơ sở dữ liệu đang trống. Hãy nhập học viên mới ở Tab đầu tiên để xuất danh sách.")
