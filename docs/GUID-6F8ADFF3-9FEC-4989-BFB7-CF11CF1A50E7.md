
# Semantic version numbers of the SilexPK API.


 The version numbering used here adheres to the concepts outlined in
 https://semver.org/.

 @file

# SX_PK_VERSION_HEADER_FILE Macro

## C

```c
#define SX_PK_VERSION_HEADER_FILE

```
/
 Copyright (c) 2018-2020 Silex Insight sa
 Copyright (c) 2014-2020 Beerten Engineering scs
 SPDX-License-Identifier: BSD-3-Clause


# Major version number of the SilexPK API


# SX_PK_API_MAJOR Macro

## C

```c
#define SX_PK_API_MAJOR 1

```

 Changes made to the API with the same major version number remain
 backwards compatible. Applications should check at compile time that
 current major version number matches the one they were made for.

# Minor version number of the SilexPK API


# SX_PK_API_MINOR Macro

## C

```c
#define SX_PK_API_MINOR 4

```

 New features added while maintaining backwards compatibility increment
 the minor version number. Applications should check that the minor
 version number is equal or larger than the minor version number
 they were written for.

# Check application has compatible version numbers.


# SX_PK_API_IS_COMPATIBLE(appmajor, Macro

## C

```c
#define SX_PK_API_IS_COMPATIBLE(appmajor, appminor) \

```

 Non-zero if the API is compatible and zero if incompatible.
 The application is compatible if the major number does matches
 the library major number and the application minor number is equal or
 smaller than the library minor number.

# Assert that the application is compatible with the library


# SX_PK_API_ASSERT_COMPATIBLE(appmajor, Macro

## C

```c
#define SX_PK_API_ASSERT_COMPATIBLE(appmajor, appminor) \

```

 If the application is not compatible, this macro will cause a compile
 time error.
