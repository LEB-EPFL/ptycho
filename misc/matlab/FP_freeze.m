%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modified script from the following paper:
% Shaowei Jiang, Pengming Song, Tianbo Wang, et al.,
% "Spatial and Fourier domain ptychography for high-throughput bio-imaging", 
% Nature Protocols, 2023
% 
% This script is used to check whether FPDatasets from the leb.freeze
% Python library can be reconstructed with the FP algorithm from Jiang, et.
% al.
%
% Used function:
% FP_genZernike.m
%
% Copyright (c) 2023, Shaowei Jiang, Pengming Song, and Guoan Zheng, 
% University of Connecticut.
% Email: shaowei.jiang@uconn.edu or guoan.zheng@uconn.edu
% All rights reserved.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Simulate the forward imaging process of Fourier ptychography
close all
clear
clc
addpath(genpath(pwd))

%% Open a dataset exported from Mr. Freeze
results = open("hdr.mat");
imageAmpSeq = results.imageAmpSeq(:, :, 1:128);
kx = results.kx;
ky = results.ky;
% imNum = results.imNum;
imNum = 128;
clear results;

%% Definitions and parameters
F = @(x) fftshift(fft2(x));                                             % define Fourier transform
invF = @(x) ifft2(ifftshift(x));                                        % define inverse Fourier transform

waveLength = 0.473e-6;                                                  % the wavelength of LED
k0 = 2*pi/waveLength;                                                   % the wavenumber
spsize = 5.86e-6/10;                                                    % the sampling pixel size at the object plane
pratio = 3;                                                             % the up-sampling factor
NA = 0.288;  

%% Generate the low-pass filter (coherent transfer function) and the Zernike modes

[m, n] = size(imageAmpSeq(:,:,1));
% The image size of measurement
M = m * pratio;  N = n * pratio;
kmax = pi/spsize;
kxm0 = linspace(-kmax,kmax,m);
kym0 = linspace(-kmax,kmax,n);
[kxm,kym] = meshgrid(kxm0,kym0);
% The sampling pixel size in Fourier domain
dkx = 2*pi/(spsize*n); 
dky = 2*pi/(spsize*m);          
cutoff = NA * k0;
% Set up the lowpass filter in the Fourier domain without aberration
lowFilter = single((kxm.^2+kym.^2)<cutoff^2); 
% Azimuthal degree (the first column) and radial degree (the sceond column) for Zernike mode
ZernikeMN = [-2 2;0 2;2 2;-3 3;-1 3;1 3;3 3;-4 4;-2 4;0 4;2 4;4 4];                                  
% The number of Zernike modes used to express the pupil
modeNum = 6;                                            
ZernikeModes = zeros(m,n,modeNum);
% The weight vector for Zernike mode
w = [0.3, 0.5, 0.3, 0.6, 0.8, 0.3, 0.1, 0.2, 0.1, 0.3, 0.1, 0.3];     
zn = 0;
for i = 1:modeNum
    % Generating Zernike mode
    ZernikeModes(:,:,i) = FP_genZernike(max(m,n),2*max(cutoff/(2*kmax/m),cutoff/(2*kmax/n)),ZernikeMN(i,1),ZernikeMN(i,2));
    zn = zn + w(i).*ZernikeModes(:,:,i);
end

%% Set up numbers for access into the Fouriers transform of the complex object
kxl = round((M-m)/2)+1;
kxh = round((M+m)/2);
kyl = round((M-m)/2)+1;
kyh = round((M+m)/2);

%% Initialization of the object and the pupil
close all                                                
initialObj = mean(imageAmpSeq,3);                                       % average all the images
initialObj = imresize(initialObj, pratio); 		                        % object initialization
initialObjF = F(initialObj);                                            % the object's Fourier spectrum
initialPupil = lowFilter;                                               % pupil initialization    

%% The iterative recovery process for FP
objectRecoverF = initialObjF;               
pupilRecover = initialPupil;                
alphaO = 1;                                                             % the parameter of rPIE
alphaP = 1;                                                             % the parameter of rPIE
loopNum = 50;                                                           % the iteration number
% The algorithm used for updating the pupil
methodType = 'GD';                                                      % select 'GD' for calibration, select 'rPIE' for subsequent experiments 
w = zeros(modeNum,1);                                                   % the weight vector of Zernike modes; 'modeNum': the number of Zernike modes
for iLoop=1:loopNum
    for i=1:imNum
        disp(['Recovering loop ',num2str(iLoop),', ',num2str(i),'th image.']);

        % Crop a sub-region from the Fourier spectrum 
        kxi = round(kx(i)/dkx);              
        kyi = round(ky(i)/dky);  
        subObjF = objectRecoverF(kxl+kxi:kxh+kxi,kyl+kyi:kyh+kyi);
        
        % Low-pass filtered by the pupil and generate the low-resolution image  
        lowResFT = subObjF.*pupilRecover;  
        imlowRes = invF(lowResFT);
        
        % Replace the amplitude and keep the phase unchanged
        imlowRes = imageAmpSeq(:,:,i).*exp(1i.*angle(imlowRes));  
        
        % Use the rPIE algorithm to update the Fourier spectrum
        updatedLowResFT = F(imlowRes);
        updateSubObjF = subObjF + conj(pupilRecover)./...
            ((1-alphaO)*abs(pupilRecover).^2+alphaO*max(max(abs(pupilRecover).^2))).*(updatedLowResFT-lowResFT); 
        objectRecoverF(kxl+kxi:kxh+kxi,kyl+kyi:kyh+kyi) = updateSubObjF;
        
        switch methodType
            % Recover the pupil using gradient descent algorithm
            case 'GD' 
                lowResFT = (1/pratio)^2*updateSubObjF.*pupilRecover;  
                imlowRes = invF(lowResFT);
                imageDiff = 1./max(max((pratio)^2*imageAmpSeq(:,:,i))).*(1-(pratio)^2.*imageAmpSeq(:,:,i)./(abs(imlowRes))); 
                for modeIdx = 1:modeNum                         
                    gdTemp = invF(lowResFT.*pi.*ZernikeModes(:,:,modeIdx));
                    % The gradient with respect to each weight
                    gd = 2.*sum(sum(imageDiff.*imag(conj(imlowRes).*gdTemp)));
                    % Update each weight
                    w(modeIdx) = w(modeIdx) + 1*10^(-6).*gd;          
                end  
                tmpzfun = zeros(m, n);
                for modeIdx = 1:modeNum
                    % Update the weight sum of Zernike modes
                    tmpzfun = tmpzfun + w(modeIdx).*ZernikeModes(:,:,modeIdx);
                end
            
                % Update the pupil function
                pupilRecover = exp(1j.*pi.*tmpzfun).*lowFilter;
            % Recover the pupil using the rPIE algorithm
            case 'rPIE'   
                pupilRecover = pupilRecover + conj(updateSubObjF)./((1-alphaP)*abs(updateSubObjF).^2 + alphaP*max(max(abs(updateSubObjF).^2))).*(updatedLowResFT-lowResFT);
                pupilRecover = pupilRecover.*lowFilter;
        end
    end
    objRecover=invF(objectRecoverF);
    % Show the results
    if mod(iLoop,5) == 0
        figure(1);
        subplot(2,2,1); imshow(imageAmpSeq(:,:,1),[]); title('Low resolution measurement','FontSize',16)
        subplot(2,2,2); imshow(abs(objRecover),[]);title('Recovered amplitude','FontSize',16);
        subplot(2,2,3); imshow(angle(objRecover),[]);title('Recovered phase','FontSize',16);
        subplot(2,2,4); imshow(angle(pupilRecover),[]);title('Recovered pupil','FontSize',16);
        pause(0.2)
    end
end
