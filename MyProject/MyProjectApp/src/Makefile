# SPDX-FileCopyrightText: 1998 Argonne National Laboratory
#
# SPDX-License-Identifier: EPICS

TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS BELOW HERE

# Use typed rset structure (see 3.16.1 release notes)
USR_CPPFLAGS += -DUSE_TYPED_RSET

# xxxRecord.h will be created from xxxRecord.dbd
DBDINC += xxxRecord

# Install xxxSupport.dbd into <top>/dbd
DBD += xxxSupport.dbd

# Build an IOC support library
LIBRARY_IOC += MyProjectSupport

# Compile and add code to the support library
MyProjectSupport_SRCS += xxxRecord.c
MyProjectSupport_SRCS += devXxxSoft.c

# Link locally-provided code into the support library,
# rather than directly into the IOC application, that
# causes problems on Windows DLL builds
MyProjectSupport_SRCS += dbSubExample.c
MyProjectSupport_SRCS += devMyProjectVersion.c
MyProjectSupport_SRCS += MyProjectHello.c
MyProjectSupport_SRCS += initTrace.c

MyProjectSupport_LIBS += $(EPICS_BASE_IOC_LIBS)

# Auto-generate a header file containing a version string.
# Version comes from the VCS if available, else date+time.
GENVERSION = MyProjectVersion.h
# Macro name
GENVERSIONMACRO = MyProjectVERSION

# Build the IOC application
PROD_IOC = MyProject

# MyProject.dbd will be created and installed
DBD += MyProject.dbd

# MyProject.dbd will include these files:
MyProject_DBD += base.dbd
MyProject_DBD += xxxSupport.dbd
MyProject_DBD += dbSubExample.dbd
MyProject_DBD += devMyProjectVersion.dbd
MyProject_DBD += MyProjectHello.dbd
MyProject_DBD += initTrace.dbd

# MyProject_registerRecordDeviceDriver.cpp derives from MyProject.dbd
MyProject_SRCS += MyProject_registerRecordDeviceDriver.cpp

# Build the main IOC entry point where needed
MyProject_SRCS_DEFAULT += MyProjectMain.cpp
MyProject_SRCS_vxWorks += -nil-

# Link in the code from our support library
MyProject_LIBS += MyProjectSupport

# To build SNL programs, SNCSEQ must be defined
# in the <top>/configure/RELEASE file
ifneq ($(SNCSEQ),)
    # Build sncExample into MyProjectSupport
    sncExample_SNCFLAGS += +r
    MyProject_DBD += sncExample.dbd
    # A .stt sequence program is *not* pre-processed:
    MyProjectSupport_SRCS += sncExample.stt
    MyProjectSupport_LIBS += seq pv
    MyProject_LIBS += seq pv

    # Build sncProgram as a standalone program
    PROD_HOST += sncProgram
    sncProgram_SNCFLAGS += +m
    # A .st sequence program *is* pre-processed:
    sncProgram_SRCS += sncProgram.st
    sncProgram_LIBS += seq pv
    sncProgram_LIBS += $(EPICS_BASE_HOST_LIBS)
endif

# Link QSRV (pvAccess Server) if available
ifdef EPICS_QSRV_MAJOR_VERSION
    MyProject_LIBS += qsrv
    MyProject_LIBS += $(EPICS_BASE_PVA_CORE_LIBS)
    MyProject_DBD += PVAServerRegister.dbd
    MyProject_DBD += qsrv.dbd
endif

# Finally link IOC to the EPICS Base libraries
MyProject_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD EXTRA GNUMAKE RULES BELOW HERE

# Explicit dependency needed for generated header file
devMyProjectVersion$(DEP): $(COMMON_DIR)/$(GENVERSION)
