#!/bin/bash
./srcds_run -game csgo -console -tickrate 128 +game_type 0 +game_mode 1 +mapgroup mg_active +map de_dust2 +sv_setsteamaccount 0A946080584B114081FF040B7F82F60A -net_port_try 1 -nomaster +sv_occlude_players 1 +pvs_min_player_Distance 1 +sv_mincmdrate 128 +sv_minupdaterate 128

