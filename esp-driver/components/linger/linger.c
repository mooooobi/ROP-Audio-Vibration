#include "linger.h"

#define GPIO_OUTPUT_PIN_SEL  (1ULL<<19)
#define LINGER_EN_GPIO (GPIO_NUM_19)
#define LINGER_TXD_GPIO (GPIO_NUM_22)
#define LINGER_RXD_GPIO (GPIO_NUM_23)
#define RX_BUFFER_SIZE 1024

static char* LINGER_TAG = "LINGER";
static bool LINGER_STATUS = false;
static uint8_t arr[] = {0xBC, 0x81, 0x52, 0xFF, 0x65, 0x03, 0xE8, 0xAA, 0xAA, 0xFF, 0xDF};
static uint8_t rxbuf[RX_BUFFER_SIZE+1];

static esp_err_t install_uart_deiver() {
    const uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    // We won't use a buffer for sending data.
    esp_err_t ret = uart_driver_install(UART_NUM_1, RX_BUFFER_SIZE * 2, 0, 0, NULL, 0);
    if (ret != ESP_OK) { return ret; }
    ret = uart_param_config(UART_NUM_1, &uart_config);
    if (ret != ESP_OK) { return ret; }
    ret = uart_set_pin(UART_NUM_1, LINGER_TXD_GPIO, LINGER_RXD_GPIO, 
        UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    return ret;
}

static int uart_write() {
    const int bytes = uart_write_bytes(UART_NUM_1, arr, sizeof(arr));
    return bytes;
}

static int uart_read() {
    const int bytes = uart_read_bytes(UART_NUM_1, rxbuf, RX_BUFFER_SIZE, 20 / portTICK_PERIOD_MS);
    return bytes;
}

static esp_err_t install_gpio_driver() {
    gpio_set_direction(LINGER_EN_GPIO, GPIO_MODE_OUTPUT);
    return gpio_set_level(LINGER_EN_GPIO, 1);
}


esp_err_t install_linger_driver() {
    esp_err_t ret = install_gpio_driver();
    if (ret != ESP_OK) { return ret; }
    // linger_enable();
    // vTaskDelay(1000 / portTICK_PERIOD_MS);

    ret = install_uart_deiver();
    if (ret != ESP_OK) { return ret; }

    LINGER_STATUS = true;
    return ESP_OK;
}

esp_err_t uninstall_linger_driver() {
    LINGER_STATUS = false;
    linger_disable();

    esp_err_t ret = uart_driver_delete(UART_NUM_1);
    esp_err_t ret2 = gpio_reset_pin(LINGER_EN_GPIO);
    return ret == ESP_OK && ret2 == ESP_OK;
}

esp_err_t linger_enable() {
    if (LINGER_STATUS) {
        return gpio_set_level(LINGER_EN_GPIO, 1);
    }
    else {
        return ESP_FAIL;
    }
}

esp_err_t linger_disable() {
    return gpio_set_level(LINGER_EN_GPIO, 0);
}

esp_err_t linger_write(linger_config_t* config) {
    arr[1] = config->data[0];
    arr[2] = config->data[1];
    arr[3] = config->data[2];
    arr[4] = config->data[3];
    // reverse the order of uint16
    arr[5] = config->data[5];
    arr[6] = config->data[4];
    // for (int i = 0; i < 4; ++i) {
    //     arr[i+1] = config->data[i];
    //     ESP_LOGI(LINGER_TAG, "Data %d [%x]", i, config->data[i]);
    // }
    if (uart_write() == sizeof(arr)) {
        return ESP_OK;
    }
    else {
        return ESP_FAIL;
    }
}

esp_err_t linger_read(linger_ret_t* ret) {
    int bytes = uart_read();
    if (bytes == 8 && ret != NULL) {
        for (int i = 0; i < 4; ++i) {
            ret->channels[i] = rxbuf[i+1];
        }
        return ESP_OK;
    }
    return ESP_FAIL;
}



