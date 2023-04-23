import React, { useState, useEffect } from 'react';
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import './App.css';

const ffmpeg = createFFmpeg({ log: true });

const App = () => {
  const [video, setVideo] = useState();
  const [ready, setReady] = useState(false);
  const [subclips, setSubclips] = useState([]);

  const load = async () => {
    await ffmpeg.load();
    setReady(true);
  };

  useEffect(() => {
    load();
  }, []);

  const processVideo = async () => {
    if (!video) {
      return;
    }

    // Write the input video to FFmpeg's memory
    ffmpeg.FS('writeFile', 'input.mp4', await fetchFile(video));

    // Process the video with FFmpeg functions
    await ffmpeg.run(
      '-y',
      '-ss',
      '0',
      '-i',
      'input.mp4',
      '-t',
      '10',
      '-vcodec',
      'copy',
      '-acodec',
      'copy',
      'output.mp4'
    );

    // Read the output video from FFmpeg's memory
    const data = ffmpeg.FS('readFile', 'output.mp4');

    // Create a URL for the output video
    const videoURL = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));

    // Generate a new clip name
    const newClipName = `Subclip ${subclips.length + 1}`;

    // Add the subclip information to the state
    setSubclips((prevSubclips) => [
      ...prevSubclips,
      {
        name: newClipName,
        size: (data.length / 1000000).toFixed(2),
        url: videoURL,
      },
    ]);
  };

  return (
    <div className="app">
      <h1>CS:GO Video Processor</h1>
      {ready ? (
        <>
          <input type="file" onChange={(e) => setVideo(e.target.files?.item(0))} />
          <button onClick={processVideo}>Process Video</button>
          {subclips.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Size</th>
                  <th>Download</th>
                </tr>
              </thead>
              <tbody>
                {subclips.map((subclip, index) => (
                  <tr key={index}>
                    <td>{subclip.name}</td>
                    <td>{subclip.size} MB</td>
                    <td>
                      <a href={subclip.url} download={`${subclip.name}.mp4`}>
                        Download
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      ) : (
        <p>Loading FFmpeg...</p>
      )}
    </div>
  );
};

export default App;