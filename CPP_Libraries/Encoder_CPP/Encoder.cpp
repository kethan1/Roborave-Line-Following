#include "Encoder.hpp"
#include <iostream>
#include <pigpio.h>

void init() {
    gpioInitialise();
    int cfg = gpioCfgGetInternals();
    cfg |= PI_CFG_NOSIGHANDLER;
    gpioCfgSetInternals(cfg);
}

void Encoder::callback(int gpio, int level, uint32_t tick, void *user) {
    /*
        Need a static callback to link with C.
    */

    Encoder *self = (Encoder *) user;

    if (gpio == self->gpioA) self->levA = level; else self->levB = level;

    if (gpio != self->lastGpio) { /* debounce */
        self->lastGpio = gpio;

        if ((gpio == self->gpioA) && (level == 1)) {
            if (self->levB) {
                self->steps++;
                self->direction = 0;
            }
        }
        else if ((gpio == self->gpioB) && (level == 1)) {
            if (self->levA) { 
                self->steps--;
                self->direction = 1;
            }
        }
    }
}


Encoder::Encoder(int aGpioA, int aGpioB) {
    gpioA = aGpioA;
    gpioB = aGpioB;
    direction = 0;

    levA = 0;
    levB = 0;

    steps = 0;
    lastGpio = -1;
    prevTicks = 0;

    gpioSetMode(gpioA, PI_INPUT);
    gpioSetMode(gpioB, PI_INPUT);

    /* pull up is needed as encoder common is grounded */

    gpioSetPullUpDown(aGpioA, PI_PUD_UP);
    gpioSetPullUpDown(aGpioB, PI_PUD_UP);

    /* monitor encoder level changes */

    gpioSetAlertFuncEx(aGpioA, callback, this);
    gpioSetAlertFuncEx(aGpioB, callback, this);
}

void Encoder::cancelCallbacks(void) {
    gpioSetAlertFuncEx(gpioA, NULL, this);
    gpioSetAlertFuncEx(gpioB, NULL, this);
}

Encoder::~Encoder() {
    cancelCallbacks();
    gpioTerminate();
}

int Encoder::getSteps() {
    return steps;
}

int Encoder::getDirection() {
    return direction;
}

void Encoder::resetSteps() {
    steps = 0;
}
