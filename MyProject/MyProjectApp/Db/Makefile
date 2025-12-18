# SPDX-FileCopyrightText: 1998 Argonne National Laboratory
#
# SPDX-License-Identifier: EPICS

TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS BELOW HERE

# Install databases, templates & substitutions like this
DB += beam_dump.db
DB += cryo.db
DB += dbSubExample.db
DB += MyProjectVersion.db
DB += rf.db
DB += tungsten_target.db
DB += user.substitutions
DB += vacuum.db

# If <anyname>.db template is not named <anyname>*.template add
# <anyname>_TEMPLATE = <templatename>

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD EXTRA GNUMAKE RULES BELOW HERE

