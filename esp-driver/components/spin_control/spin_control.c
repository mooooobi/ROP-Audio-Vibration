/*
 * SPDX-FileCopyrightText: 2022-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#include "spin_control.h"

// ADC1 Channels
#define EXAMPLE_ADC1_CHAN0 ADC_CHANNEL_5
#define EXAMPLE_ADC1_CHAN1 ADC_CHANNEL_6
#define EXAMPLE_ADC1_CHAN2 ADC_CHANNEL_7
#define EXAMPLE_ADC_ATTEN ADC_ATTEN_DB_12

int adc_raw[3];
static adc_oneshot_unit_handle_t adc1_handle;

void install_spin_control()
{

    //-------------ADC1 Init---------------//
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc1_handle));

    //-------------ADC1 Config---------------//
    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = EXAMPLE_ADC_ATTEN,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, EXAMPLE_ADC1_CHAN0, &config));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, EXAMPLE_ADC1_CHAN1, &config));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, EXAMPLE_ADC1_CHAN2, &config));
}

int read_control_value(int channel)
{
    adc_channel_t activate_chan = EXAMPLE_ADC1_CHAN0;
    if (channel == 0)
    {
        activate_chan = EXAMPLE_ADC1_CHAN0;
    }
    else if (channel == 1)
    {
        activate_chan = EXAMPLE_ADC1_CHAN1;
    }
    else
    {
        activate_chan = EXAMPLE_ADC1_CHAN2;
    }
    ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, activate_chan, &adc_raw[channel]));
    adc_cali_line_fitting_config_t cali_config = {
        .unit_id = ADC_UNIT_1,
        .atten = EXAMPLE_ADC_ATTEN,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    adc_cali_handle_t handle;
    ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&cali_config, &handle));
    ESP_ERROR_CHECK(adc_cali_raw_to_voltage(handle, adc_raw[channel],&adc_raw[channel]));
    ESP_ERROR_CHECK(adc_cali_delete_scheme_line_fitting(handle));
    return adc_raw[channel];
}

void uninstall_spin_control()
{
    // Tear Down
    ESP_ERROR_CHECK(adc_oneshot_del_unit(adc1_handle));
}
