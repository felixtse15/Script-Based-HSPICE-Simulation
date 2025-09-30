*PDK Library
.LIB "./sky130_model/sky130.spice" tt

**************************************************************************************
* Hspice Options
* Accuracy Control

.option	method=gear accurate=1 runlvl=6 gmin=1e-21 gmindc=1e-21 
.option absmos=1e-12 relmos=1e-4 relv=1e-4 relvdc=1e-4
.option	ingold=2 $ ingold=0: Engineering Format, ingold=2: E-Format
.option measdgt=7 numdgt=7 mcbrief=1 nopage nomod 
.option post

*=======================================================================================
* PARAMETERS, POWER SUPPLIES

.PARAM
+      vdd = 1.8
+      len = 150n
+      wid_p = 900n
+      wid_n = 360n

**	DRIVER-PARAMS	**


**	END-PARAMS	**

*=======================================================================================
* CIRCUITS

.subckt inv in out vdd vss Wp=wid_p Wn=wid_n
Xm1 out in vss vss NMOS_VTG L='len' W=Wn
Xm0 out in vdd vdd PMOS_VTG L='len' W=Wp
.ends


**	DRIVER-STAGES	**
X_driver0 DIN node_measure vdd vss inv Wp="wid_p" Wn="wid_n"

**	END-STAGES	**

*32 load inverters and 1f cap
X_load1 node_measure out1 vdd vss inv 
c1 out1 vss 1f

X_load2 node_measure out2 vdd vss inv
c2 out2 vss 1f

X_load3 node_measure out3 vdd vss inv
c3 out3 vss 1f

X_load4 node_measure out4 vdd vss inv
c4 out4 vss 1f

X_load5 node_measure out5 vdd vss inv
c5 out5 vss 1f

X_load6 node_measure out6 vdd vss inv
c6 out6 vss 1f

X_load7 node_measure out7 vdd vss inv
c7 out7 vss 1f

X_load8 node_measure out8 vdd vss inv
c8 out8 vss 1f

X_load9 node_measure out9 vdd vss inv
c9 out9 vss 1f

X_load10 node_measure out10 vdd vss inv
c10 out10 vss 1f

X_load11 node_measure out11 vdd vss inv
c11 out11 vss 1f

X_load12 node_measure out12 vdd vss inv
c12 out12 vss 1f

X_load13 node_measure out13 vdd vss inv
c13 out13 vss 1f

X_load14 node_measure out14 vdd vss inv
c14 out14 vss 1f

X_load15 node_measure out15 vdd vss inv
c15 out15 vss 1f

X_load16 node_measure out16 vdd vss inv
c16 out16 vss 1f

X_load17 node_measure out17 vdd vss inv
c17 out17 vss 1f

X_load18 node_measure out18 vdd vss inv
c18 out18 vss 1f

X_load19 node_measure out19 vdd vss inv
c19 out19 vss 1f

X_load20 node_measure out20 vdd vss inv
c20 out20 vss 1f

X_load21 node_measure out21 vdd vss inv
c21 out21 vss 1f

X_load22 node_measure out22 vdd vss inv
c22 out22 vss 1f

X_load23 node_measure out23 vdd vss inv
c23 out23 vss 1f

X_load24 node_measure out24 vdd vss inv
c24 out24 vss 1f

X_load25 node_measure out25 vdd vss inv
c25 out25 vss 1f

X_load26 node_measure out26 vdd vss inv
c26 out26 vss 1f

X_load27 node_measure out27 vdd vss inv
c27 out27 vss 1f

X_load28 node_measure out28 vdd vss inv
c28 out28 vss 1f

X_load29 node_measure out29 vdd vss inv
c29 out29 vss 1f

X_load30 node_measure out30 vdd vss inv
c30 out30 vss 1f

X_load31 node_measure out31 vdd vss inv
c31 out31 vss 1f

X_load32 node_measure out32 vdd vss inv
c32 out32 vss 1f
  
 
*50f load capacitance
c_wire node_measure vss 50f


*=======================================================================================
* Initial Conditions

.IC
+    V(DIN)=0

*=======================================================================================
*Controls

v1 vss 0 DC=0
v0 vdd 0 DC='vdd'
v2 DIN 0 PWL 0 0 200p 0 220p 1.8 1.22n 1.8 1.24n 0

*=======================================================================================
*Analysis

.TEMP 25.0
.TRAN 1p 2n 

.PROBE TRAN
+    V(node_measure)
+    V(DIN)

.OP
.measure TRAN delay TRIG V(DIN) VAL=0.9 RISE=1 TARG V(node_measure) VAL=0.9 RISE=1
.measure TRAN charge_total INTEGRAL -i(v0) FROM=0 TO=2n
.measure TRAN energy_total PARAM = 'vdd * charge_total'
*=======================================================================================
* Use Alter command to simulate other cases






.END
