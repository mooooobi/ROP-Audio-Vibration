/* SD card and FAT filesystem example.
   This example uses SPI peripheral to communicate with SD card.

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

#include <string.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "sd_test_io.h"
#include "driver/i2s_std.h"
#include "driver/i2s_common.h"
#include "linger.h"
#include "spin_control.h"

void init(void)
{
    ESP_ERROR_CHECK(install_linger_driver());
    ESP_ERROR_CHECK(linger_enable());
    install_spin_control();
}

static const char *TAG = "example";
static i2s_chan_handle_t tx_chan;
static sdmmc_card_t *card;
static float volume;
static uint8_t elec_stims[1069] = {0, 77, 112, 116, 111, 112, 115, 113, 115, 115, 117, 113, 114, 113, 112, 118, 119, 118, 117, 113, 115, 113, 115, 115, 113, 112, 112, 114, 117, 123, 120, 116, 115, 119, 119, 125, 127, 124, 125, 121, 123, 123, 129, 128, 123, 115, 114, 115, 121, 113, 111, 116, 113, 116, 114, 130, 123, 118, 117, 116, 112, 114, 113, 115, 115, 116, 113, 116, 129, 133, 130, 127, 122, 121, 121, 124, 123, 123, 122, 120, 120, 122, 126, 129, 116, 113, 112, 114, 116, 113, 116, 115, 113, 116, 117, 153, 129, 121, 116, 111, 115, 114, 115, 112, 114, 119, 115, 113, 122, 124, 122, 120, 125, 122, 122, 120, 118, 120, 120, 117, 117, 118, 121, 119, 119, 115, 114, 115, 122, 117, 116, 120, 128, 131, 132, 129, 133, 121, 124, 125, 132, 128, 129, 125, 126, 127, 132, 134, 142, 148, 151, 158, 161, 172, 177, 184, 189, 193, 197, 198, 197, 209, 206, 206, 203, 203, 197, 192, 214, 185, 181, 193, 172, 188, 163, 190, 182, 172, 217, 164, 177, 196, 169, 207, 167, 196, 182, 172, 213, 166, 167, 196, 175, 197, 156, 193, 177, 159, 219, 168, 168, 194, 171, 197, 159, 181, 179, 162, 208, 166, 167, 197, 174, 195, 167, 252, 243, 227, 224, 215, 213, 212, 235, 205, 209, 202, 191, 186, 236, 230, 188, 199, 186, 206, 176, 239, 207, 175, 219, 176, 184, 206, 238, 206, 163, 194, 183, 167, 233, 228, 205, 196, 176, 212, 208, 238, 209, 203, 212, 196, 213, 202, 196, 199, 202, 193, 191, 190, 185, 203, 238, 238, 229, 240, 244, 255, 249, 245, 246, 241, 250, 245, 231, 243, 248, 234, 236, 239, 224, 233, 239, 235, 229, 244, 245, 199, 239, 239, 239, 227, 230, 227, 216, 237, 240, 234, 235, 242, 218, 237, 231, 225, 225, 245, 230, 192, 226, 226, 242, 227, 231, 227, 207, 236, 231, 234, 228, 233, 217, 225, 236, 229, 225, 235, 228, 189, 231, 238, 238, 222, 229, 229, 217, 232, 231, 233, 239, 239, 222, 233, 234, 230, 224, 235, 227, 189, 231, 241, 241, 239, 235, 238, 219, 246, 252, 236, 236, 238, 219, 227, 228, 225, 223, 233, 228, 197, 229, 232, 209, 221, 232, 229, 246, 251, 248, 236, 248, 248, 232, 241, 246, 250, 233, 247, 241, 211, 234, 244, 241, 241, 237, 229, 218, 234, 231, 232, 231, 243, 215, 229, 241, 243, 230, 238, 244, 201, 224, 229, 239, 237, 240, 236, 211, 233, 231, 233, 229, 233, 223, 229, 239, 231, 223, 238, 235, 204, 232, 238, 239, 231, 233, 232, 229, 246, 247, 232, 246, 233, 222, 228, 250, 247, 226, 235, 230, 198, 224, 233, 241, 234, 238, 235, 225, 243, 243, 232, 231, 245, 220, 231, 240, 228, 224, 241, 236, 197, 226, 232, 239, 227, 235, 231, 223, 237, 238, 230, 230, 234, 234, 219, 220, 220, 213, 214, 206, 199, 193, 187, 217, 213, 187, 203, 173, 212, 173, 188, 199, 173, 213, 170, 186, 199, 180, 216, 171, 188, 193, 169, 222, 181, 185, 189, 172, 206, 164, 190, 204, 183, 214, 170, 178, 203, 175, 207, 165, 185, 187, 168, 218, 175, 179, 196, 176, 209, 170, 188, 190, 167, 220, 177, 189, 199, 183, 213, 214, 195, 190, 177, 224, 177, 202, 200, 179, 218, 175, 212, 199, 186, 229, 184, 214, 214, 203, 240, 189, 222, 201, 215, 228, 221, 227, 232, 214, 226, 214, 222, 224, 235, 227, 233, 231, 232, 228, 229, 233, 253, 243, 230, 222, 217, 214, 211, 203, 221, 209, 202, 201, 193, 220, 193, 192, 205, 194, 215, 181, 188, 196, 177, 220, 179, 187, 188, 177, 211, 169, 190, 191, 168, 218, 174, 188, 204, 185, 210, 203, 190, 201, 200, 222, 217, 226, 231, 220, 227, 224, 196, 223, 222, 246, 249, 238, 223, 208, 220, 209, 241, 213, 213, 222, 221, 195, 218, 237, 213, 184, 200, 201, 186, 237, 228, 215, 206, 185, 224, 183, 239, 210, 174, 233, 189, 209, 215, 239, 220, 180, 213, 214, 197, 237, 230, 202, 208, 181, 223, 179, 239, 220, 199, 228, 198, 214, 213, 238, 224, 188, 244, 210, 188, 239, 231, 232, 213, 240, 241, 233, 246, 214, 215, 240, 232, 226, 209, 240, 228, 196, 245, 217, 225, 242, 233, 244, 217, 245, 242, 238, 235, 219, 234, 239, 223, 241, 228, 237, 236, 237, 230, 222, 230, 236, 231, 226, 223, 232, 238, 239, 203, 228, 235, 234, 229, 236, 243, 252, 252, 249, 235, 247, 249, 232, 244, 247, 241, 232, 246, 238, 209, 236, 239, 239, 229, 235, 231, 216, 236, 227, 234, 234, 235, 221, 232, 236, 234, 231, 245, 248, 198, 224, 233, 234, 228, 243, 230, 211, 237, 230, 232, 224, 230, 214, 231, 243, 239, 225, 235, 235, 196, 232, 234, 239, 234, 240, 236, 220, 236, 244, 234, 245, 229, 225, 239, 245, 240, 229, 239, 230, 195, 222, 227, 241, 241, 229, 228, 223, 240, 237, 234, 231, 242, 221, 228, 231, 224, 225, 237, 232, 198, 228, 230, 238, 229, 233, 225, 225, 236, 235, 210, 242, 238, 239, 249, 251, 249, 237, 247, 245, 216, 243, 247, 241, 238, 248, 240, 240, 249, 251, 236, 233, 236, 218, 229, 234, 233, 225, 240, 235, 200, 232, 242, 241, 243, 251, 243, 222, 233, 228, 230, 232, 237, 216, 229, 230, 232, 225, 239, 232, 202, 232, 246, 241, 228, 235, 229, 221, 239, 248, 232, 229, 238, 224, 242, 243, 245, 230, 243, 231, 212, 236, 241, 241, 237, 237, 230, 217, 232, 233, 233, 230, 241, 221, 227, 239, 234, 229, 240, 242, 195, 225, 230, 243, 237, 238, 237, 212, 235, 229, 232, 231, 236, 219, 228, 236, 234, 229, 242, 244, 213, 208, 209, 203, 197, 194, 191, 183, 180, 173, 166, 159, 156, 150, 146, 143, 137, 133, 129, 129, 122, 120, 122, 123, 119, 123, 120, 125, 124, 122, 123, 123, 127, 125, 126, 122, 125, 123, 123, 121, 125, 118, 119, 124, 120, 119, 116, 116, 116, 113, 113, 115, 114, 112, 114, 115, 113, 111, 106, 107, 103, 102, 102, 98, 100, 99, 95, 95, 97, 96, 95, 95, 92, 93, 92, 90, 89, 90, 91, 88, 82, 80, 79, 78, 77, 74, 74, 69, 64, 60, 57, 50, 43, 29};

#define MOUNT_POINT "/sdcard"

#define PIN_NUM_MISO CONFIG_EXAMPLE_PIN_MISO
#define PIN_NUM_MOSI CONFIG_EXAMPLE_PIN_MOSI
#define PIN_NUM_CLK CONFIG_EXAMPLE_PIN_CLK
#define PIN_NUM_CS CONFIG_EXAMPLE_PIN_CS

sdmmc_card_t *init_sd_card(void)
{
    esp_err_t ret;

    // Options for mounting the filesystem.
    // If format_if_mount_failed is set to true, SD card will be partitioned and
    // formatted in case when mounting fails.
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
#ifdef CONFIG_EXAMPLE_FORMAT_IF_MOUNT_FAILED
        .format_if_mount_failed = true,
#else
        .format_if_mount_failed = false,
#endif // EXAMPLE_FORMAT_IF_MOUNT_FAILED
        .max_files = 5,
        .allocation_unit_size = 16 * 1024};
    sdmmc_card_t *card;
    const char mount_point[] = MOUNT_POINT;
    ESP_LOGI(TAG, "Initializing SD card");

    // Use settings defined above to initialize SD card and mount FAT filesystem.
    // Note: esp_vfs_fat_sdmmc/sdspi_mount is all-in-one convenience functions.
    // Please check its source code and implement error recovery when developing
    // production applications.
    ESP_LOGI(TAG, "Using SPI peripheral");

    // By default, SD card frequency is initialized to SDMMC_FREQ_DEFAULT (20MHz)
    // For setting a specific frequency, use host.max_freq_khz (range 400kHz - 20MHz for SDSPI)
    // Example: for fixed frequency of 10MHz, use host.max_freq_khz = 10000;
    sdmmc_host_t host = SDSPI_HOST_DEFAULT();

    // For SoCs where the SD power can be supplied both via an internal or external (e.g. on-board LDO) power supply.
    // When using specific IO pins (which can be used for ultra high-speed SDMMC) to connect to the SD card
    // and the internal LDO power supply, we need to initialize the power supply first.
#if CONFIG_EXAMPLE_SD_PWR_CTRL_LDO_INTERNAL_IO
    sd_pwr_ctrl_ldo_config_t ldo_config = {
        .ldo_chan_id = CONFIG_EXAMPLE_SD_PWR_CTRL_LDO_IO_ID,
    };
    sd_pwr_ctrl_handle_t pwr_ctrl_handle = NULL;

    ret = sd_pwr_ctrl_new_on_chip_ldo(&ldo_config, &pwr_ctrl_handle);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to create a new on-chip LDO power control driver");
        return;
    }
    host.pwr_ctrl_handle = pwr_ctrl_handle;
#endif

    spi_bus_config_t bus_cfg = {
        .mosi_io_num = PIN_NUM_MOSI,
        .miso_io_num = PIN_NUM_MISO,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4092,
    };

    ret = spi_bus_initialize(host.slot, &bus_cfg, SDSPI_DEFAULT_DMA);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to initialize bus.");
        return NULL;
    }

    // This initializes the slot without card detect (CD) and write protect (WP) signals.
    // Modify slot_config.gpio_cd and slot_config.gpio_wp if your board has these signals.
    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = PIN_NUM_CS;
    slot_config.host_id = host.slot;

    ESP_LOGI(TAG, "Mounting filesystem");
    ret = esp_vfs_fat_sdspi_mount(mount_point, &host, &slot_config, &mount_config, &card);

    if (ret != ESP_OK)
    {
        if (ret == ESP_FAIL)
        {
            ESP_LOGE(TAG, "Failed to mount filesystem. "
                          "If you want the card to be formatted, set the CONFIG_EXAMPLE_FORMAT_IF_MOUNT_FAILED menuconfig option.");
        }
        else
        {
            ESP_LOGE(TAG, "Failed to initialize the card (%s). "
                          "Make sure SD card lines have pull-up resistors in place.",
                     esp_err_to_name(ret));
        }
        return NULL;
    }
    ESP_LOGI(TAG, "Filesystem mounted");

    sdmmc_card_print_info(stdout, card);
    return card;
}
void deinit_sd_card(sdmmc_card_t *card)
{
    // All done, unmount partition and disable SPI peripheral
    const char mount_point[] = MOUNT_POINT;
    esp_vfs_fat_sdcard_unmount(mount_point, card);
    ESP_LOGI(TAG, "Card unmounted");
    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    // deinitialize the bus after all devices are removed
    spi_bus_free(host.slot);
}

typedef struct
{
    char riff_id[4];
    uint32_t riff_size;
    char wave_id[4];
} RiffHeader;

typedef struct
{
    char chunk_id[4];
    uint32_t chunk_size;
} ChunkHeader;

typedef struct
{
    uint16_t audio_format;
    uint16_t num_of_channels;
    uint32_t sample_rate;
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
} FormatChunk;

void init_i2s(uint32_t sample_rate, uint16_t bits_per_sample, uint16_t num_of_channels)
{
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
    chan_cfg.auto_clear = true;
    chan_cfg.dma_frame_num = 960;
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(sample_rate),
        .slot_cfg = I2S_STD_MSB_SLOT_DEFAULT_CONFIG(bits_per_sample, num_of_channels),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = CONFIG_EXAMPLE_I2S_BCK_PIN,
            .ws = CONFIG_EXAMPLE_I2S_LRCK_PIN,
            .dout = CONFIG_EXAMPLE_I2S_DATA_PIN,
            .din = I2S_GPIO_UNUSED,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_chan, NULL));
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_chan, &std_cfg));
}

void music_task()
{
    FILE *f = fopen(MOUNT_POINT "/test.wav", "rb");
    if (f == NULL)
    {
        ESP_LOGE(TAG, "Failed to open file for reading");
        return;
    }
    // wav_header_t header;
    RiffHeader riff_header;
    fread(&riff_header, sizeof(RiffHeader), 1, f);
    if (strncmp(riff_header.riff_id, "RIFF", 4) != 0 || strncmp(riff_header.wave_id, "WAVE", 4) != 0)
    {
        ESP_LOGE(TAG, "Not a wav file");
        fclose(f);
        return;
    }
    ESP_LOGI(TAG, "RIFF size: %lu", riff_header.riff_size + 8);
    ChunkHeader chunk_header;
    uint32_t sample_rate = 0;
    uint16_t bits_per_sample = 0;
    uint16_t num_of_channels = 0;
    while (fread(&chunk_header, sizeof(ChunkHeader), 1, f))
    {
        if (strncmp(chunk_header.chunk_id, "data", 4) == 0)
        {
            ESP_LOGI(TAG, "Found 'data' chunk");
            ESP_LOGI(TAG, "Chunk size: %lu bytes", chunk_header.chunk_size);
            break;
        }
        else if (strncmp(chunk_header.chunk_id, "fmt ", 4) == 0)
        {
            // Read the format chunk
            FormatChunk format_chunk;
            fread(&format_chunk, sizeof(FormatChunk), 1, f);
            sample_rate = format_chunk.sample_rate;
            bits_per_sample = format_chunk.bits_per_sample;
            num_of_channels = format_chunk.num_of_channels;
            if (sizeof(FormatChunk) < chunk_header.chunk_size)
            {
                fseek(f, chunk_header.chunk_size - sizeof(FormatChunk), SEEK_CUR);
            }
        }
        else
        {
            fseek(f, chunk_header.chunk_size, SEEK_CUR);
        }
    }
    ESP_LOGI(TAG, "Sample rate: %lu", sample_rate);
    ESP_LOGI(TAG, "Bits per sample: %u", bits_per_sample);
    ESP_LOGI(TAG, "Channels: %u", num_of_channels);

    init_i2s(sample_rate, bits_per_sample, num_of_channels);
    ESP_LOGI(TAG, "I2S initialized");

    size_t buffer_length = 960 * num_of_channels * bits_per_sample / 8;
    int16_t *buffer = (int16_t *)malloc(buffer_length);
    ESP_LOGI(TAG, "Buffer length: %u", buffer_length);
    int i = 0;

    ESP_ERROR_CHECK(i2s_channel_enable(tx_chan));
    ESP_LOGI(TAG, "I2S enabled");

    while (fread(buffer, buffer_length, 1, f) == 1)
    {

        for (i = 0; i < buffer_length / 2; i++)
        {
            buffer[i] = (int16_t)((float)buffer[i] * volume);
        }
        ESP_ERROR_CHECK(i2s_channel_write(tx_chan, buffer, buffer_length, NULL, portMAX_DELAY));
    }
    free(buffer);
    fclose(f);
    ESP_ERROR_CHECK(i2s_channel_disable(tx_chan));
    vTaskDelete(NULL);
}

void volume_task()
{
    int raw_mv;
    while (1)
    {
        raw_mv = read_control_value(1);
        volume = ((float)raw_mv - 142.0) / 3008.0;
        vTaskDelay(pdMS_TO_TICKS(500));
        ESP_LOGI("volume", "%f", volume);
    }
}

void dac_task()
{
    linger_config_t config;
    config.cmd = 0x81;
    config.chan3 = LINGER_CHANNEL_NA;
    config.chan2 = LINGER_CHANNEL_NA;
    config.chan1 = LINGER_CHANNEL_GND;
    config.chan0 = LINGER_CHANNEL_VCC;
    config.amp = 100;
    config.freq = 200;
    config.duty = LINGER_DUTY(20);
    int i=0;
    for(i=0;i<1069;i++){
        config.amp=elec_stims[i];
        ESP_ERROR_CHECK(linger_write(&config));
        ESP_LOGI("AMP","V(Hex): %02x\tTimes: %.1f(s)",elec_stims[i],i*0.2);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
    vTaskDelete(NULL);
}

// void manager_task(){
//     eTaskState music_state,dac_state;
//     while(1){
//         music_state=eTaskGetState(music_handle);
//         dac_state=eTaskGetState(dac_handle);
//     }
// }
TaskHandle_t* music_handle;
TaskHandle_t* dac_handle;

void app_main(void)
{
    init();
    card = init_sd_card();
    if (card == NULL)
    {
        return;
    }
    xTaskCreate(volume_task, "volume_task", 1024 * 4, NULL, 2, NULL);
    xTaskCreate(music_task, "music_task", 16384, NULL, 1, music_handle);
    xTaskCreate(dac_task,"dac_task",16384,NULL,1,dac_handle);
    // deinit_sd_card(card);
}
