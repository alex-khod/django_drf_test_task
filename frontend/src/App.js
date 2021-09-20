import React, { Component, useState } from "react";

function getCookie(key){
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    if (cookies.length > 0)
      {
        cookies = cookies.map((x) => {return x.split('=')});
        cookies = cookies.find((x) => {return x[0]===key});
        if (cookies !== undefined) return cookies[1];
      }
  }
}

function getId(question, idx) {
  return question.id + 'response' + idx;
}

// these should be their own components...
function SingleAnswer(props) {
  const response = props.responses[0];
  const question = props.question;

  function handleOnChange(e) {
    const userResponse = e.target.value;
    props.handleOnChange(userResponse);
    // props.handleSubmit(e);
  }

  return question.answers_display.map((answer, idx) => {
        return (
          <li key={idx} className="answer">
          <label htmlFor={getId(question, idx)}>
            <input type="radio" name="text" id={getId(question, idx)}
              value={idx}
              onChange={handleOnChange}
              defaultChecked={response===idx ? true : false} />
            {answer}
            </label>
          </li>
        )
  })
}

function MultipleAnswer (props) {
  const question = props.question;
  const responses = props.responses;
  const initialState = question.answers_display.map((a, idx) => { return responses.indexOf(idx) > -1});
  const [multiChecked] = useState(initialState);

  function getValues(){
    var values = question.answers_display.map((a, idx) => idx);
    values = values.filter((a, idx) => {return multiChecked[idx]});
    return values
  }

  props.handleOnChange(getValues())

  function handleOnChange (e) {
    const idx = e.target.value;
    multiChecked[idx] = !multiChecked[idx];
    props.handleOnChange(getValues());
  }

  return question.answers_display.map((answer, idx) => {
        return (
          <li key={idx} className="answer">
          <label htmlFor={getId(question, idx)}>
            <input type="checkbox" name="text"
              id={getId(question, idx)}
              value={idx}
              onChange={ handleOnChange }
              defaultChecked={responses.indexOf(idx) > -1 ? true : false}
                />
            {answer}
            </label>
          </li>
        )
  });
}

function TextAnswer(props) {
  const response = props.responses[0] === undefined ? '' : props.responses[0];
  var [textAnswer, setText] = useState(response);
  const question = props.question;
  return (
    <li className="answer">
      <span>Your answer: </span>
      <input type="text"
            name="text"
            id={question.id}
            value={textAnswer}
            onChange={(e) => { setText(e.target.value); props.handleOnChange([e.target.value]); }}
            />
    </li>
  )
}

function Question(props) {
  const csrftoken = getCookie('csrftoken');


  var [newResponse] = useState([]);

  function handleOnChange(value){
    newResponse = value;
  }

  const question = props.question;

  var responsesArr = [];
  if (question.responses.length > 0){
    try{
        responsesArr = JSON.parse(question.responses[0].text);
    } catch (c) {
      console.error(c);
    }
  }

  function handleSubmit(e) {
    if (e.type === 'submit') e.preventDefault();

    const params = JSON.stringify(
      {'question' : question.id,
        'text' : newResponse });

    console.log(newResponse);
    console.log(params);

    fetch('/api/responses/', {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken' : csrftoken,
        },
        method: 'POST',
        body: params,
    }).then((res) => {
        console.log(res);
        return res.json();
      }
    ).then((json) =>
      {
        console.log(json);
      }
    )
  }

  // probably better than fetching from request.

  const shared = {
    'question' : question,
    'responses' : responsesArr,
    'handleSubmit' : handleSubmit,
    'handleOnChange' : handleOnChange,
  }
  const renderTypes =
    {
        "SA" : () => {return <SingleAnswer {...shared} />},
        "MA" : () => {return <MultipleAnswer {...shared} />},
        "TA" : () => {return <TextAnswer {...shared} />},
    }

  return (
    <form action="/api/poll_responses"
    onSubmit={(e) => {handleSubmit(e)}}
    >
    {renderTypes[question.type]()}
    <button type='submit'>Send </button>
    </form>
  )
}

function Poll(props) {

  if (!(props.questions.length > 0)) return null;
  return props.questions.map((question) => {
      return (
        <div key={question.id} className="question">
            <strong>Question: {question.text} Type: {question.type_display}</strong>
            <ul>
            <Question question={question} />
            </ul>
        </div>
      )
    })
}

function Polls(props) {
  return props.polls.map((poll) => {
      return (
        <div key={poll.id} className="poll">
            <h2>Poll: {poll.title}</h2>
            <p>Start: {poll.start_at}</p>
            <p>Expires: {poll.expire_at}</p>
            <p>Description: {poll.description}</p>
            <Poll questions={poll.questions} />
        </div>
      )
    })
}

class App extends Component {
  constructor(props) {
    super(props);
    this.urls = {
      'all' : '/api/polls/',
      'me' : '/api/polls/me/'
    }
    this.state = {
      page : 1,
      fetchUrl : this.urls['all'],
      pollRequest: null,
      polls: [],
    };
    this.handleClick = this.handleClick.bind(this);
  }

  async fetchData() {
      try {
        const response = await fetch(this.state.fetchUrl);
        const polls = await response.json();
        this.setState({
          pollRequest : polls,
          polls : polls.results
        });
      } catch (e) {
        console.log(e);
    }
  }

    async componentDidMount() {
      this.fetchData();
    }

    handleClick(e) {
      this.setState({fetchUrl : this.urls[e.target.id]},
        () => {this.fetchData()});
    }

    render() {
      return (
        <main className="content">
            <h1>Polls</h1>
            <button id="all" onClick={this.handleClick}>All polls</button>
            <button id="me" onClick={this.handleClick}>My participation</button>
            {this.state.polls.length > 0 &&
              <Polls key={0} polls={this.state.polls} />
            }
        </main>
      )
    }
  }

export default App;
