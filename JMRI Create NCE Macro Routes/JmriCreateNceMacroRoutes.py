## This script is designed to be used with JMRI. When run within JMRI
#  PanelPro, this script will create 1 Route, 1 Sensor, and 1 Logix
#  Conditional for each of N macros, defined by @ref NUM_MACROS. The
#  Route activates the Sensor. The Logix Conditional detects the Sensor
#  activation (Conditional Variable) and subsequently activates
#  a Conditional Action to both reset the sensor to inactive after a brief
#  delay and activeate a Conditional Action to execute Jython, which in
#  turn, sends the NCE macro command to the NCE computer inteface.
#
#  @copyright
#  Copyright (C) 2020 Stuart W Baker
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or (at
#  your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  @author Stuart W Baker
#  @date 19 July 2020

import jmri
import java

## Number of supported Macros.
# - 16 - PowerCab
# - 16 - SB3a
# - 256 - PowerPro CS02
NUM_MACROS = 256

## The Jython script.
JYTHON_CMD = \
"""
import jmri
import java

class MyNceListener(jmri.jmrix.nce.NceListener):
  def message(self, msg):
    return
  def reply(self, msg):
    return

mnl = MyNceListener()

# Get the traffic controller
tc = None
try:
  tc = jmri.InstanceManager.getDefault( \\
    jmri.jmrix.nce.NceSystemConnectionMemo).getNceTrafficController()
except:
  print \"No Traffic Controller\"

if (tc != None):
  if (tc.getCommandOptions() >=
      jmri.jmrix.nce.NceTrafficController.OPTION_2006):
    m = jmri.jmrix.nce.NceMessage(5)
    m.setElement(0, jmri.jmrix.nce.NceMessage.SEND_ACC_SIG_MACRO_CMD)
    m.setElement(1, 0x00) # addr_h
    m.setElement(2, 0x01) # addr_l
    m.setElement(3, 0x01) # Macro cmd
    m.setElement(4, %d)   # Macro #
    m.setBinary(True)
    m.setReplyLen(jmri.jmrix.nce.NceMessage.REPLY_1)
    tc.sendNceMessage(m, mnl)

  # Unfortunately, the new command doesn't tell us if the macro is
  # empty, so we send the old command for status.
  m = jmri.jmrix.nce.NceMessage(2)
  m.setElement(0, jmri.jmrix.nce.NceMessage.MACRO_CMD)
  m.setElement(1, %d) # Macro #
  m.setBinary(True)
  m.setReplyLen(jmri.jmrix.nce.NceMessage.REPLY_1)
  tc.sendNceMessage(m, mnl)
"""

# get reference to managers
lm = jmri.InstanceManager.getDefault(jmri.LogixManager)
cm = jmri.InstanceManager.getDefault(jmri.ConditionalManager)


# create logix entry
l = lm.getBySystemName("IXNCEM")
if (l != None):
  lm.deleteLogix(l)
l = lm.createNewLogix("IXNCEM", "NCE Macro Senders")

# one iteration for each of NUM_MACROS
for i in range (0, NUM_MACROS):
  # create sensor
  s = None
  try:
    s = sensors.newSensor("IS:NCEM:" + str(i), \
                          "NCE Macro " + str(i) + " Trigger")
  except:
    print "Sensor " + str(i) + " not created"

  # create route
  r_name = "Macro " + str(i)
  r = routes.getBySystemName("IR:NCEM:" + str(i))
  if (r != None):
    # overide default name before deleting
    r_name = r.getUserName()
    routes.deleteRoute(r)
  r = routes.provideRoute("IR:NCEM:" + str(i), r_name)

  # create conditional
  c = cm.getBySystemName("IXNCEMC" + str(i))
  if (c != None):
    cm.deleteConditional(c)
  c = cm.createNewConditional("IXNCEMC" + str(i), "Macro " + str(i))
  c.setLogicType(jmri.Conditional.AntecedentOperator. \
                 getOperatorFromIntValue(jmri.Conditional.ALL_AND), "R1")

  if (l != None and s != None and r != None and c != None):
    # tie it all the elements together
    r.addOutputSensor("IS:NCEM:" + str(i), jmri.Sensor.ACTIVE)
    r.setEnabled(True)
    l.deleteConditional("IXNCEMC" + str(i))
    l.addConditional("IXNCEMC" + str(i), -1)
    c.setTriggerOnChange(True)

    # create our conditional variable to listen for the sensor
    cv = jmri.ConditionalVariable( \
      False, jmri.Conditional.Operator.getOperatorFromIntValue( \
        jmri.Conditional.OPERATOR_NONE), \
      jmri.Conditional.Type.getOperatorFromIntValue( \
        jmri.Conditional.TYPE_SENSOR_ACTIVE), \
      "IS:NCEM:" + str(i), True)

    # associate our conditional variable with the conditional
    c.setStateVariables([cv])

    # create our conditional action to reset the sensor after delay
    ca1 = jmri.implementation.DefaultConditionalAction( \
      1, jmri.Conditional.Action.getOperatorFromIntValue( \
        jmri.Conditional.ACTION_DELAYED_SENSOR), \
      "IS:NCEM:" + str(i), 4, "0.5")

    # create our conditional action which executes Jython script to send macro
    ca2 = jmri.implementation.DefaultConditionalAction( \
      1, jmri.Conditional.Action.getOperatorFromIntValue( \
        jmri.Conditional.ACTION_JYTHON_COMMAND), \
      " ", -1, JYTHON_CMD % (i, i))

    # associate our conditional actions with the conditional
    c.setAction([ca1, ca2])
  
  else:
    print "object error on macro " + str(i) + " creation"

# makd logix active
l.setEnabled(True)
l.activateLogix()

print "success"
  
