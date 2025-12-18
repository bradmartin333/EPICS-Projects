#!../../bin/windows-x64/MyProject

#- SPDX-FileCopyrightText: 2000 Argonne National Laboratory
#-
#- SPDX-License-Identifier: EPICS

#- You may have to change MyProject to something else
#- everywhere it appears in this file

< ./envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/MyProject.dbd"
MyProject_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadTemplate "db/user.substitutions"
dbLoadRecords "db/MyProjectVersion.db", "user=bradm"
dbLoadRecords "db/dbSubExample.db", "user=bradm"

#- Set this to see messages from mySub
#-var mySubDebug 1

#- Run this to trace the stages of iocInit
#-traceIocInit

cd "${TOP}/iocBoot/${IOC}"
iocInit

## Start any sequence programs
#seq sncExample, "user=bradm"
