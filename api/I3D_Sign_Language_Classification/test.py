from gradio_client import Client

client = Client("https://8df87406180e21cda4.gradio.live/")
result = client.predict(
		"https://github.com/gradio-app/gradio/raw/main/test/test_files/video_sample.mp4",	# str (filepath on your computer (or URL) of file) in 'Video (*.mp4)' Video component
		"WLASL100",	# str  in 'Trained on:' Radio component
		api_name="/predict"
)
print(result)