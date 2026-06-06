import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# Cấu hình trang
st.set_page_config(page_title="Quản Lý Thông Tin Học Viên", layout="wide")
st.title("ỨNG DỤNG QUẢN LÝ THÔNG TIN HỌC VIÊN LÁI XE (CẬP NHẬT 2026)")

# Tên file lưu trữ dữ liệu mặc định
DATA_FILE = "database_khachhang.xlsx"

# Khai báo các cột chuẩn của hệ thống
COLUMNS_LIST = ["STT", "Họ tên", "Ngày sinh", "CCCD", "Số báo danh", "Số điện thoại", "Hạng xe", "Ngày thi"]

# Hàm khởi tạo hoặc tải dữ liệu từ file Excel
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            
            # Kiểm tra và chuyển đổi dữ liệu sang dạng chuỗi text để tránh mất số 0 hoặc lỗi định dạng
            for col in df.columns:
                if col in ["Ngày sinh", "Ngày thi", "CCCD", "Số điện thoại", "Số báo danh"]:
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Kiểm tra và bổ sung cột thiếu nếu dữ liệu cũ chưa có
            for col in COLUMNS_LIST:
                if col not in df.columns:
                    df[col] = "Chưa có"
            return df[COLUMNS_LIST]
        except Exception:
            return pd.DataFrame(columns=COLUMNS_LIST)
    else:
        return pd.DataFrame(columns=COLUMNS_LIST)

# Hàm lưu dữ liệu vào file Excel gốc
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# Tải dữ liệu vào session_state của Streamlit để quản lý trạng thái
if 'df_data' not in st.session_state:
    st.session_state.df_data = load_data()

# Khai báo các Tab chức năng
tab1, tab2, tab3 = st.tabs(["➕ Thêm Học Viên Mới", "🔍 Tìm Kiếm & Chỉnh Sửa", "📥 Xuất Excel In Ấn"])

# Danh sách hạng xe mới áp dụng từ năm 2026
HANG_XE_2026 = ["A1", "A", "B", "C1", "C", "D1", "D2", "D", "BE", "C1E", "CE", "D1E", "D2E", "DE"]

# ------------------------------------------------------------------------------------------
# TAB 1: THÊM MỚI HỌC VIÊN (ĐÃ KHÓA CHẶT ĐỊNH DẠNG 10 SỐ VÀ 12 SỐ)
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("Nhập thông tin học viên mới")
    
    with st.form("form_them_moi", clear_on_submit=False): 
        col1, col2 = st.columns(2)
        with col1:
            ho_ten = st.text_input("Họ và tên *")
            ngay_sinh_dt = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
            # max_chars=12 ngăn không cho gõ ký tự thứ 13
            cccd = st.text_input("Số CCCD (Bắt buộc nhập đủ 12 số) *", max_chars=12, help="Nhập chính xác 12 chữ số")
            sbd = st.text_input("Số báo danh (SBD)")
        with col2:
            # max_chars=10 ngăn không cho gõ ký tự thứ 11
            sdt = st.text_input("Số điện thoại (Bắt buộc nhập đủ 10 số) *", max_chars=10, help="Nhập chính xác 10 chữ số bắt đầu từ số 0")
            hang_xe = st.selectbox("Hạng xe (Luật mới 2026)", HANG_XE_2026)
            ngay_thi_dt = st.date_input("Ngày thi dự kiến", min_value=datetime.today(), format="DD/MM/YYYY")
            
        submit_btn = st.form_submit_button("Lưu vào hệ thống")
        
        if submit_btn:
            # Làm sạch khoảng trắng thừa
            ho_ten_clean = ho_ten.strip()
            cccd_clean = cccd.strip()
            sdt_clean = sdt.strip()
            
            # 1. Kiểm tra bỏ trống
            if not ho_ten_clean or not sdt_clean or not cccd_clean:
                st.error("❌ Vui lòng điền đầy đủ các thông tin bắt buộc (* gồm Họ tên, CCCD, Số điện thoại)")
            
            # 2. KHÓA ĐỊNH DẠNG SỐ ĐIỆN THOẠI: Phải hoàn toàn là số, bắt đầu bằng 0 VÀ PHẢI ĐỦ 10 KÝ TỰ
            elif not sdt_clean.isdigit() or len(sdt_clean) != 10 or not sdt_clean.startswith('0'):
                st.error(f"⚠️ SỐ ĐIỆN THOẠI KHÔNG HỢP LỆ! Bạn hiện nhập {len(sdt_clean)} ký tự. Vui lòng nhập ĐÚNG và ĐỦ 10 chữ số (bắt đầu bằng số 0).")
            
            # 3. KHÓA ĐỊNH DẠNG CCCD: Phải hoàn toàn là số VÀ PHẢI ĐỦ 12 KÝ TỰ
            elif not cccd_clean.isdigit() or len(cccd_clean) != 12:
                st.error(f"⚠️ SỐ CCCD KHÔNG HỢP LỆ! Bạn hiện nhập {len(cccd_clean)} ký tự. Căn cước công dân phải nhập ĐÚNG và ĐỦ 12 chữ số.")
                
            else:
                # Nếu tất cả dữ liệu đều chuẩn xác 100% -> tiến hành lưu
                if len(st.session_state.df_data) == 0:
                    next_stt = 1
                else:
                    next_stt = int(st.session_state.df_data["STT"].max()) + 1
                
                ngay_sinh_str = ngay_sinh_dt.strftime("%d/%m/%Y")
                ngay_thi_str = ngay_thi_dt.strftime("%d/%m/%Y")
                
                new_row = {
                    "STT": next_stt,
                    "Họ tên": ho_ten_clean,
                    "Ngày sinh": ngay_sinh_str,
                    "CCCD": cccd_clean,
                    "Số báo danh": sbd.strip() if sbd else "Chưa có",
                    "Số điện thoại": sdt_clean,
                    "Hạng xe": hang_xe,
                    "Ngày thi": ngay_thi_str
                }
                
                st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df_data)
                st.success(f"🎉 Đã lưu thành công học viên: {ho_ten_clean} (STT: {next_stt})")
                st.rerun()

# ------------------------------------------------------------------------------------------
# TAB 2: TÌM KIẾM VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("Danh sách & Chỉnh sửa thông tin nhanh")
    
    df_current = st.session_state.df_data
    
    search_keyword = st.text_input("🔍 Nhập Họ tên, CCCD hoặc Số điện thoại để tìm kiếm:")
    
    if search_keyword:
        df_filtered = df_current[
            df_current["Họ tên"].str.contains(search_keyword, case=False, na=False) |
            df_current["CCCD"].astype(str).str.contains(search_keyword, na=False) |
            df_current["Số điện thoại"].astype(str).str.contains(search_keyword, na=False)
        ]
    else:
        df_filtered = df_current

    st.write("💡 *Bạn có thể click đúp trực tiếp vào ô trong bảng dưới đây để sửa nhanh, hoặc tích chọn hàng để xóa.*")
    
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic",
        key="data_editor_key",
        use_container_width=True
    )
    
    if st.button("Xác nhận lưu thay đổi đã sửa"):
        if search_keyword:
            df_current.update(edited_df)
            st.session_state.df_data = df_current
        else:
            st.session_state.df_data = edited_df
            
        st.session_state.df_data["STT"] = pd.to_numeric(st.session_state.df_data["STT"]).astype(int)
        save_data(st.session_state.df_data)
        st.success("Đã cập nhật thay đổi thành công vào file hệ thống!")
        st.rerun()

# ------------------------------------------------------------------------------------------
# TAB 3: XUẤT FILE EXCEL ĐẸP IN ẤN
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("Xem trước danh sách & Xuất file Excel chuẩn In Ấn")
    
    if len(st.session_state.df_data) > 0:
        st.dataframe(st.session_state.df_data, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_data.to_excel(writer, index=False, sheet_name='DANH SÁCH HỌC VIÊN')
            
            workbook  = writer.book
            worksheet = writer.sheets['DANH SÁCH HỌC VIÊN']
            
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#1F4E78',
                'font_color': '#FFFFFF',
                'font_name': 'Times New Roman',
                'font_size': 12,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            cell_center_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'font_size': 11,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            cell_left_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'font_size': 11,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            worksheet.set_row(0, 28)
            
            for col_num, value in enumerate(st.session_state.df_data.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for i, col in enumerate(st.session_state.df_data.columns):
                if col in ["Họ tên"]:
                    current_format = cell_left_format
                else:
                    current_format = cell_center_format
                
                for row_num in range(1, len(st.session_state.df_data) + 1):
                    val = st.session_state.df_data.iloc[row_num - 1, i]
                    worksheet.write(row_num, i, val, current_format)
                    worksheet.set_row(row_num, 22)
                
                max_len = max(
                    st.session_state.df_data[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 5
                worksheet.set_column(i, i, max_len)
                
            worksheet.set_landscape()
            worksheet.set_paper(9)
            worksheet.fit_to_pages(1, 0)
            
        st.download_button(
            label="📥 Tải file Excel Chuẩn In Ấn (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Danh_sach_in_an_hoc_vien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Hiện tại chưa có dữ liệu nào để xuất.")
