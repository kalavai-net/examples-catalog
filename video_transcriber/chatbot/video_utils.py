import yt_dlp

def list_formats(video_url):
    ydl_opts = {
        "listformats": True, # Lists all available formats
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=False)

def download_youtube_video(video_url, format_code=None, download_audio_only=False, download_video_only=False):
    ydl_opts = {}
    if format_code is not None:
        ydl_opts["format"] = format_code  # Uses specified format
    
    if download_audio_only:
        ydl_opts["format"] = "bestaudio"
    elif download_video_only:
        ydl_opts["format"] = "worstvideo"
    else:
        ydl_opts["format"] = "bestvideo+bestaudio"
    
    print("Download quality: ", ydl_opts)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    # Get the filename of the downloaded file
    info_dict = ydl.extract_info(video_url, download=False)
    filename = ydl.prepare_filename(info_dict)
    
    return filename


if __name__ == "__main__":
    try:
        # Request video URL from user
        video_url = input("Please enter the full URL of the YouTube video: ")
        print(
            list_formats(video_url)
        )
        print(
            download_youtube_video(video_url, download_video_only=True)
        )
        print("Download completed successfully.")
    except ValueError as e:
        print(e)