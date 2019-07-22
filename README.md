# Chatty
### An AI Chatbot built in Python

* Work is in progress

Chatty is an AI powered conversational dialog interface built in Python.The smooth UI makes it effortless to create and train conversations to the bot and it continuously gets smarter as it learns from conversations it has with people. Chatty can live on any channel of your choice (such as Messenger, Slack etc.) by integrating it’s API with that platform.

You don’t need to be an expert at artificial intelligence to create an awesome chatbot that has artificial intelligence. With this basic project you can create an artificial intelligence powered chatting machine in no time.There may be scores of bugs. So feel free to contribute  via pull requests.

### Installation without docker

#### backend

* Setup Virtualenv and install python requirements
```sh
make setup

make run_dev

source venv/bin/activate && python manage.py init
```
* Production
```sh
make run_prod
```

#### frontend
* Development
```sh
cd frontend
npm install
ng serve
```
* Production
```sh
cd frontend
ng build --prod --environment=python
```
serve files in dist/ folder using nginx or any webserver

### DB

#### Restore
You can import some default intents using follwing steps

- goto http://localhost:8080/agent/default/settings
- click 'choose file'
- choose 'examples/default_intents.json file'
- click import

### Screenshots
![](https://i.ibb.co/W2jVLkB/Screenshot-from-2019-07-13-15-10-41.png)
![](https://i.ibb.co/K2MXvtb/Screenshot-from-2019-07-13-15-10-32.png)
![](https://i.ibb.co/K2MXvtb/Screenshot-from-2019-07-13-15-10-32.png)

### Todos
 *  Wire seats ui with mongo
 *  Write Unit Tests
 *  NLTK to Spacy migration
 *  PyCRFSuite to sklearn-crfsuite migration
 *  Support follow up conversations
 
 ### Dependencies documentations
* [NLTK documentation](www.nltk.org/)
* [SKLearn documentation](http://scikit-learn.org/)
* [CRFsuite documentation](http://www.chokkan.org/software/crfsuite/)
* [python CRfSuite](https://python-crfsuite.readthedocs.io/en/latest/)

**Free Software, Hell Yeah!**
<hr></hr>

_Made with :heart:
