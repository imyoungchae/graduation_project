# -*- coding: utf-8 -*-

# GPIO 라이브러리
import smbus                   
import math
import time


# MPU-6050 Register
CONFIG       = 0x1A     # LowPassFilter bit 2:0
GYRO_CONFIG  = 0x1B     # FS_SEL bit 4:3
ACCEL_CONFIG = 0x1C     # FS_SEL bit 4:3
PWR_MGMT_1   = 0x6B     # sleep bit 6, clk_select bit 2:0

DLPF_BW_256 = 0x00      # Acc: BW-260Hz, Delay-0ms, Gyro: BW-256Hz, Delay-0.98ms
DLPF_BW_188 = 0x01
DLPF_BW_98  = 0x02
DLPF_BW_42  = 0x03
DLPF_BW_20  = 0x04
DLPF_BW_10  = 0x05
DLPF_BW_5   = 0x06      # Acc: BW-5Hz, Delay-19ms, Gyro: BW-5Hz, Delay-18.6ms


GYRO_FS_250  = 0x00 << 3    # 250 deg/sec
GYRO_FS_500  = 0x01 << 3
GYRO_FS_1000 = 0x02 << 3
GYRO_FS_2000 = 0x03 << 3    # 2000 deg/sec


ACCEL_FS_2  = 0x00 << 3     # 2g
ACCEL_FS_4  = 0x01 << 3
ACCEL_FS_8  = 0x02 << 3
ACCEL_FS_16 = 0x03 << 3     # 16g


SLEEP_EN        = 0x01 << 6
SLEEP_DIS       = 0x00 << 6

CLOCK_INTERNAL  = 0x00  # internal clk(8KHz) 이용 (Not! Recommended)
CLOCK_PLL_XGYRO = 0x01  # XGyro와 동기
CLOCK_PLL_YGYRO = 0x02  # YGyro와 동기
CLOCK_PLL_ZGYRO = 0x03  # ZGyro와 동기

# Data 읽기
ACCEL_XOUT_H = 0x3B     # Low는 0x3C
ACCEL_YOUT_H = 0x3D     # Low는 0x3E
ACCEL_ZOUT_H = 0x3F     # Low는 0x40
GYRO_XOUT_H  = 0x43     # Low는 0x44
GYRO_YOUT_H  = 0x45     # Low는 0x46
GYRO_ZOUT_H  = 0x47     # Low는 0x48


I2C_bus = smbus.SMBus(1)
MPU6050_addr = 0x68


def write_byte(adr, data):
    I2C_bus.write_byte_data(MPU6050_addr, adr, data)


def read_byte(adr):
    return I2C_bus.read_byte_data(MPU6050_addr, adr)


def read_word(adr):
    high = I2C_bus.read_byte_data(MPU6050_addr, adr)
    low = I2C_bus.read_byte_data(MPU6050_addr, adr+1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val             

def get_raw_data():

    gyro_xout = read_word_2c(GYRO_XOUT_H)
    gyro_yout = read_word_2c(GYRO_YOUT_H)
    gyro_zout = read_word_2c(GYRO_ZOUT_H)
    accel_xout = read_word_2c(ACCEL_XOUT_H)
    accel_yout = read_word_2c(ACCEL_YOUT_H)
    accel_zout = read_word_2c(ACCEL_ZOUT_H)
    return accel_xout, accel_yout, accel_zout,\
           gyro_xout, gyro_yout, gyro_zout



def cal_angle_acc(AcX, AcY, AcZ):

    y_radians = math.atan2(AcX, math.sqrt((AcY*AcY) + (AcZ*AcZ)))
    x_radians = math.atan2(AcY, math.sqrt((AcX*AcX) + (AcZ*AcZ)))
    return math.degrees(x_radians), -math.degrees(y_radians)

DEGREE_PER_SECOND = 32767 / 250  
                              

past = 0      
baseAcX = 0   
baseAcY = 0
baseAcZ = 0
baseGyX = 0
baseGyY = 0
baseGyZ = 0

GyX_deg = 0   # 측정 각도
GyY_deg = 0
GyZ_deg = 0

def cal_angle_gyro(GyX, GyY, GyZ):

    global GyX_deg, GyY_deg, GyZ_deg

    now = time.time()
    dt = now - past     # 초단위

    GyX_deg += ((GyX - baseGyX) / DEGREE_PER_SECOND) * dt
    GyY_deg += ((GyY - baseGyY) / DEGREE_PER_SECOND) * dt
    GyZ_deg += ((GyZ - baseGyZ) / DEGREE_PER_SECOND) * dt

    return now      

def sensor_calibration():

    SumAcX = 0
    SumAcY = 0
    SumAcZ = 0
    SumGyX = 0
    SumGyY = 0
    SumGyZ = 0

    for i in range(10):
        AcX, AcY, AcZ, GyX, GyY, GyZ = get_raw_data()
        SumAcX += AcX
        SumAcY += AcY
        SumAcZ += AcZ
        SumGyX += GyX
        SumGyY += GyY
        SumGyZ += GyZ
        time.sleep(0.1)

    avgAcX = SumAcX / 10
    avgAcY = SumAcY / 10
    avgAcZ = SumAcZ / 10
    avgGyX = SumGyX / 10
    avgGyY = SumGyY / 10
    avgGyZ = SumGyZ / 10

    return avgAcX, avgAcY, avgAcZ, avgGyX, avgGyY, avgGyZ


def set_MPU6050_init(dlpf_bw=DLPF_BW_256,
                     gyro_fs=GYRO_FS_250, accel_fs=ACCEL_FS_2,
                     clk_pll=CLOCK_PLL_XGYRO):
    global baseAcX, baseAcY, baseAcZ, baseGyX, baseGyY, baseGyZ, past

    write_byte(PWR_MGMT_1, SLEEP_EN | clk_pll)      # sleep mode(bit6), clock(bit2:0)은 XGyro 동기
    write_byte(CONFIG, dlpf_bw)                     # bit 2:0
    write_byte(GYRO_CONFIG, gyro_fs)                # Gyro Full Scale bit 4:3
    write_byte(ACCEL_CONFIG, accel_fs)              # Accel Full Scale Bit 4:3
    write_byte(PWR_MGMT_1, SLEEP_DIS | clk_pll)     # Start

    # sensor 계산 초기화
    baseAcX, baseAcY, baseAcZ, baseGyX, baseGyY, baseGyZ \
        = sensor_calibration()
    past = time.time()

    return read_byte(PWR_MGMT_1)    # 정말 시작되었는지 확인


if __name__ == '__main__':
    test = set_MPU6050_init(dlpf_bw=DLPF_BW_98)   # BW만 변경, 나머지는 default 이용
    print("Gyro PWR_MGMT_1 Register = ", test)


    sensor_calibration()    # Gyro의 기준값 계산

    cnt = 0

    while True:
        # 3) accel, gyro의 Raw data 읽기, 
        AcX, AcY, AcZ, GyX, GyY, GyZ = get_raw_data()
     
        # 4-1) Accel을 이용한 각도 계산
        AcX_deg, AcY_deg = cal_angle_acc(AcX, AcY, AcZ)

        # 4-2) Gyro를 이용한 각도 계산 
        past = cal_angle_gyro(GyX, GyY, GyZ)

        # 5) 0.01초 간격으로 값 읽기
        time.sleep(0.01)
        cnt += 1

        # 1초에 한번씩 display
        if cnt%100 == 0:
            print("GyX,Y,Z_deg = ", GyX_deg, ',', GyY_deg, ',', GyZ_deg)
            # print("AcX_deg, AcY_deg = ", AcX_deg, ',', AcY_deg)




