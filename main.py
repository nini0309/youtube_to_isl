import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from flask import Flask,request,render_template,send_from_directory,jsonify, flash

app =Flask(__name__,static_folder='static', static_url_path='')
app.secret_key = "VatsalParsaniya"

import nlp

@app.route('/home',methods=['GET'])
def home():
	return render_template('homepage.html')

@app.route('/',methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/youtube',methods=['GET'])
def youtube():
	return render_template('youtube.html')

@app.route('/learn',methods=['GET'])
def learn():
	return render_template('learn.html')

@app.route('/audio_to_text',methods=['GET'])
def audio_to_text():
	return render_template('audio.html')

@app.route('/',methods=['GET','POST'])
def flask_test():
	text = request.form.get('text') #gets the text data from input field of front end
	print("text is", text)
	if(text==""):
		return "";
	output = nlp.translate(text)

	final_words_dict = {}

	# fills the json 
	for words in output:
		for i,word in enumerate(words,start=1):
			final_words_dict[i]=word;

	print("---------------Final words dict--------------");
	print(final_words_dict)

	return final_words_dict;

@app.route('/audio_to_text',methods=['GET','POST'])
def audio_test():
	text = request.form.get('text') #gets the text data from input field of front end
	print("text is", text)
	if(text==""):
		return ""
	output = nlp.translate(text)

	final_words_dict = {}

	# fills the json 
	for words in output:
		for i,word in enumerate(words,start=1):
			final_words_dict[i]=word;

	print("---------------Final words dict--------------");
	print(final_words_dict)

	return final_words_dict;

	
import youtube
@app.route('/youtube',methods=['GET','POST'])
def youtube_test():
	text = request.form.get('text') #gets the text data from input field of front end
	print("url is", text)
	if(text==""):
		return ""
	youtube_to_text = youtube.get_text(text)
	output = nlp.translate(youtube_to_text)

	final_words_dict = {}

	# fills the json 
	for words in output:
		for i,word in enumerate(words,start=1):
			final_words_dict[i]=word


	print("---------------Final words dict--------------");
	print(final_words_dict)

	return final_words_dict;


# serve sigml files for animation
@app.route('/static/<path:path>')
def serve_signfiles(path):
	print("here");
	return send_from_directory('static',path)


if __name__=="__main__":
	app.run(debug=True)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'