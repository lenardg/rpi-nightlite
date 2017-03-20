# Nightlite for Raspberry Pi with a Blinkt!

try:
	import blinkt
except ImportError:
	exit("Make sure the Blinkt! library has been installed!")

from colorsys import hsv_to_rgb
from enum import Enum
import time

DEBUG = False 
BRIGHTNESS = 0.5
BRIGHTNESS_NITE = 0.2
BRIGHTNESS_CLOCK = 0.1

class state(Enum):
	day = 1
	nearsleep = 2
	sleep = 3
	night = 4
	nearmorning = 5
	morning = 6

currentState = state.day

def init():
	blinkt.clear()
	blinkt.set_brightness ( BRIGHTNESS )

def color(h,s=1.0,v=1.0):
	return tuple([int(c*255) for c in hsv_to_rgb(h/360.0, s, v)])

def shift(hfrom,hto,duration,v=1.0):
	if hto < hfrom:
		step = -1
	else:
		step = 1
	blinkt.set_brightness(BRIGHTNESS)
	for i in range(hfrom,hto,step):
		r,g,b = color(i, v=v)
		if DEBUG:
			print("#{0}: r:{1} g:{2} b:{3}".format(i,r,g,b))
		blinkt.set_all(r,g,b)
		blinkt.show()
		time.sleep( duration / abs(hfrom-hto) )

def fadeout(hue,duration,v=1.0):
	for i in range(100,0,-1):
		r,g,b = color(hue,v=v)
		if DEBUG:
			print(BRIGHTNESS * (i / 100.0))
		blinkt.set_all(r,g,b,BRIGHTNESS * (i / 100.0))
		blinkt.show()
		time.sleep( duration / 100)
	blinkt.clear()
	blinkt.show()

def fadein(hue,duration,v=1.0):
	for i in range(0,100):
		r,g,b = color(hue,v=v)
		if DEBUG:
			print(BRIGHTNESS * (i / 100.0))
		blinkt.set_all(r,g,b,BRIGHTNESS * (i / 100.0))
		blinkt.show()
		time.sleep( duration / 100)

def sethue(hue,v=1.0):
	r,g,b = color(hue,v=v)
	blinkt.set_all(r,g,b)
	blinkt.show()

def setbrightness(b):
	blinkt.set_brightness(b)
	blinkt.show()

def showclock(hour, minute):
	if hour >= 12:
		hourcolor = (255,0,0)
	else:
		hourcolor = (255,192,0)

	h = "{0:04b}".format(hour%12)
	index = 0
	r, g, b = hourcolor
	for c in h:
		if c == '0':
			blinkt.set_pixel(index, 0, 0, 0)
		else:
			blinkt.set_pixel(index, r, g, b, BRIGHTNESS_CLOCK)
		index = index + 1
	
	m = "{0:04b}".format(int(minute / 5))
	for c in m:
		if c == '0':
			blinkt.set_pixel(index, 0, 0, 0)
		else:
			blinkt.set_pixel(index, 200, 0, 255, BRIGHTNESS_CLOCK)
		index = index + 1

	blinkt.show() 

def processMinute(hour,minute):
	global currentState
	if currentState == state.day:
		if hour > 19 or (hour == 19 and minute >= 30):
			currentState = state.nearsleep
			fadein(330,10)
	#	else:
	#		showclock(hour, minute);
	elif currentState == state.nearsleep:
		if hour == 20 and minute < 15:
			pass
		elif hour == 20 and minute >= 15 and minute < 37:
			sethue(330 + (minute-15)*2, v=1.0-((minute - 15)/44.0) )
		elif hour > 20 or (hour == 20 and minute >= 37):
			sethue(15,v=0.5)
			currentState = state.sleep
	elif currentState == state.sleep:
		if hour == 22 and minute < 30:
			setbrightness( BRIGHTNESS - (BRIGHTNESS - BRIGHTNESS_NITE) * (minute / 30.0) )
		elif hour >= 22 or hour < 6:
			setbrightness( BRIGHTNESS_NITE )
			currentState = state.night
	elif currentState == state.night:
		if hour == 6 and minute >= 50:
			setbrightness( BRIGHTNESS_NITE + (BRIGHTNESS - BRIGHTNESS_NITE) * ((minute - 50) / 10))
		elif hour == 7:
			setbrightness( BRIGHTNESS )
			shift(15,100,30)
			currentState = state.morning
	elif currentState == state.morning:
		if hour == 8:
			fadeout(100,10)
			currentState = state.day

def main():
	init()
	for hour in range(18,33):
		realhour = hour%24
		print("{0:2}: ".format(realhour),end='')
		for minute in range(0,60):
			print('.', end='', flush=True)
			if realhour < 6:
				time.sleep(0.02)
			else:
				time.sleep(0.15)
			processMinute(realhour,minute)
		print("]")

if __name__ == '__main__':
	main()
