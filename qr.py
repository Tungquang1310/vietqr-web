import requests

# Thông tin cố định
BANK_ID = "VCB"  # Vietcombank
ACCOUNT_NO = "1034002102"
ACCOUNT_NAME = "TONG QUANG TUNG"

# Nhập số tiền
amount = input("Nhập số tiền cần thanh toán: ")

# Tạo URL ảnh QR VietQR
vietqr_url = (
    f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={amount}"
    f"&addInfo=Thanh+toan+hoa+don&accountName={ACCOUNT_NAME}"
)

# Tải ảnh QR về máy
response = requests.get(vietqr_url)
if response.status_code == 200:
    with open("vietqr.png", "wb") as f:
        f.write(response.content)
    print("Đã tải mã QR thanh toán vietqr.png từ vietqr.net")
else:
    print("Không thể tải ảnh QR. Kiểm tra lại thông tin hoặc kết nối mạng.")

# Hàm tạo TLV
def tlv(tag, value):
    length = f"{len(value):02d}"
    return f"{tag}{length}{value}"

# Hàm tính CRC-CCITT
def calc_crc(payload):
    crc = 0xFFFF
    for c in payload:
        crc ^= ord(c) << 8
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X')

# Tạo payload VietQR chuẩn EMVCo
def create_vietqr_payload(bank_id, account_no, account_name, amount, add_info):
    # Merchant Account Information (ID "38")
    guid = tlv("00", "A000000727")
    bank_acc = tlv("01", bank_id + account_no)
    name = tlv("02", account_name)
    mai = guid + bank_acc + name
    mai_full = tlv("38", mai)

    payload = "".join([
        tlv("00", "01"),  # Payload Format Indicator
        tlv("01", "12"),  # Point of Initiation Method
        mai_full,
        tlv("53", "704"),  # Currency (704 = VND)
        tlv("54", str(amount)),  # Amount
        tlv("58", "VN"),  # Country Code
        tlv("62", tlv("08", add_info)),  # Additional Info
    ])
    # Thêm trường CRC
    payload_crc = payload + "6304"
    crc = calc_crc(payload_crc)
    return payload_crc + crc

# Tạo payload VietQR
add_info = "Thanh toan hoa don"
payload = create_vietqr_payload(BANK_ID, ACCOUNT_NO, ACCOUNT_NAME, amount, add_info)

