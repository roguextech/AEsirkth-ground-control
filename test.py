from utils import Sigmundr

sigmundr = Sigmundr()

# Frame number
frame = b'\x01'
# Status
frame += b'\x00'
# Err_msg
frame += b'\x04\x03'
# RTC
frame += b'\x01\x02\x01\x0B'
# Timer
frame += b'\x10\x27\x00\x00' # 5s
# Battery1
frame += b'\x00\x00'
# Battery2
frame += b'\x00\x00'
# IMU2
frame += b'\x07\xAE\x06\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xDE\x00\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xAE\x06\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xDE\x00\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
# BMP2
frame += b'\xD0\x07\x00\x00\x00\xCD\x8B\x01'
# BMP3
frame += b'\x00\x00\x00\x00\x00\x00\x00\x00'
# MAG
frame += b'\x00\x00\x00\x00\x00\x00'
# PITOT
frame += b'\x00\x00'

sigmundr.update_sensors(frame)

# Frame number
frame = b'\x01'
# Status
frame += b'\x00'
# Err_msg
frame += b'\x04\x03'
# RTC
frame += b'\x01\x02\x01\x11'
# Timer
frame += b'\x10\x27\x00\x00' # 5s
# Battery1
frame += b'\x00\x00'
# Battery2
frame += b'\x00\x00'
# IMU2
frame += b'\x07\xAE\x06\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xDE\x00\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xAE\x06\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
frame += b'\x07\xDE\x00\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE\x07\xDE'
# BMP2
frame += b'\xD0\x07\x00\x00\x00\xCD\x8B\x01'
# BMP3
frame += b'\x00\x00\x00\x00\x00\x00\x00\x00'
# MAG
frame += b'\x00\x00\x00\x00\x00\x00'
# PITOT
frame += b'\x00\x00'

sigmundr.update_sensors(frame)

print(sigmundr.imu.raw_data)
print(sigmundr.rtc.raw_data)