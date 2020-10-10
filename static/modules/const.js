"use strict";

export const name = "const";

// This value defines the duration the conditions to swap the displayed tables have to apply before it will be acted on.
// This value is only checked against every 100ms.
export const RCBOARD_CHECK_AND_HIDE_CHECK_INTERVAL = 2500;

// Duration for the tables to be swapped.
export const RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION = 30000;

// Should only round times or also distance to first driver be shown?
// true: switch display on the interval defined below
// false: always show round times
export const RCBOARD_LAPTIME_DELTA_CHANGE = false;

// Interval for changing display of laptime vs delta to first pilot.
// This is only relevant when the previous setting is true.
export const RCBOARD_LAPTIME_DELTA_CHANGE_INTERVAL = 10000;
