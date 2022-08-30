# PMU_ConfigCurrentSensor Function

## C

```c
bool PMU_ConfigCurrentSensor(bool enable);
```

## Description

 This routine will configure the BUCK current sensor.
 It only can be configured when the power mode is set as PMU_MODE_BUCK_PSM.
 Disable current sensor can improve the current consumption of sleep mode.

## Parameters

| Param | Description |
|:----- |:----------- |
| bool enable | Enable/Disable BUCK current sensor  false: Disable  true : Enable  

## Returns

*bool* - true is success
 false is fail due to power mode is not in PMU_MODE_BUCK_PSM 
