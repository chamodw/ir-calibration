/*
 * sensor.c
 *
 * Created: 19/06/2020 3:46:17 PM
 *  Author: csam754
 */ 


#include "sensor.h"
#include "Sensirion/sensirion_sensors.h"
#include "sam.h"
#include "Color/color.h"
#include "UV/si1133.h"

#include <string.h>
#include "ir_constants.h"

Kiw_DataPacket* g_packet;


#ifndef KIW_SENSOR_TYPE
#error "Sensor type not defined"
#endif

uint8_t sensor_initPacket(Kiw_DataPacket* packet)
{
	g_packet = packet;
	g_packet->type = (K_PKT_TYPE_DATA << 8) | (KIW_SENSOR_TYPE );
	g_packet->header = 0x0A0A;
	g_packet->footer = 0x0B0B;
	g_packet->seq = 0;
	
	return K_SENSOR_OK;
}

uint8_t sensor_init()
{
	uint8_t e = K_SENSOR_STATUS_UNKNOWN;
	
#if KIW_SENSOR_TYPE == SENSOR_TYPE_CONDUCTIVTIY
	e = cdt_init();
#elif  KIW_SENSOR_TYPE == SENSOR_TYPE_HUMIDITY
	e = humidity_init();
#elif  KIW_SENSOR_TYPE == SENSOR_TYPE_VOC
#if K_VOC_TYPE == 0
	e = tvoc_init();
#else
	//e = ags02ma_init();
#endif

#elif KIW_SENSOR_TYPE == SENSOR_TYPE_COLOUR
	e = veml_init();
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_UV_LIGHT
	e = Si1133_init();
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_BODY_TEMP
	e = mrt311_init();
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_TEMP_CALIB
	e = mrt311_init();
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_HEART_RATE
	e = ppg_init();
#endif

	return e;
	
	
}



// Returns the sensor name (For USB Descriptors)
const char* sensor_name()
{
	
#if KIW_SENSOR_TYPE == SENSOR_TYPE_CONDUCTIVTIY
		const char* s =  "Kiwrious Conductance Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_HUMIDITY
		const char* s =  "Kiwrious Humidity Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_VOC
		const char* s =  "Kiwrious VOC Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_COLOUR
		const char* s =  "Kiwrious Colour Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_UV_LIGHT
		const char* s =  "Kiwrious UV Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_BODY_TEMP
		const char* s =  "Kiwrious Temperature Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_TEMP_CALIB
		const char* s =  "Kiwrious Temperature Sensor";
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_HEART_RATE
		const char* s =  "Kiwrious Heart Rate Sensor";
#else
		const char* s = "Kiwrious Sensor";
#endif

	return s;
}


//Reads the sensor and copies the data to dest buffer, returns number of values written
uint16_t sensor_read(int16_t* dest)
{
	
	
#if KIW_SENSOR_TYPE == SENSOR_TYPE_CONDUCTIVTIY
	int16_t val=0, range=0;
	int8_t e = cdt_readAuto(&val, &range, &dest[2]);
	if (e == K_SENSOR_OK)
	{
		dest[0] = val;		
		dest[1] = range;
		return 2;
	}
	return 0;
	
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_HUMIDITY
	
	int32_t h=0, t=0;
	int8_t e = humidity_measure(&t, &h); //returns tmp*1000 and humidity*1000
	if(e == K_SENSOR_OK)
	{
		dest[0] = t/10; //Temperature in C *100
		dest[1] = h/10; // RH % *100
		return 2;
	}
	return 0;
	
	
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_VOC

	uint16_t tvoc_ppb, co2_eq_ppm = 0;
	int8_t e;
#if K_VOC_TYPE == 0
	 e =  tvoc_measure(&tvoc_ppb, &co2_eq_ppm);
#elif K_VOC_TYPE == 1
	e = ags02ma_measure (&tvoc_ppb);
#endif
	if(e == K_SENSOR_OK)
	{
		dest[0] = tvoc_ppb; // tVOC in ppb
		dest[1] = co2_eq_ppm; // CO2(eq) in ppm
		return 2;
	}
	return 0;
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_COLOUR
	
	int8_t e = veml_singleShot(0, 1, (uint16_t*) dest);
	if (e == K_SENSOR_OK)
		return 4;
	else
		return 0;
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_UV_LIGHT
	float res[2]; //lux, uv
	int8_t e = measure_lux_uv(&res[0], &res[1]);
//	if (e == K_SENSOR_OK)
	{
			
		memcpy(dest, res, sizeof(float)*2);

		return 8;
	}
	//else
		//return 0;

#elif KIW_SENSOR_TYPE == SENSOR_TYPE_BODY_TEMP

	int16_t object, sensor, object_raw, sensor_raw;
	int8_t e = mrt311_read(&object, &sensor, &object_raw, &sensor_raw);


	dest[0] = (int16_t)object;
	dest[1] = (int16_t) sensor;
	dest[2] = object_raw;
	dest[3] = sensor_raw;
	return 8;
#elif KIW_SENSOR_TYPE == SENSOR_TYPE_TEMP_CALIB
		int16_t object, sensor, object_raw, sensor_raw;
		int8_t e = mrt311_read(&object, &sensor, &object_raw, &sensor_raw);
		
		float constants[3] = {
			IR_CALIB_A,
			IR_CALIB_B,
			IR_CALIB_C };
			
		dest[0] = (int16_t)sensor;
		dest[1] = (int16_t) object_raw;
		
		memcpy((void*)&dest[2], (void*)constants, sizeof(constants));
		
	return 8;
#else	
	return 0; //No bytes written
#endif
}
