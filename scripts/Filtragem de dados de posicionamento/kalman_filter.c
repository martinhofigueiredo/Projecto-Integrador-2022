#include <stdio.h>
#include <time.h>
#include <stdlib.h>

float state_update_position(float zn, float xn_1, float alfa);
float noise(float x);

int main(){
    srand(time(NULL));
    float buf[100];
    float new_sample_x, new_sample_y, curr_estimate_posx, curr_estimate_posy;
    int i;
    int N = 0; //   N = Sample number
    float Kalman_Gain = 0.3;
    float posx = 0, posy = 0;
    FILE *f = fopen("pos.txt", "w");
    FILE *p = fopen("path.txt", "r");
    while(fscanf(p, "%f %f", &posx, &posy) != EOF){
        ///////////////////////////////////////////////////////////////////////////////////////////////////////////
        //  New sample
        new_sample_x = noise(posx);//randfloat(posx);
        
        //  For the first sample, the estimated position is the measured position
        if(N == 0)
            curr_estimate_posx = new_sample_x;

        //  Estimates current position using Kalman filter
        curr_estimate_posx = state_update_position(new_sample_x, curr_estimate_posx, Kalman_Gain);

        //  Same thing for y------------------------------------------------------------------------------------
        new_sample_y = noise(posy);//randfloat(posy);
        
        
        //  For the first sample, the estimated position is the measured position
        if(N == 0)
            curr_estimate_posy = new_sample_y;

        //  Estimates current position using Kalman filter
        curr_estimate_posy = state_update_position(new_sample_y, curr_estimate_posy, Kalman_Gain);
        /////////////////////////////////////////////////////////////////////////////////////////////////////////


        //  Update buffer (newest value in index 0)
        /*for(i = 100; i > 0; i--)
            buf[i] = buf[i-1];
        buf[0] = new_sample;*/

        printf("Sample: (%f,%f)\t\tEstimate: (%f,%f)\n", new_sample_x, new_sample_y, curr_estimate_posx, curr_estimate_posy);
        fprintf(f, "%f,%f,%f,%f\n",  new_sample_x, new_sample_y, curr_estimate_posx, curr_estimate_posy);

        N++;
    }
    fclose(p);
    fclose(f);
    return 0;
}

//  Takes float vector (samples) and number of samples so far
//                  xn_1 = xn,n-1 -> prediction from last iteration
//                  zn -> current sample
//                  N iteration
//                  alfa -> kalman gain
float state_update_position(float zn, float xn_1, float alfa){
    return xn_1 + (zn-xn_1)*alfa;
}

float noise(float x){
    int r = rand() % 2;

    return r == 1 ? x+0.2 : x-0.2;
}