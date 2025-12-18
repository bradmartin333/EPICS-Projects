#!../../bin/windows-x64/MyProject

#- SPDX-FileCopyrightText: 2000 Argonne National Laboratory
#-
#- SPDX-License-Identifier: EPICS

#- You may have to change MyProject to something else
#- everywhere it appears in this file

# 1. LOAD ENVIRONMENT VARIABLES FIRST
# This uses the absolute path to ensure $(TOP) and $(IOC) are defined.
< C:/Users/bradm/Downloads/EPICS_PROJECTS/MyProject/iocBoot/iocMyProject/envPaths

# 2. OPTIONAL: Change directory to the application root.
# This is often helpful for relative paths used in other commands.
cd "$(TOP)"

## 3. Register all support components
# Use $(TOP) to ensure the path to the DBD file is correct.
dbLoadDatabase "$(TOP)/dbd/MyProject.dbd"
MyProject_registerRecordDeviceDriver pdbbase

## 4. Load record instances
dbLoadTemplate "$(TOP)/db/user.substitutions"
dbLoadRecords "$(TOP)/db/MyProjectVersion.db", "user=bradm"
dbLoadRecords "$(TOP)/db/dbSubExample.db", "user=bradm"

#- Set this to see messages from mySub
#-var mySubDebug 1

#- Run this to trace the stages of iocInit
#-traceIocInit

# 5. Initialize the IOC
iocInit

## Start any sequence programs
#seq sncExample, "user=bradm"