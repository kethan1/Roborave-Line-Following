#ifndef Encoder_HPP
#define Encoder_HPP
#include <stdint.h>
typedef void (*EncoderCB_t)(int);

class Encoder {
    int gpioA, gpioB, levA, levB, lastGpio, direction;
    volatile int steps;
    volatile uint32_t prevTicks;

    /* Need a static callback to link with C. */
    static void callback(int gpio, int level, uint32_t tick, void *user);

    /* This function releases the resources used by the decoder. */
    void cancelCallbacks(void);

    public:
        /*
            This function establishes a rotary encoder on gpioA and gpioB.
            When the encoder is turned the callback function is called.
        */
        Encoder(int aGpioA, int aGpioB);

        int getSteps();

        void resetSteps();

        int getDirection();

        ~Encoder();
};

void init();

#endif