#!/bin/bash
gcc my_p2p_api_test_linux.c my_p2p_ui_test_linux.c -lpthread -o my_p2p_ui
MY_MAC=$(ifconfig wlan5 | grep HWaddr | sed s/'.*HWaddr '//g)
TARGET_MAC=$1
WPS=$2
./my_p2p_ui wlan5 $MY_MAC $TARGET_MAC $WPS
