# PMU_Mode_T Enum

## C

```c
typedef enum
{
    // Linear mode - This is the default mode when CPU and peripherals are running.
    PMU_MODE_MLDO = 1,
    // Buck (DC-DC/switching) mode; supports High Power (PWM) - The most efficient mode
    //when the CPU and peripherals are running. In this mode, the SoC is powered by the DC-DC converter
    PMU_MODE_BUCK_PWM, // 2
    // Buck (DC-DC/switching) mode; supports Low Power (PSK) mode
    PMU_MODE_BUCK_PSM // 3
} PMU_Mode_T;

```



