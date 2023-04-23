import React, { useState, useEffect } from 'react';
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import { FFprobeWorker } from "ffprobe-wasm";
import './App.css';

const ffmpeg = createFFmpeg({ log: true });
const worker = new FFprobeWorker();

const App = () => {
  const [video, setVideo] = useState();
  const [videoCreationTimestamp, setVideoCreationTimestamp] = useState(null);
  const [jsonFile, setJsonFile] = useState();
  const [ready, setReady] = useState(false);
  const [subclips, setSubclips] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [responseData, setResponseData] = useState(null); // new state for response data

  const load = async () => {
    await ffmpeg.load();
    setReady(true);
  };

  useEffect(() => {
    load();
  }, []);

  const handleJsonFileChange = async (e) => {
    const file = e.target.files?.item(0);
    if (file) {
      setJsonFile(file);
      setProcessing(true);
      const response = await fetch('http://localhost:8081/v1/highlights', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_data: JSON.parse(await file.text()),
          user_preferences: {
            max_times: [10, 15, 20, 30],
            save_single_kills: true,
          },
        }),
      });

      if (response.ok) {
        const responseData = await response.json();
        setResponseData(responseData);
        setProcessing(false);
        console.log("responseData", responseData);
      }
    }
  };

  const getVideoCreationTimestamp = async (file) => {
    const fileInfo = await worker.getFileInfo(file);
    const creationTime = fileInfo.format.tags["creation_time"]
    const timestamp = Date.parse(creationTime);
    return timestamp;
  };

  const handleVideoFileChange = async (e) => {
    const file = e.target.files?.item(0);
    if (file) {
      setVideo(file);

      // Get and set the video creation date
      try {
        const creationTimestamp = await getVideoCreationTimestamp(file);
        if (creationTimestamp) {
          setVideoCreationTimestamp(creationTimestamp);
          console.log('Video creation date:', creationTimestamp);
        } else {
          console.error('Error getting video creation date');
        }
      } catch (error) {
        console.error('Error getting video metadata:', error);
      }
    }
  };

  const formatTime = (timeInMilliseconds) => {
    const date = new Date(timeInMilliseconds);
    return date.toISOString().slice(11, -1);
  };

  const processVideo = async () => {
    if (!video || !responseData) {
      return;
    }
    console.log("processing video", video);

    const CHUNK_SIZE = 2 * (1024 ** 3) - 1; // 2 GB
    const fileSize = video.size;
    const numChunks = Math.ceil(fileSize / CHUNK_SIZE);
    let minChunkIdx = 0;

    for (let clipIdx = 0; clipIdx < responseData.length; clipIdx++) {
      let clip = responseData[clipIdx];
      let success = false;

      // Calculate the start and end times of the clip (clip.start and clip.end are in milliseconds)
      const startTime = clip.start - videoCreationTimestamp - 5000;
      const endTime = clip.end - videoCreationTimestamp + 3000;
      const startTimeStr = formatTime(startTime);
      const durationStr = formatTime(endTime - startTime);


      for (let chunkIdx = minChunkIdx; chunkIdx < numChunks; chunkIdx++) {
        const chunkStart = chunkIdx * CHUNK_SIZE;
        const chunkEnd = Math.min((chunkIdx + 1) * CHUNK_SIZE, fileSize);
        console.log(`Processing clip ${clip.name} (${durationStr}) in chunk ${chunkIdx}...`);

        // Write the input video chunk to FFmpeg's memory
        ffmpeg.FS('writeFile', 'input.mp4', await fetchFile(video.slice(chunkStart, chunkEnd)));

        try {
          // Process the video with FFmpeg functions
          await ffmpeg.run(
            '-y',
            '-ss',
            startTimeStr,
            '-i',
            'input.mp4',
            '-t',
            durationStr,
            '-vcodec',
            'copy',
            '-acodec',
            'copy',
            'output.mp4'
          );

          // Read the output video from FFmpeg's memory
          const data = ffmpeg.FS('readFile', 'output.mp4');
          console.log('Read output video from memory');

          // Create a URL for the output video
          const videoURL = URL.createObjectURL(new Blob([data.buffer], { type: 'video/mp4' }));

          // Add the subclip information to the state
          setSubclips((prevSubclips) => [
            ...prevSubclips,
            {
              name: clip.name,
              size: (data.length / 1000000).toFixed(2),
              url: videoURL,
            },
          ]);

          success = true;
          minChunkIdx = chunkIdx;
          break;
        } catch (error) {
          console.error(`Failed to process clip ${clip.name} in chunk ${chunkIdx}. Trying next chunk.`);
        }
      }

      if (!success) {
        console.error(`Failed to process clip ${clip.name} in all chunks.`);
      }
    };
  };

  return (
    <div className="app">
      <h1>CS:GO Video Processor</h1>
      {ready ? (
        <>
          <input type="file" accept="application/json" onChange={handleJsonFileChange} />
          <input type="file" accept="video/*" onChange={handleVideoFileChange} />
          <button onClick={processVideo} disabled={processing || !responseData || !video}>Process Video</button> {/* disable the button if the processing status is true or if the response data is not available */}
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
