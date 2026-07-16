create table NGUOI_BAN(
	MaNguoiBan varchar(10) not null primary key,
	MatKhau varchar(50) not null,
	HoTen nvarchar(40),
	SoDienThoai varchar(10),
	Email varchar(40),
	TenCuaHang nvarchar(40),
	DiaChi nvarchar(100));

create table KHACH_HANG(
	MaKhachHang varchar(10) not null primary key,
	HoTen nvarchar(40),
	SoDienThoai varchar(10),
	Email varchar(40),
	DiaChi nvarchar(100));
	

create table SAN_PHAM(
	MaSP varchar(10) not null primary key,
	TenSP nvarchar(100),
	MoTa nvarchar(max),
	GiaBan float,
	SoLuongTon int,
	HinhAnh varchar(255));

create table VOUCHER(
	MaVoucher varchar(10) not null primary key,
	TenVoucher nvarchar(100),
	GiaTriGiam float,
	DieuKienApDung nvarchar(255),
	NgayBatDau datetime,
	NgayKetThuc datetime,
	TrangThai nvarchar(40));

create table LIVESTREAM(
	MaLive varchar(10) not null primary key,
	MaNguoiBan varchar(10) not null references NGUOI_BAN(MaNguoiBan),
	TenLive nvarchar(100),
	ThoiGianBatDau datetime,
	ThoiGianKetThuc datetime,
	TrangThai nvarchar(40));


create table LIVESTREAM_SAN_PHAM(
	MaLive varchar(10) not null references LIVESTREAM(MaLive),
	MaSP varchar(10) not null references SAN_PHAM(MaSP),
	primary key (MaLive, MaSP));


create table BINH_LUAN(
	MaBinhLuan varchar(10) not null primary key,
	MaLive varchar(10) not null references LIVESTREAM(MaLive),
	NoiDung nvarchar(max),
	ThoiGian datetime,
	NguoiBinhLuan nvarchar(50),
	LoaiBinhLuan nvarchar(40));

create table DON_HANG(
	MaDonHang varchar(10) not null primary key,
	MaKhachHang varchar(10) not null references KHACH_HANG(MaKhachHang),
	MaBinhLuan varchar(10) references BINH_LUAN(MaBinhLuan),
	MaVoucher varchar(10) references VOUCHER(MaVoucher),
	NgayDat datetime,
	TongTien float,
	TrangThaiDH nvarchar(40));

create table CHI_TIET_DON_HANG(
	MaDonHang varchar(10) not null references DON_HANG(MaDonHang),
	MaSP varchar(10) not null references SAN_PHAM(MaSP),
	SoLuong int,
	DonGia float,
	ThanhTien float,
	primary key (MaDonHang, MaSP));

create table HOA_DON(
	MaHoaDon varchar(10) not null primary key,
	MaDonHang varchar(10) not null references DON_HANG(MaDonHang),
	PhuongThucTT nvarchar(50),
	TongTien float,
	ThoiGianLap datetime,
	TrangThaiHD nvarchar(40));

--Nạp dữ liệu vào bảng--
--1. NẠP DỮ LIỆU BẢNG: NGUOI_BAN
insert into NGUOI_BAN(MaNguoiBan, MatKhau, HoTen, SoDienThoai, Email, TenCuaHang, DiaChi)
values
('NB01', '123', N'Phạm Văn D', '0901234567', 'pham@gmail.com', N'Phạm Shop', N'TP.HCM'),
('NB02', '456', N'Hồ E', '0907654321', 'ho@gmail.com', N'Hồ Fashion', N'Hà Nội'),
('NB03', '789', N'Trần Phạm E', '0911223344', 'tran@gmail.com', N'Ế Boutique', N'Đà Nẵng');

--2. NẠP DỮ LIỆU BẢNG: SAN_PHAM
insert into SAN_PHAM(MaSP, TenSP, MoTa, GiaBan, SoLuongTon, HinhAnh)
values
('SP01', N'Áo Thun Cực Chất', N'Chất cotton co giãn 4 chiều', 160000, 15, 'aothun.jpg'), 
('SP02', N'Quần Jean Sành Điệu', N'Vải jean dày dặn dáng suông', 250000, 50, 'quanjean.jpg'), 
('SP03', N'Váy Công Chúa VIP', N'Đầm dự tiệc sang chảnh', 350000, 5, 'vay.jpg'), 
('SP04', N'Nón Kết Thể Thao', N'Chống nắng thời trang', 40000, 100, 'non.jpg'); 

--3. NẠP DỮ LIỆU BẢNG: KHACH_HANG
insert into KHACH_HANG(MaKhachHang, HoTen, SoDienThoai, Email, DiaChi)
values
('KH01', N'Nguyễn Văn A', '0933333333', 'customer_a@gmail.com', N'TP.HCM'),
('KH02', N'Lê Thị B', '0944444444', 'customer_b@gmail.com', N'Hà Nội'),
('KH03', N'Chiến Thần Bom Hàng', '0955555555', 'customer_c@gmail.com', N'Cần Thơ'); 

--4. NẠP DỮ LIỆU BẢNG: VOUCHER
insert into VOUCHER(MaVoucher, TenVoucher, GiaTriGiam, DieuKienApDung, NgayBatDau, NgayKetThuc, TrangThai)
values
('VOUCHER01', N'Giảm Giá Đầu Năm', 20000, N'Đơn từ 200k', '2026-01-01', '2026-02-01', N'Hết hạn'),
('VOUCHER02', N'Siêu Sale Tháng 3', 50000, N'Đơn từ 300k', '2026-03-01', '2026-03-31', N'Đang áp dụng');

--5. NẠP DỮ LIỆU BẢNG: LIVESTREAM
insert into LIVESTREAM(MaLive, MaNguoiBan, TenLive, ThoiGianBatDau, ThoiGianKetThuc, TrangThai)
values
('LIVE01', 'NB01', N'Xả Kho Đón Tết 2026', '2026-01-15 19:00:00', '2026-01-15 22:00:00', N'Đã kết thúc'), 
('LIVE02', 'NB01', N'Mega Sale Tháng 3', '2026-03-15 20:00:00', '2026-03-15 23:00:00', N'Đã kết thúc'), 
('LIVE03', 'NB02', N'Chốt Đơn Mỏi Tay', '2026-03-20 12:00:00', '2026-03-20 15:00:00', N'Đã kết thúc');

--6. NẠP DỮ LIỆU BẢNG: LIVESTREAM_SAN_PHAM
insert into LIVESTREAM_SAN_PHAM(MaLive, MaSP)
values
('LIVE01', 'SP01'),
('LIVE01', 'SP02'),
('LIVE02', 'SP02'),
('LIVE02', 'SP03'),
('LIVE03', 'SP01');

--7. NẠP DỮ LIỆU BẢNG: BINH_LUAN
insert into BINH_LUAN(MaBinhLuan, MaLive, NoiDung, ThoiGian, NguoiBinhLuan, LoaiBinhLuan)
values
('BL01', 'LIVE01', N'Chốt SP01 size M nha shop', '2026-01-15 19:10:00', N'Nguyễn Văn A', N'Chốt đơn'),
('BL02', 'LIVE02', N'Chốt SP02 với SP03 luôn nha', '2026-03-15 20:15:00', N'Nguyễn Văn A', N'Chốt đơn'),
('BL03', 'LIVE03', N'Chốt SP01 shop ơi', '2026-03-20 12:30:00', N'Lê Thị B', N'Chốt đơn'),
('BL04', 'LIVE02', N'Áo này có co giãn không shop?', '2026-03-15 20:20:00', N'Lê Thị B', N'Hỏi đáp'); 

--8. NẠP DỮ LIỆU BẢNG: DON_HANG
insert into DON_HANG(MaDonHang, MaKhachHang, MaBinhLuan, MaVoucher, NgayDat, TongTien, TrangThaiDH)
values
('DH01', 'KH01', 'BL01', 'VOUCHER01', '2026-01-15 19:15:00', 160000, N'Đã giao'), 
('DH02', 'KH01', 'BL02', 'VOUCHER02', '2026-03-15 20:30:00', 600000, N'Đã giao'),
('DH03', 'KH02', 'BL03', null, '2026-03-20 12:45:00', 160000, N'Đang giao');

--9. NẠP DỮ LIỆU BẢNG: CHI_TIET_DON_HANG
insert into CHI_TIET_DON_HANG(MaDonHang, MaSP, SoLuong, DonGia, ThanhTien)
values
('DH01', 'SP01', 1, 160000, 160000),
('DH02', 'SP02', 1, 250000, 250000),
('DH02', 'SP03', 1, 350000, 350000),
('DH03', 'SP01', 1, 160000, 160000);

--10. NẠP DỮ LIỆU BẢNG: HOA_DON
insert into HOA_DON(MaHoaDon, MaDonHang, PhuongThucTT, TongTien, ThoiGianLap, TrangThaiHD)
values
('HD01', 'DH01', N'Thẻ tín dụng', 160000, '2026-01-15 19:30:00', N'Đã thanh toán'),
('HD02', 'DH02', N'Chuyển khoản', 600000, '2026-03-15 21:00:00', N'Đã thanh toán'),
('HD03', 'DH03', N'COD', 160000, '2026-03-20 13:00:00', N'Chưa thanh toán');






