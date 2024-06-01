from phy import ser_driver
driver=ser_driver.Ser_driver()
driver.set_mode1(False)

driver.set_mode2(ser_driver.Mode.V,ser_driver.Mode.G,ser_driver.Mode.G,ser_driver.Mode.G)

driver.set_voltage('00')

driver.set_duty(True,45)

driver.set_frequency(50)

driver.send()

