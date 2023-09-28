function zernikfunc = FP_genZernike(tpixel, NApixel, m, n)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Citation: Shaowei Jiang, Pengming Song, Tianbo Wang, et al.,
% "Spatial and Fourier domain ptychography for high-throughput bio-imaging", 
% submitted to Nature Protocols, 2023
% 
% Zernike modes generation function for Fourier-domain ptychography (FP). 
%
% Inputs:
% tpixel        The size of the image
% NApixel       The diameter of NA
% m             Azimuthal degree
% n             radial degree 
%
% Outputs:
% zernikfunc    The Zernike mode
%
% Copyright (c) 2023, Shaowei Jiang, Pengming Song, and Guoan Zheng, 
% University of Connecticut.
% Email: shaowei.jiang@uconn.edu or guoan.zheng@uconn.edu
% All rights reserved.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    x=linspace(-tpixel/NApixel,tpixel/NApixel,tpixel);
    [X,Y] = meshgrid(x,x);
    [theta,r] = cart2pol(X,Y);
    idx = r<=1;
    zernikfunc = zeros(size(X));
    zernikfunc(idx) = zernfun(n,m,r(idx),theta(idx));
end

