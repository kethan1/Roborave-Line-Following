EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R1
U 1 1 61809FFB
P 4100 3550
F 0 "R1" H 4170 3596 50  0000 L CNN
F 1 "R" H 4170 3505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4030 3550 50  0001 C CNN
F 3 "~" H 4100 3550 50  0001 C CNN
	1    4100 3550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 6180C34D
P 4100 3850
F 0 "R2" H 4170 3896 50  0000 L CNN
F 1 "R" H 4170 3805 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4030 3850 50  0001 C CNN
F 3 "~" H 4100 3850 50  0001 C CNN
	1    4100 3850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 6180CB94
P 4100 4150
F 0 "R3" H 4030 4104 50  0000 R CNN
F 1 "R" H 4030 4195 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4030 4150 50  0001 C CNN
F 3 "~" H 4100 4150 50  0001 C CNN
	1    4100 4150
	-1   0    0    1   
$EndComp
$Comp
L Device:R R4
U 1 1 6180D509
P 4600 3550
F 0 "R4" H 4670 3596 50  0000 L CNN
F 1 "R" H 4670 3505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4530 3550 50  0001 C CNN
F 3 "~" H 4600 3550 50  0001 C CNN
	1    4600 3550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R5
U 1 1 6180EB88
P 4600 3850
F 0 "R5" H 4670 3896 50  0000 L CNN
F 1 "R" H 4670 3805 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4530 3850 50  0001 C CNN
F 3 "~" H 4600 3850 50  0001 C CNN
	1    4600 3850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R6
U 1 1 6180F41C
P 4600 4150
F 0 "R6" H 4670 4196 50  0000 L CNN
F 1 "R" H 4670 4105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4530 4150 50  0001 C CNN
F 3 "~" H 4600 4150 50  0001 C CNN
	1    4600 4150
	1    0    0    -1  
$EndComp
$Comp
L Device:R R7
U 1 1 61816C43
P 5050 3550
F 0 "R7" H 5120 3596 50  0000 L CNN
F 1 "R" H 5120 3505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4980 3550 50  0001 C CNN
F 3 "~" H 5050 3550 50  0001 C CNN
	1    5050 3550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R8
U 1 1 61818B79
P 5050 3850
F 0 "R8" H 5120 3896 50  0000 L CNN
F 1 "R" H 5120 3805 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4980 3850 50  0001 C CNN
F 3 "~" H 5050 3850 50  0001 C CNN
	1    5050 3850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R9
U 1 1 6181910A
P 5050 4150
F 0 "R9" H 5120 4196 50  0000 L CNN
F 1 "R" H 5120 4105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4980 4150 50  0001 C CNN
F 3 "~" H 5050 4150 50  0001 C CNN
	1    5050 4150
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 4300 4100 4750
Wire Wire Line
	4100 4750 4600 4750
Connection ~ 4600 4750
Wire Wire Line
	4600 4750 5050 4750
Wire Wire Line
	4600 4300 4600 4750
Wire Wire Line
	5050 4300 5050 4750
Wire Wire Line
	5050 3700 4950 3700
Connection ~ 5050 3700
Wire Wire Line
	4600 3700 4500 3700
Connection ~ 4600 3700
Wire Wire Line
	4100 3700 4000 3700
Connection ~ 4100 3700
$Comp
L Connector:Screw_Terminal_01x02 J4
U 1 1 6182DEF1
P 6900 3200
F 0 "J4" V 6864 3012 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 6773 3012 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 6900 3200 50  0001 C CNN
F 3 "~" H 6900 3200 50  0001 C CNN
	1    6900 3200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J5
U 1 1 6183D280
P 5350 3200
F 0 "J5" V 5314 3012 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 5223 3012 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 5350 3200 50  0001 C CNN
F 3 "~" H 5350 3200 50  0001 C CNN
	1    5350 3200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J6
U 1 1 6183E1B5
P 5700 3200
F 0 "J6" V 5664 3012 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 5573 3012 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 5700 3200 50  0001 C CNN
F 3 "~" H 5700 3200 50  0001 C CNN
	1    5700 3200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J7
U 1 1 6183FE2C
P 6050 3200
F 0 "J7" V 6014 3012 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 5923 3012 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 6050 3200 50  0001 C CNN
F 3 "~" H 6050 3200 50  0001 C CNN
	1    6050 3200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J8
U 1 1 61841035
P 6400 3200
F 0 "J8" V 6364 3012 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 6273 3012 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 6400 3200 50  0001 C CNN
F 3 "~" H 6400 3200 50  0001 C CNN
	1    6400 3200
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7000 3400 7000 3450
Wire Wire Line
	7000 4750 6500 4750
Connection ~ 5050 4750
Wire Wire Line
	6500 3400 6500 4750
Connection ~ 6500 4750
Wire Wire Line
	6500 4750 6150 4750
Wire Wire Line
	6150 3400 6150 4750
Connection ~ 6150 4750
Wire Wire Line
	6150 4750 5800 4750
Wire Wire Line
	5800 3400 5800 4750
Connection ~ 5800 4750
Wire Wire Line
	5450 3400 5450 4750
Wire Wire Line
	5050 4750 5450 4750
Connection ~ 5450 4750
Wire Wire Line
	5450 4750 5800 4750
Wire Wire Line
	6900 3400 6700 3400
Wire Wire Line
	6700 3400 6700 3050
Wire Wire Line
	6700 3050 6300 3050
Wire Wire Line
	6300 3050 6300 3400
Wire Wire Line
	6300 3400 6400 3400
Wire Wire Line
	5250 3050 5250 3400
Wire Wire Line
	5250 3400 5350 3400
Connection ~ 6300 3050
Wire Wire Line
	5600 3050 5600 3400
Wire Wire Line
	5600 3400 5700 3400
Connection ~ 5600 3050
Wire Wire Line
	5600 3050 5250 3050
Wire Wire Line
	5600 3050 5950 3050
Wire Wire Line
	6050 3400 5950 3400
Wire Wire Line
	5950 3400 5950 3050
Connection ~ 5950 3050
Wire Wire Line
	5950 3050 6300 3050
Wire Wire Line
	4000 3350 4000 3700
Wire Wire Line
	4100 3350 4100 3400
Wire Wire Line
	4500 3350 4500 3700
Wire Wire Line
	4600 3350 4600 3400
Wire Wire Line
	4950 3350 4950 3700
Wire Wire Line
	5050 3350 5050 3400
$Comp
L Connector:Screw_Terminal_01x02 J1
U 1 1 618404EA
P 4000 3150
F 0 "J1" V 3964 2962 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 3873 2962 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 4000 3150 50  0001 C CNN
F 3 "~" H 4000 3150 50  0001 C CNN
	1    4000 3150
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J2
U 1 1 6184261F
P 4500 3150
F 0 "J2" V 4464 2962 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 4373 2962 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 4500 3150 50  0001 C CNN
F 3 "~" H 4500 3150 50  0001 C CNN
	1    4500 3150
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J3
U 1 1 61843096
P 4950 3150
F 0 "J3" V 4914 2962 50  0000 R CNN
F 1 "Screw_Terminal_01x02" V 4823 2962 50  0000 R CNN
F 2 "TerminalBlock:TerminalBlock_bornier-2_P5.08mm" H 4950 3150 50  0001 C CNN
F 3 "~" H 4950 3150 50  0001 C CNN
	1    4950 3150
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR01
U 1 1 6186983D
P 7000 3450
F 0 "#PWR01" H 7000 3200 50  0001 C CNN
F 1 "GND" H 7005 3277 50  0000 C CNN
F 2 "" H 7000 3450 50  0001 C CNN
F 3 "" H 7000 3450 50  0001 C CNN
	1    7000 3450
	1    0    0    -1  
$EndComp
Connection ~ 7000 3450
Wire Wire Line
	7000 3450 7000 4750
$EndSCHEMATC
