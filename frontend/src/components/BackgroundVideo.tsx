import { useEffect, useRef, useState } from 'react';

const BackgroundVideo = () => {
  const desktopVideoRef = useRef<HTMLVideoElement>(null);
  const mobileVideoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const setupSeamlessVideo = (video: HTMLVideoElement | null) => {
      if (!video) return;

      // Set up video for seamless looping
      video.muted = true;
      video.autoplay = true;
      video.loop = true;
      video.playsInline = true;
      video.preload = 'auto';

      const handleLoadedData = () => {
        video.play().catch((error) => {
          console.log('Video autoplay prevented:', error);
          // Try to play again after user interaction
          const playOnInteraction = () => {
            video.play().catch(console.error);
            document.removeEventListener('click', playOnInteraction);
            document.removeEventListener('touchstart', playOnInteraction);
          };
          document.addEventListener('click', playOnInteraction);
          document.addEventListener('touchstart', playOnInteraction);
        });
      };

      const handleTimeUpdate = () => {
        // Ensure seamless loop by resetting when near the end
        if (video.duration - video.currentTime < 0.1) {
          video.currentTime = 0;
        }
      };

      const handleEnded = () => {
        // Force restart if the loop fails
        video.currentTime = 0;
        video.play().catch(console.error);
      };

      // Add event listeners
      video.addEventListener('loadeddata', handleLoadedData);
      video.addEventListener('timeupdate', handleTimeUpdate);
      video.addEventListener('ended', handleEnded);

      // Start loading the video
      video.load();

      // Cleanup function
      return () => {
        video.removeEventListener('loadeddata', handleLoadedData);
        video.removeEventListener('timeupdate', handleTimeUpdate);
        video.removeEventListener('ended', handleEnded);
      };
    };

    // Setup both videos
    const desktopCleanup = setupSeamlessVideo(desktopVideoRef.current);
    const mobileCleanup = setupSeamlessVideo(mobileVideoRef.current);

    return () => {
      desktopCleanup?.();
      mobileCleanup?.();
    };
  }, []);

  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden bg-black">
      {/* Desktop video */}
      <video
        ref={desktopVideoRef}
        className="absolute inset-0 w-full h-full object-cover hidden md:block video-container"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        style={{
          objectFit: 'cover',
          width: '100%',
          height: '100%',
          objectPosition: 'center',
        }}
      >
        <source
          src="https://storage.googleapis.com/pinhole-about-assets-prod-asia/RNDR_TunnelVidoes_stretched_005_1440x1080.mp4"
          type="video/mp4"
        />
        Your browser does not support the video tag.
      </video>
      
      {/* Mobile video */}
      <video
        ref={mobileVideoRef}
        className="absolute inset-0 w-full h-full object-cover md:hidden video-container"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        style={{
          objectFit: 'cover',
          width: '100%',
          height: '100%',
          objectPosition: 'center',
        }}
      >
        <source
          src="https://storage.googleapis.com/pinhole-about-assets-prod-asia/RNDR_TunnelVidoes_stretched_005_420x1118.mp4"
          type="video/mp4"
        />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default BackgroundVideo; 