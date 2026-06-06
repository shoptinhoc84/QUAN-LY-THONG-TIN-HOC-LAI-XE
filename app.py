# ------------------------------------------------------------------------------------------
# TAB 3: XUẤT FILE EXCEL ĐẸP IN ẤN
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("Xem trước danh sách & Xuất file Excel chuẩn In Ấn")
    
    if len(st.session_state.df_data) > 0:
        st.dataframe(st.session_state.df_data, use_container_width=True)
        
        # Hàm xuất định dạng nâng cao bằng XlsxWriter
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_data.to_excel(writer, index=False, sheet_name='DANH SÁCH HỌC VIÊN')
            
            # Lấy đối tượng workbook và worksheet từ hệ thống
            workbook  = writer.book
            worksheet = writer.sheets['DANH SÁCH HỌC VIÊN']
            
            # 1. Tạo định dạng cho Tiêu đề cột (Header): Nền xanh đậm, chữ trắng, in đậm, viền xám mỏng
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#1F4E78',  # Màu xanh navy chuyên nghiệp
                'font_color': '#FFFFFF',
                'font_name': 'Times New Roman',
                'font_size': 12,
                'border': 1,
                'border_color': '#D9D9D9'
            })
            
            # 2. Tạo các định dạng ô nội dung học viên
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
            
            # Đặt độ cao cho hàng tiêu đề cột
            worksheet.set_row(0, 28)
            
            # Đè định dạng chuẩn lên dòng đầu tiên (Header)
            for col_num, value in enumerate(st.session_state.df_data.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Duyệt qua từng cột để căn lề và tính toán độ rộng tự động
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
            worksheet.set_paper(9)        # Khổ giấy A4
            worksheet.fit_to_pages(1, 0)  # Tự co khít vừa vặn chiều ngang
            
        # ĐÃ SỬA: Ép định dạng mime chuẩn xác của Excel mã nguồn mở để trình duyệt không tự đổi thành CSV
        st.download_button(
            label="📥 Tải file Excel Chuẩn In Ấn (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Danh_sach_in_an_hoc_vien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Hiện tại chưa có dữ liệu nào để xuất.")
