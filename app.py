import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Quản Lý Thông Tin Khách Hàng", layout="wide")
st.title("ỨNG DỤNG QUẢN LÝ THÔNG TIN HỌC VIÊN LÁI XE")

# Tên file lưu trữ dữ liệu mặc định
DATA_FILE = "database_khachhang.xlsx"

# Hàm khởi tạo hoặc tải dữ liệu từ file Excel
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_excel(DATA_FILE)
        except Exception:
            # Nếu file lỗi hoặc trống, tạo mới dataframe
            return pd.DataFrame(columns=["STT", "Họ tên", "Ngày sinh", "Số báo danh", "Số điện thoại", "Hạng xe"])
    else:
        return pd.DataFrame(columns=["STT", "Họ tên", "Ngày sinh", "Số báo danh", "Số điện thoại", "Hạng xe"])

# Hàm lưu dữ liệu vào file Excel
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# Tải dữ liệu vào session_state của Streamlit để quản lý trạng thái
if 'df_data' not in st.session_state:
    st.session_state.df_data = load_data()

# Chia giao diện thành các Tab chức năng
tab1, tab2, tab3 = st.tabs(["➕ Thêm Học Viên Mới", "🔍 Tìm Kiếm & Chỉnh Sửa", "📥 Xuất Excel"])

# ------------------------------------------------------------------------------------------
# TAB 1: THÊM MỚI HỌC VIÊN
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("Nhập thông tin học viên mới")
    
    with st.form("form_them_moi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ho_ten = st.text_input("Họ và tên *")
            ngay_sinh = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today())
            sbd = st.text_input("Số báo danh (SBD)")
        with col2:
            sdt = st.text_input("Số điện thoại *")
            hang_xe = st.selectbox("Hạng xe", ["A1", "A2", "B1", "B2", "C", "D", "E", "FC"])
            
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
                
                # Tạo bản ghi mới
                new_row = {
                    "STT": next_stt,
                    "Họ tên": ho_ten.strip(),
                    "Ngày sinh": ngay_sinh.strftime("%d/%m/%Y"),
                    "Số báo danh": sbd.strip() if sbd else "Chưa có",
                    "Số điện thoại": sdt.strip(),
                    "Hạng xe": hang_xe
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

    # Hiển thị bảng dữ liệu (Cho phép sửa trực tiếp bằng data_editor)
    st.write("💡 *Bạn có thể click đúp trực tiếp vào ô trong bảng dưới đây để sửa nhanh, hoặc tích chọn hàng để xóa.*")
    
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic", # Cho phép thêm/xóa dòng trực tiếp tại bảng nếu muốn
        key="data_editor_key",
        use_container_width=True
    )
    
    # Nút bấm để xác nhận lưu các thay đổi vừa sửa trên bảng
    if st.button("Xác nhận lưu thay đổi đã sửa"):
        # Cập nhật lại những dòng đã lọc vào data gốc
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
        
        # Chuyển đổi dataframe thành dữ liệu excel để tải về
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