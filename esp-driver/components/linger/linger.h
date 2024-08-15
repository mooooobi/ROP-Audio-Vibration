#ifndef __LINGER_H__
#define __LINGER_H__
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "driver/uart.h"
#include "string.h"
#include "driver/gpio.h"

#define LINGER_CHANNEL_VCC 0x2
#define LINGER_CHANNEL_GND 0x0
#define LINGER_CHANNEL_NA 0x1
#define LINGER_DUTY(X) (2*(X)+1)

typedef union {
    uint8_t data[6];
    struct {
        uint8_t cmd;
        uint8_t chan0 : 2;
        uint8_t chan1 : 2;
        uint8_t chan2 : 2;
        uint8_t chan3 : 2;
        uint8_t amp;
        uint8_t duty;
        uint16_t freq;
    };
} linger_config_t;
 
typedef struct {
    uint8_t channels[4];
} linger_ret_t ;


esp_err_t install_linger_driver();
esp_err_t uninstall_linger_driver();

esp_err_t linger_enable();
esp_err_t linger_disable();
// esp_err_t linger_config();
esp_err_t linger_read(linger_ret_t* ret);
esp_err_t linger_write(linger_config_t* config);

#endif