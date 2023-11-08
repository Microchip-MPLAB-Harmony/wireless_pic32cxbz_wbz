
# Common function definitions for keys.


# KEYREF_API_FILE Macro

## C

```c
#define KEYREF_API_FILE

```

 @file
 Copyright (c) 2020 Silex Insight. All Rights reserved.


# Returns a reference to a key whose key material is in user memory.


# SX_KEYREF_LOAD_MATERIAL Macro

## C

```c
typedef struct sxkeyref (FUNC_SX_KEYREF_LOAD_MATERIAL)(size_t keysz, const char keymaterial);
#define SX_KEYREF_LOAD_MATERIAL ((FUNC_SX_KEYREF_LOAD_MATERIAL)((uint32_t )(API_TABLE_BASE_ADDRESS + ATO_SX_KEYREF_LOAD_MATERIAL)))

```

 This function loads the user provided key data and returns an initialized
 sxkeyref object.

 The returned object can be passed to any of the sx_aead_create_() or
 sx_blkcipher_create_() functions.

## Parameters

 [in] keysz size of the key to be loaded 

## Parameters

 [in] keymaterial key to be loaded with size \p keysz  @return sxkeyref initialized object with provided inputs  | Param | Description |
|:----- |:----------- |

| @remark | \p keymaterial buffer should not be changed until the operation  is completed. 


# Returns a reference to a key selected by an index.


 This function initializes a sxkeyref object to use predefined hardware keys.
 Currently, predefined hardware keys can be used with AES(BA411) and
 SM4(BA419).

 The returned object can be passed to any of the sx_aead_create_() or
 sx_blkcipher_create_() functions.

## Parameters

 [in] keyindex index of the hardware key, must be 0 or 1.  @return sxkeyref initialized object with configuration of the hardware key  index provided 

