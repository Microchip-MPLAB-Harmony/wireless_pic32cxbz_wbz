
# SilexPK status codes


 @file

# SX_PK_STATUSCODES_HEADER_FILE Macro

## C

```c
#define SX_PK_STATUSCODES_HEADER_FILE

```
/
 Copyright (c) 2018-2020 Silex Insight sa
 Copyright (c) 2018-2020 Beerten Engineering scs
 SPDX-License-Identifier: BSD-3-Clause



# SX_ERR_IK_MODE Function

## C

```c
#define SX_ERR_IK_MODE 16
```

 @addtogroup SX_PK_STATUS

 @{

# The function or operation succeeded */


# The function or operation was given an invalid parameter */


# SX_ERR_INVALID_PARAM Macro

## C

```c
#define SX_ERR_INVALID_PARAM 1

```



# Unknown error */


# The operation is still executing */


# SX_ERR_BUSY Macro

## C

```c
#define SX_ERR_BUSY 3

```



# The input operand is not a quadratic residue */


# The input value for Rabin-Miller test is a composite value */


# SX_ERR_COMPOSITE_VALUE Macro

## C

```c
#define SX_ERR_COMPOSITE_VALUE 5

```



# Inversion of non-invertible value */


# The signature is not valid


# SX_ERR_INVALID_SIGNATURE Macro

## C

```c
#define SX_ERR_INVALID_SIGNATURE 7

```


 This error can happen during signature generation
 and signature verification

# The functionality or operation is not supported */


# The output operand is a point at infinity */


# SX_ERR_POINT_AT_INFINITY Macro

## C

```c
#define SX_ERR_POINT_AT_INFINITY 9

```



# The input value is outside the expected range */


# The modulus has an unexpected value


# SX_ERR_INVALID_MODULUS Macro

## C

```c
#define SX_ERR_INVALID_MODULUS 11

```


 This error happens when the modulus is zero or
 even when odd modulus is expected

# The input point is not on the defined elliptic curve */


# The input operand is too large */


# SX_ERR_OPERAND_TOO_LARGE Macro

## C

```c
#define SX_ERR_OPERAND_TOO_LARGE 13

```



# A platform specific error */


# The evaluation period for the product expired */


# SX_ERR_EXPIRED Macro

## C

```c
#define SX_ERR_EXPIRED 15

```



# The hardware is still in IK mode


# SX_ERR_IK_MODE Macro

## C

```c
#define SX_ERR_IK_MODE 16

```

 This error happens when a normal operation
 is started and the hardware is still in IK mode.
 Run command ::SX_PK_CMD_IK_EXIT to exit the IK
 mode and to run normal operations again

# The parameters of the elliptic curve are not valid. */


# Return a brief text string describing the given status code.


# char Typedef

## C

```c
typedef const char (FUNC_SX_DESCRIBE_STATUSCODE)(int code);

```

# SX_DESCRIBE_STATUSCODE Macro

## C

```c
#define SX_DESCRIBE_STATUSCODE ((FUNC_SX_DESCRIBE_STATUSCODE)((uint32_t )(API_TABLE_BASE_ADDRESS + ATO_SX_DESCRIBE_STATUSCODE)))

```


## Parameters

 [in] code Value of status code  @return Text string describing the status code 


