# ------------------------------------------------------------------------------------------
# TAB 1: THÊM MỚI HỌC VIÊN (ĐÃ SỬA LỖI HIỂN THỊ THÔNG BÁO THÀNH CÔNG)
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("Nhập thông tin học viên mới")
    
    with st.form("form_them_moi", clear_on_submit=True): # Đổi thành True để lưu xong tự xóa sạch ô nhập cho người kế tiếp
        col1, col2 = st.columns(2)
        with col1:
            ho_ten = st.text_input("Họ và tên *")
            ngay_sinh_dt = st.date_input("Ngày sinh", min_value=datetime(1950, 1, 1), max_value=datetime.today(), format="DD/MM/YYYY")
            cccd = st.text_input("Số CCCD (Bắt buộc nhập đủ 12 số) *", max_chars=12, help="Nhập chính xác 12 chữ số")
            sbd = st.text_input("Số báo danh (SBD)")
        with col2:
            sdt = st.text_input("Số điện thoại (Bắt buộc nhập đủ 10 số) *", max_chars=10, help="Nhập chính xác 10 chữ số bắt đầu từ số 0")
            hang_xe = st.selectbox("Hạng xe (Luật mới 2026)", HANG_XE_2026)
            lura_xe = st.selectbox("Lựa xe (Phân loại)", LOAI_XE_LIST)
            ngay_thi_dt = st.date_input("Ngày thi dự kiến", min_value=datetime.today(), format="DD/MM/YYYY")
            
        submit_btn = st.form_submit_button("Lưu vào hệ thống")
        
        if submit_btn:
            ho_ten_clean = ho_ten.strip()
            cccd_clean = cccd.strip()
            sdt_clean = sdt.strip()
            
            # 1. Kiểm tra bỏ trống
            if not ho_ten_clean or not sdt_clean or not cccd_clean:
                st.error("❌ Vui lòng điền đầy đủ các thông tin bắt buộc (* gồm Họ tên, CCCD, Số điện thoại)")
            
            # 2. Khóa định dạng Số điện thoại
            elif not sdt_clean.isdigit() or len(sdt_clean) != 10 or not sdt_clean.startswith('0'):
                st.error(f"⚠️ SỐ ĐIỆN THOẠI KHÔNG HỢP LỆ! Bạn hiện nhập {len(sdt_clean)} ký tự. Vui lòng nhập ĐÚNG và ĐỦ 10 chữ số (bắt đầu bằng số 0).")
            
            # 3. Khóa định dạng CCCD
            elif not cccd_clean.isdigit() or len(cccd_clean) != 12:
                st.error(f"⚠️ SỐ CCCD KHÔNG HỢP LỆ! Bạn hiện nhập {len(cccd_clean)} ký tự. Căn cước công dân phải nhập ĐÚNG và ĐỦ 12 chữ số.")
                
            else:
                # Tiến hành lưu dữ liệu
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
                    "Lựa xe": lura_xe,
                    "Ngày thi": ngay_thi_str
                }
                
                st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df_data)
                
                # ĐÃ SỬA: Lưu trạng thái thông báo vào session_state để không bị mất khi rerun
                st.session_state.luu_thanh_cong = f"🎉 Đã lưu thành công học viên: {ho_ten_clean} (STT: {next_stt})"
                st.rerun()

# Hiển thị thông báo ngoài form sau khi trang tải lại thành công
if 'luu_thanh_cong' in st.session_state:
    st.success(st.session_state.luu_thanh_cong)
    st.toast(st.session_state.luu_thanh_cong, icon="🎉") # Bật thêm bong bóng thông báo góc màn hình
    del st.session_state.luu_thanh_cong # Xóa dấu vết để lần sau không bị lặp lại thông báo cũ
