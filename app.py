import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Quản Lý Thông Tin Học Viên", layout="wide")
st.title("ỨNG DỤNG QUẢN LÝ THÔNG TIN HỌC VIÊN LÁI XE (CẬP NHẬT 2026)")

# Tên file lưu trữ dữ liệu mặc định
DATA_FILE = "database_khachhang.xlsx"

# Khai báo các cột chuẩn của hệ thống
COLUMNS_LIST = ["STT", "Họ tên", "Ngày sinh", "Số báo danh", "Số điện thoại", "Hạng xe", "Ngày thi"]

# Hàm khởi tạo hoặc tải dữ liệu từ file Excel
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            # Đảm bảo các cột ngày tháng luôn ở dạng chuỗi để không bị Excel tự định dạng lại
            if "Ngày sinh" in df.columns:
                df["Ngày sinh"] = df["Ngày sinh"].astype(str)
            if "Ngày thi" in df.columns:
                df["Ngày thi"] = df["Ngày thi"].astype(str)
            
            # Kiểm tra và bổ sung cột thiếu nếu file cũ không có
            for col in COLUMNS_LIST:
                if col not in df.columns:
                    df[col] = "Chưa có"
            return df[COLUMNS_LIST]
        except Exception:
            return pd.DataFrame(columns=COLUMNS_LIST)
    else:
        return pd.DataFrame(columns=COLUMNS_LIST)

# Hàm lưu dữ liệu vào file Excel
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# Tải dữ liệu vào session_state của Streamlit để quản lý trạng thái
if 'df_data' not in st.session_state:
    st.session_state.df_data = load_data()

# Chia giao diện thành các Tab chức năng
tab1, tab2, tab3 = st.tabs(["➕ Thêm Học Viên Mới", "🔍 Tìm Kiếm & Chỉnh Sửa", "📥 Xuất Excel"])

# Danh sách hạng xe mới áp dụng từ năm 2026
HANG_XE_2026 = ["A1", "A", "B", "C1", "C", "D1", "D2", "D", "BE", "C1E", "CE", "D1E", "D2E", "DE"]

# ------------------------------------------------------------------------------------------
# TAB 1: THÊM MỚI HỌC VIÊN
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("Nhập thông tin học viên mới")
    
    with st.form("form_them_moi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ho_ten = st.text_input("Họ và tên *")
            # Chọn ngày sinh - mặc định hiển thị định dạng ngày/tháng/năm trên web
            ngay_sinh_dt = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
            sbd = st.text_input("Số báo danh (SBD)")
        with col2:
            sdt = st.text_input("Số điện thoại *")
            hang_xe = st.selectbox("Hạng xe (Luật mới 2026)", HANG_XE_2026)
            ngay_thi_dt = st.date_input("Ngày thi dự kiến", min_value=datetime.today(), format="DD/MM/YYYY")
            
        submit_btn = st.form_submit_button("Lưu hệ thống")
        
        if submit_btn:
            if not ho_ten or not sdt:
                st.error("Vui lòng điền đầy đủ các thông tin bắt buộc (*)")
            else:
                # Tính số thứ tự (STT) tự động tăng
                if len(st.session_state.df_data) == 0:
                    next_stt = 1
                else:
                    next_stt = int(st.session_state.df_data["STT"].max()) + 1
                
                # Ép định dạng ngày về chuẩn Ngày/Tháng/Năm trước khi lưu
                ngay_sinh_str = ngay_sinh_dt.strftime("%d/%m/%Y")
                ngay_thi_str = ngay_thi_dt.strftime("%d/%m/%Y")
                
                # Tạo bản ghi mới
                new_row = {
                    "STT": next_stt,
                    "Họ tên": ho_ten.strip(),
                    "Ngày sinh": ngay_sinh_str,
                    "Số báo danh": sbd.strip() if sbd else "Chưa có",
                    "Số điện thoại": sdt.strip(),
                    "Hạng xe": hang_xe,
                    "Ngày thi": ngay_thi_str
                }
                
                # Thêm vào dataframe và lưu file
                st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df_data)
                st.success(f"Đã lưu thành công học viên: {ho_ten} (STT: {next_stt})")

# ------------------------------------------------------------------------------------------
# TAB 2: TÌM KIẾM VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("Danh sách & Chỉnh sửa thông tin")
    
    df_current = st.session_state.df_data
    
    # Bộ lọc tìm kiếm nhanh
    search_keyword = st.text_input("🔍 Nhập Họ tên hoặc Số điện thoại để tìm kiếm:")
    
    if search_keyword:
        df_filtered = df_current[
            df_current["Họ tên"].str.contains(search_keyword, case=False, na=False) |
            df_current["Số điện thoại"].astype(str).str.contains(search_keyword, na=False)
        ]
    else:
        df_filtered = df_current

    st.write("💡 *Bạn có thể click đúp trực tiếp vào ô trong bảng dưới đây để sửa nhanh, hoặc tích chọn hàng để xóa.*")
    
    # Sử dụng data_editor chỉnh sửa trực tiếp, ép kiểu cột Ngày tháng thành chuỗi để tránh bị đảo lộn
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic",
        key="data_editor_key",
        use_container_width=True
    )
    
    # Nút bấm để xác nhận lưu các thay đổi
    if st.button("Xác nhận lưu thay đổi đã sửa"):
        if search_keyword:
            df_current.update(edited_df)
            st.session_state.df_data = df_current
        else:
            st.session_state.df_data = edited_df
            
        save_data(st.session_state.df_data)
        st.success("Đã cập nhật thay đổi thành công vào file hệ thống!")
        st.rerun()

# ------------------------------------------------------------------------------------------
# TAB 3: XUẤT FILE EXCEL
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("Xuất dữ liệu ra file Excel")
    
    if len(st.session_state.df_data) > 0:
        st.dataframe(st.session_state.df_data, use_container_width=True)
        
        # Chuyển đổi dữ liệu sang excel dạng nhị phân để tải trực tiếp trên trình duyệt
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_data.to_excel(writer, index=False, sheet_name='DanhSachHocVien')
            
        st.download_button(
            label="📥 Tải file Excel về máy (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Danh_sach_hoc_vien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("Hiện tại chưa có dữ liệu nào để xuất.")
