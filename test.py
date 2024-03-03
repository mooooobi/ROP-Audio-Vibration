from phy import ser_driver
import time
driver=ser_driver.Ser_driver()

driver.set_mode1(False)

driver.set_mode2(ser_driver.Mode.V,ser_driver.Mode.G,ser_driver.Mode.G,ser_driver.Mode.G)

# driver.set_voltage('FF')

driver.set_duty(False,50)

# driver.set_frequency(1000)

# driver.send()
pcm=[]
with open("/home/linchi/rop/ROP-Audio-Vibration/output.txt") as file:
    while(1):
        get=file.readline()
        get: str=get.strip()
        tmp=get.split()
        if(len(tmp)!=2):
            break
        target=tmp[0]
        pcm.append('{:02X}'.format(int(target)))

for i in pcm:
    driver.set_voltage(i)
    driver.send()
    time.sleep(0.05)