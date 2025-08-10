# JoyCheck (PortMaster)

Trình kiểm tra tay cầm cho máy chơi game cầm tay Linux chạy **PortMaster**. Hiển thị trạng thái nút, trục và D-Pad theo thời gian thực. Dùng để test nhanh sau khi map phím hoặc đổi tay cầm.

## Tính năng
- Trực quan Button / Axis / Hat (D-Pad) theo thời gian thực.
- Hỗ trợ hot-swap nhiều tay cầm.
- Toàn màn hình tối ưu cho handheld.
- Ghi log tùy chọn để chẩn đoán.

## Yêu cầu
- Đã cài **PortMaster**.

## Cài đặt
**ArkOS và Rocknix**  
Sao chép **thư mục JoyCheck** và **file JoyCheck.sh** vào:
```
/roms/ports
```

**muOS**  
Sao chép **thư mục JoyCheck** vào:
```
/ports
```
Sao chép **file JoyCheck.sh** vào:
```
/roms/ports
```

**CrossMix**  
Sao chép **thư mục JoyCheck** và **file JoyCheck.sh** vào:
```
/Data/ports
```

Cấp quyền chạy cho script (điều chỉnh đường dẫn nếu khác):
```
chmod +x /roms/ports/JoyCheck.sh
```

## Sử dụng
- Mở **PortMaster → Ports → JoyCheck**.
- Cắm hoặc pair tay cầm trước khi chạy để nhận thiết bị ngay.
- Hỗ trợ hot-swap. Nếu không nhận, thoát và mở lại.

## Log và khắc phục sự cố
- Log mặc định: `/roms/ports/joycheck/run.log`.
- Nếu không thấy input:
  - Kiểm tra kết nối USB/Bluetooth và mapping của hệ thống.
  - Đảm bảo `JoyCheck.sh` có quyền thực thi.
  - Xác nhận đúng đường dẫn PortMaster theo firmware bạn dùng.

## Tương thích
- Đã kiểm tra với PortMaster **2025.07.14-1510**: https://github.com/PortsMaster/PortMaster-GUI/releases

## Ghi công & quy chiếu
- Một phần ý tưởng và quy trình tham khảo từ **PortMaster-GUI**. PortMaster và PortMaster-GUI là các dự án riêng biệt. JoyCheck là dự án độc lập và **không liên kết hay được bảo trợ** bởi các dự án này.
- Mọi nhãn hiệu và tên sản phẩm thuộc về chủ sở hữu tương ứng.

## Giấy phép và bản quyền
- **Giấy phép:** MIT
- **Bản quyền © 2025 To Hung Duong** <HungDuongWP@gmail.com>
- Bạn được phép sử dụng lại theo điều khoản giấy phép MIT. Khi phân phối lại dưới dạng mã nguồn hoặc nhị phân, vui lòng giữ nguyên thông báo này và toàn văn giấy phép MIT.
- Liên hệ: <HungDuongWP@gmail.com>
