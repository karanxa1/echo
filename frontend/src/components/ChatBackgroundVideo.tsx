import { useEffect, useRef, useState } from 'react';

const ChatBackgroundVideo = () => {
  const desktopVideoRef = useRef<HTMLVideoElement>(null);
  const mobileVideoRef = useRef<HTMLVideoElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const videos = [desktopVideoRef.current, mobileVideoRef.current];
    
    const handleVideoEvents = () => {
      videos.forEach(video => {
        if (!video) return;

        // Seamless loop handling
        const handleTimeUpdate = () => {
          if (video.duration - video.currentTime < 0.1) {
            video.currentTime = 0;
          }
        };

        const handleEnded = () => {
          video.currentTime = 0;
          video.play().catch(console.error);
        };

        const handleCanPlay = () => {
          setIsLoaded(true);
          video.play().catch(console.error);
        };

        // Add event listeners
        video.addEventListener('timeupdate', handleTimeUpdate);
        video.addEventListener('ended', handleEnded);
        video.addEventListener('canplay', handleCanPlay);

        // Cleanup function
        return () => {
          video.removeEventListener('timeupdate', handleTimeUpdate);
          video.removeEventListener('ended', handleEnded);
          video.removeEventListener('canplay', handleCanPlay);
        };
      });
    };

    handleVideoEvents();
  }, []);

  return (
    <>
      {/* Desktop Video */}
      <video
        ref={desktopVideoRef}
        className="hidden md:block fixed inset-0 w-full h-full object-cover"
        style={{ zIndex: -1 }}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
      >
        <source
          src="https://storage.googleapis.com/pinhole-about-assets-prod-asia/RNDR_TunnelVidoes_stretched_005_1440x1080.mp4"
          type="video/mp4"
        />
      </video>

      {/* Mobile Video */}
      <video
        ref={mobileVideoRef}
        className="block md:hidden fixed inset-0 w-full h-full object-cover"
        style={{ zIndex: -1 }}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
      >
        <source
          src="https://storage.googleapis.com/pinhole-about-assets-prod-asia/RNDR_TunnelVidoes_stretched_005_420x1118.mp4"
          type="video/mp4"
        />
      </video>

      {/* Loading overlay */}
      {!isLoaded && (
        <div className="fixed inset-0 bg-black flex items-center justify-center" style={{ zIndex: -1 }}>
          <div className="text-white text-center">
            <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p>Loading...</p>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatBackgroundVideo; 