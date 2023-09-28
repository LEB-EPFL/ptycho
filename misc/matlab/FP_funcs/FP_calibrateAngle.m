function [kx, ky, NAt]= FP_calibrateAngle(ledPositions,xint,yint,total,n)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Citation: Shaowei Jiang, Pengming Song, Tianbo Wang, et al.,
% "Spatial and Fourier domain ptychography for high-throughput bio-imaging", 
% submitted to Nature Protocols, 2023
% 
% incident angle calibration function for Fourier-domain ptychography (FP). 
%
% Inputs:
% ledPositions      The positions of LEDs
% (xint, yint)      Offset of initial LED to the patch center
% total             The number of LEDs
% n                 The refractive index
%
% Outputs:
% (kx,ky)           The normalized wavevectors of the illumination
% NAt               The illumination NAs of LEDs
%
% Copyright (c) 2023, Shaowei Jiang, Pengming Song, and Guoan Zheng, 
% University of Connecticut.
% Email: shaowei.jiang@uconn.edu or guoan.zheng@uconn.edu
% All rights reserved.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
kx=zeros(1,total);ky=kx;NAt=kx;
for tt=1:total

    xl=xint+ledPositions(tt,1);
    yl=yint+ledPositions(tt,2);
    l=sqrt(xl^2+yl^2);                                      % distance between the LED and the center LED 
    thetal=atan2(yl,xl);                                    % angle of LED in x-y plane

    xoff = 0;                                               % initial gues where beam enters bottom of slide
    thetag = -asin(l/sqrt(l^2+ledPositions(tt,3)^2)/n);     % get angle of beam in glass from Snell's law
    xin = tan(thetag);                                     % find where the beam exits the top of the slide
    xoff = xoff-xin;                                       % modify guess where beam enters bottom of slide by this amount

    % repeat the above produre until the beam exits the top of the slide
    % within 1 micron of center
    while abs(xin) > 0.001
        thetag = -asin((l-xoff)/sqrt((l-xoff)^2+ledPositions(tt,3)^2)/n);
        xin = xoff + tan(thetag);
        xoff = xoff - xin;
    end
      
    theta = asin((l-xoff)/sqrt((l-xoff)^2+ledPositions(tt,3)^2));

    NAt(1,tt)=abs(sin(theta));
    kx(1,tt)=-NAt(1,tt)*cos(thetal);
    ky(1,tt)=-NAt(1,tt)*sin(thetal);
   
end
end
