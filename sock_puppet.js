const { Innertube } = require('youtubei.js');

(async () => {
    const youtube = await Innertube.create();

    // Random video from docs
    const firstVideoId = 'AYN8616Loc0';
  
    let videoId = firstVideoId;
    let watchNext;

    for (let i = 0; i < 5; i++) { // Loop 5 times for demonstration purposes
        console.log(`Watching video ID: ${videoId}`);

        // Get video information
        const videoInfo = await youtube.getInfo(videoId);
        // console.log(videoInfo);

        // Retrieve the transcript of the video
        try {
            const transcriptInfo = await videoInfo.getTranscript();
            // console.log('Raw Transcript Data:', JSON.stringify(transcriptInfo, null, 2)); // Log the raw transcript data
            // const transcriptLines = transcriptInfo.transcript.content.body.initial_segments.map(segment => segment.text);
            // console.log('Transcript:', transcriptLines.join('\n'));
            const transcriptLines = transcriptInfo.transcript.content.body.initial_segments.map(segment => segment.snippet.text);
            console.log('Transcript:', transcriptLines.join(' '));
        } catch (error) {
            console.log('Transcript not available for this video');
        }

        // Print out the title
        console.log(`Watching Video Title: ${videoInfo.basic_info.title}`);

        // Retrieve the next batch of suggested videos
        watchNext = await videoInfo.getWatchNextContinuation();

        // Filter out reel items
        const filteredContents = watchNext.watch_next_feed.filter(item => item.type === 'CompactVideo');

        // console.log(filteredContents);

        // Log the IDs and titles of the suggested videos
        filteredContents.forEach((video, index) => {
            console.log(`Suggested Video ${index + 1}: ${video.title.text} (ID: ${video.id})`);
        });

        // Choose the next video to watch from the suggested videos
        if (filteredContents.length > 0) {
            videoId = filteredContents[0].id;
        } else {
            console.log('No more suggested videos.');
            break;
        }
    }
})();
