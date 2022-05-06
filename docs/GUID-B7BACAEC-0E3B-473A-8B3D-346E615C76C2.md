# PMU\_ConfigCurrentSensor Function

**Parent topic:**[PMU System](GUID-4F3FCED2-8D39-4756-838A-1248B8A619A4.md)

## C

```c
bool PMU_ConfigCurrentSensor(bool enable);
```

## Description

This routine will configure the BUCK current sensor. It only can be configured when the power mode is set as PMU\_MODE\_BUCK\_PSM. Disable current sensor can improve the current consumption of sleep mode.

## Parameters

|Param|Description|
|-----|-----------|
|bool enable|Enable/Disable BUCK current sensor false: Disable true : Enable|

## Returns

*bool* - true is success false is fail due to power mode is not in PMU\_MODE\_BUCK\_PSM

