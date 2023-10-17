/* ************************************************************************** */
/** Register Definitions

  @Company
    Microchip Technology

  @File Name
    regdef.h

  @Summary
    Brief description of the file.

  @Description
    Describe the purpose of this file.
 */
/* ************************************************************************** */
#include <stdint.h>
//#include "pic32cx5109bz31048_fpga.h"

#ifndef _REGDEF_H    /* Guard against multiple inclusion */
#define _REGDEF_H



#define _ROT_BASE_ADDRESS                       ROT_BASE_ADDRESS
   

//Efusecon address is _ROT_BASE_ADDRESS + 0xC08
//#define EFUSECON (ROT_REGS->ROT_EFUSE_CON)
#define EFUSECON (*((volatile unsigned int *) (0x44003808) ))
//typedef union {
//  struct {
//    uint32_t PGM1BIT:1;
//    uint32_t PGMMODE:1;
//    uint32_t :3;
//    uint32_t ENLD:1;
//    uint32_t ENLDALL:1;
//    uint32_t ENPGM:1;
//    uint32_t :24;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __EFUSECONbits_t;
//extern volatile __EFUSECONbits_t EFUSECONbits __asm__ ("EFUSECON") __attribute__((section("sfrs"), address(0x44003808)));

//#define EFUSERWDATA (ROT_REGS->ROT_EFUSE_RWDATA)
#define EFUSERWDATA (*((volatile unsigned int *) (0x44003804) ))
//
//typedef union {
//  struct {
//    uint32_t DATA:8;
//    uint32_t :32;
//    uint32_t ADDR:12;
//    uint32_t :4;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __EFUSERWDATAbits_t;
//extern volatile __EFUSERWDATAbits_t EFUSERWDATAbits __asm__ ("EFUSERWDATA") __attribute__((section("sfrs"), address(0x44003804)));


//#define SECBOOT (ROT_REGS->ROT_SEC_BOOT)
#define SECBOOT (*((volatile unsigned int *) (0x44003800) ))

//#define SECBOOT SECBOOT
//extern volatile uint32_t   SECBOOT __attribute__((section("sfrs"), address(0x44003800)));
//typedef union {
//  struct {
//    uint32_t SECBOOTREQD:2;
//    uint32_t :6;
//    uint32_t BOOTSTATUS:8;
//    uint32_t SECBOOTDONE:2;
//    uint32_t :14;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __SECBOOTbits_t;
//extern volatile __SECBOOTbits_t SECBOOTbits __asm__ ("SECBOOT") __attribute__((section("sfrs"), address(0x44003800)));

#define UUID4 UUID4
extern volatile uint32_t   UUID4 __attribute__((section("sfrs"), address(0x44002D7C)));
#define UUID3 UUID3
extern volatile uint32_t   UUID3 __attribute__((section("sfrs"), address(0x44002D78)));
#define UUID2 UUID2
extern volatile uint32_t   UUID2 __attribute__((section("sfrs"), address(0x44002D74)));
#define UUID1 UUID1
extern volatile uint32_t   UUID1 __attribute__((section("sfrs"), address(0x44002D70)));

#define FCFG FCFG
extern volatile uint32_t   FCFG __attribute__((section("sfrs"), address(0x44002c74)));
#define ROOTKEY9 ROOTKEY9
extern volatile uint32_t   ROOTKEY9 __attribute__((section("sfrs"), address(0x44002c74)));
typedef union {
  struct {
    uint32_t BOOTKEY:16;
    uint32_t ROOTKEY:16;
  };
  struct {
    uint32_t w:32;
  };
} __FCFGRK9bits_t;
extern volatile __FCFGRK9bits_t FCFGbits __asm__ ("FCFG") __attribute__((section("sfrs"), address(0x44002C74)));
extern volatile __FCFGRK9bits_t ROOTKEY9bits __asm__ ("ROOTKEY9") __attribute__((section("sfrs"), address(0x44002C74)));

#define ROOTKEY8 ROOTKEY8
extern volatile uint32_t   ROOTKEY8 __attribute__((section("sfrs"), address(0x44002C70)));
#define ROOTKEY7 ROOTKEY7
extern volatile uint32_t   ROOTKEY7 __attribute__((section("sfrs"), address(0x44002C6C)));
#define ROOTKEY6 ROOTKEY6
extern volatile uint32_t   ROOTKEY6 __attribute__((section("sfrs"), address(0x44002C68)));
#define ROOTKEY5 ROOTKEY5
extern volatile uint32_t   ROOTKEY5 __attribute__((section("sfrs"), address(0x44002C64)));
#define ROOTKEY4 ROOTKEY4
extern volatile uint32_t   ROOTKEY4 __attribute__((section("sfrs"), address(0x44002C60)));
#define ROOTKEY3 ROOTKEY3
extern volatile uint32_t   ROOTKEY3 __attribute__((section("sfrs"), address(0x44002C5C)));
#define ROOTKEY2 ROOTKEY2
extern volatile uint32_t   ROOTKEY2 __attribute__((section("sfrs"), address(0x44002C58)));
#define ROOTKEY1 ROOTKEY1
extern volatile uint32_t   ROOTKEY1 __attribute__((section("sfrs"), address(0x44002C54)));

#define BOOTKEY13 BOOTKEY13
extern volatile uint32_t   BOOTKEY13 __attribute__((section("sfrs"), address(0x44002C54)));
typedef union {
  struct {
    uint32_t BOOTKEY:16;
    uint32_t ROOTKEY:16;
  };
  struct {
    uint32_t w:32;
  };
} __RK1BK13bits_t;
extern volatile __RK1BK13bits_t ROOTKEY1bits __asm__ ("ROOTKEY1") __attribute__((section("sfrs"), address(0x44002C54)));
extern volatile __RK1BK13bits_t BOOTKEY13bits __asm__ ("BOOTKEY13") __attribute__((section("sfrs"), address(0x44002C54)));

#define BOOTKEY12 BOOTKEY12
extern volatile uint32_t   BOOTKEY12 __attribute__((section("sfrs"), address(0x44002C50)));
#define BOOTKEY11 BOOTKEY11
extern volatile uint32_t   BOOTKEY11 __attribute__((section("sfrs"), address(0x44002C4C)));
#define BOOTKEY10 BOOTKEY10
extern volatile uint32_t   BOOTKEY10 __attribute__((section("sfrs"), address(0x44002C48)));
#define BOOTKEY9 BOOTKEY9
extern volatile uint32_t   BOOTKEY9 __attribute__((section("sfrs"), address(0x44002C44)));
#define BOOTKEY8 BOOTKEY8
extern volatile uint32_t   BOOTKEY8 __attribute__((section("sfrs"), address(0x44002C40)));
#define BOOTKEY7 BOOTKEY7
extern volatile uint32_t   BOOTKEY7 __attribute__((section("sfrs"), address(0x44002C3C)));
#define BOOTKEY6 BOOTKEY6
extern volatile uint32_t   BOOTKEY6 __attribute__((section("sfrs"), address(0x44002C38)));
#define BOOTKEY5 BOOTKEY5
extern volatile uint32_t   BOOTKEY5 __attribute__((section("sfrs"), address(0x44002C34)));
#define BOOTKEY4 BOOTKEY4
extern volatile uint32_t   BOOTKEY4 __attribute__((section("sfrs"), address(0x44002C30)));
#define BOOTKEY3 BOOTKEY3
extern volatile uint32_t   BOOTKEY3 __attribute__((section("sfrs"), address(0x44002C2C)));
#define BOOTKEY2 BOOTKEY2
extern volatile uint32_t   BOOTKEY2 __attribute__((section("sfrs"), address(0x44002C28)));
#define BOOTKEY1 BOOTKEY1
extern volatile uint32_t   BOOTKEY1 __attribute__((section("sfrs"), address(0x44002C24)));

#define LCCTR  (*((volatile unsigned int *) (0x44002C24) ))
//#define LCCTR LCCTR
//extern volatile uint32_t   LCCTR __attribute__((section("sfrs"), address(0x44002C24)));
//typedef union {
//  struct {
//    uint32_t LCC:4;
//    uint32_t :12;
//    uint32_t BOOTKEY:16;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __LCCTRBK1bits_t;
//extern volatile __LCCTRBK1bits_t LCCTRbits __asm__ ("LCCTRbits") __attribute__((section("sfrs"), address(0x44002C24)));
//extern volatile __LCCTRBK1bits_t BOOTKEY1bits __asm__ ("BOOTKEY1bits") __attribute__((section("sfrs"), address(0x44002C24)));


//#define RBCTR RBCTR
#define RBCTR (*((volatile unsigned int *) (0x44002C04) ))
//extern volatile uint32_t   RBCTR __attribute__((section("sfrs"), address(0x44002C04)));
//typedef union {
//  struct {
//    uint32_t RBCTR:8;
//    uint32_t :24;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __RBCTRbits_t;
//extern volatile __RBCTRbits_t RBCTRbits __asm__ ("RBCTR") __attribute__((section("sfrs"), address(0x44002C04)));

//#define SECCFG ROT_REGS->ROT_SECCFG
#define SECCFG (*((volatile unsigned int *) (0x44002C00) ))
//extern volatile uint32_t   SECCFG __attribute__((section("sfrs"), address(0x44002C00)));
//typedef union {
//  struct {
//    uint32_t :2;
//    uint32_t CPROT:2;
//    uint32_t UUIDLCK:2;
//    uint32_t DBGLCK:2;
//    uint32_t ROOTKEYLCK:2;
//    uint32_t BOOTKEYLCK:2;
//    uint32_t :2;
//    uint32_t PATCHLCK:2;
//    uint32_t ADDBOOTKEY:1;
//    uint32_t :15;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __SECCFGbits_t;
//extern volatile __SECCFGbits_t SECCFGbits __asm__ ("SECCFG") __attribute__((section("sfrs"), address(0x44002C00)));

#define MISCDIAG (*((volatile unsigned int *) (0x44000440) ))
//extern volatile uint32_t   MISCDIAG __attribute__((section("sfrs"), address(0x44000440)));
//typedef union {
//  struct {
//    uint32_t TMODEOUT:4;
//    uint32_t DET1ACT:1;
//    uint32_t DET2ACT:1;
//    uint32_t DET3ACT:1;
//    uint32_t DET4ACT:1;
//    uint32_t PUBTM:1;
//    uint32_t PRIVTM:1;
//    uint32_t :6;
//    uint32_t PMURO:1;
//    uint32_t UVR1RO:1;
//    uint32_t UVR1BO:1;
//    uint32_t UVR2RO:1;
//    uint32_t UVR2BO:1;
//    uint32_t FPORRA:1;
//    uint32_t BORBYP:1;
//    uint32_t LDORDBYP:1;
//    uint32_t SPLLFSMRUN:1;
//    uint32_t SLOCK:1;
//    uint32_t SPLLREQ:1;
//    uint32_t :4;
//    uint32_t CXDIAG:1;
//  };
//  struct {
//    uint32_t w:32;
//  };
//} __MISCDIAGbits_t;
//extern volatile __MISCDIAGbits_t MISCDIAGbits __asm__ ("MISCDIAG") __attribute__((section("sfrs"), address(0x44000440)));
//extern volatile uint32_t        MISCDIAGCLR __attribute__((section("sfrs"),address(0x44000444)));
//extern volatile uint32_t        MISCDIAGSET __attribute__((section("sfrs"),address(0x44000448)));
//extern volatile uint32_t        MISCDIAGINV __attribute__((section("sfrs"),address(0x4400044C)));
#define  MISCDBG (*((volatile unsigned int *) (0x44000100) ))

#define MISCDBGCLR (*((volatile unsigned int *) (0x44000104) ))

/* Provide C++ Compatibility */
#ifdef __cplusplus
extern "C" {
#endif

#ifdef __cplusplus
}
#endif

#endif
/* *****************************************************************************
 End of File
 */
