function addQuestion() {
  let oporni_element;
  let number_for_span;
  let id;
  if (Object.keys(obj).length == 0) {
    obj['1'] = [1, 2];
    id = 1;
    number_for_span = 1;

  } else {
    id = +Object.keys(obj)[Object.keys(obj).length - 1];
    id += 1;
    obj[id] = [1, 2];
    number_for_span = Object.keys(obj).length;
  }



  oporni_element = document.querySelector('.questions');

  oporni_element.insertAdjacentHTML("beforeend", `
    <div>
      <span class="number" id="number-${id}">${number_for_span}.</span>
      <input class="question" id="question-${id}" value="${id}">
      <label for="addimage-${id}" id="label-${id}">Выберите файл</label>
      <input type="file" id="addimage-${id}" class="addimage" accept="image/*">
      <button class="delquestion" id="delquestion-${id}"><img src='/static/test_creation/trashbin.png'"></button>
      <input class="max_score" id="max_score-${id}" value="1">
      <br>
      <input type="checkbox" id="check-${id}-1" class="answercheck">
      <input class="answer" id="answer-${id}-1" value="${id}-1">
      <button class="delanswer" id="delanswer-${id}-1"><img src="/static/test_creation/trashbin.png"></button>
      <br>
      <input type="checkbox" id="check-${id}-2" class="answercheck">
      <input class="answer" id="answer-${id}-2" value="${id}-2">
      <button class="delanswer" id="delanswer-${id}-2"><img src="/static/test_creation/trashbin.png"></button>
      <br>
      <button class="addanswer" id="addanswer-${id}">Добавить ответ</button>
    </div>
`);

  document.querySelector('#addanswer-' + id).addEventListener('click', () => addAnswer(id));
  document.querySelector('#delquestion-' + id).addEventListener('click', () => deleteQuestion(id));
  document.querySelector('#delanswer-' + id + '-1').addEventListener('click', () => deleteAnswer(id, 1));
  document.querySelector('#delanswer-' + id + '-2').addEventListener('click', () => deleteAnswer(id, 2));
  document.querySelector('#addimage-' + id).addEventListener('change', (event) => addImage(event, id));
}


function addAnswer(id) {
  let list_of_answers = obj[id];
  let last_answer;
  if (list_of_answers.length == 0) {
    last_answer = 0;
  } else {
    last_answer = list_of_answers[list_of_answers.length - 1];
  }
  let addbutton = document.querySelector('#addanswer-' + id);

  
  addbutton.insertAdjacentHTML("beforebegin", `
    <input type="checkbox" id="check-${id}-${last_answer + 1}" class="answercheck">
    <input class="answer" id="answer-${id}-${last_answer + 1}" value="${id}-${last_answer + 1}">
    <button class="delanswer" id="delanswer-${id}-${last_answer + 1}"><img src="/static/test_creation/trashbin.png"></button>
    <br>`);
  obj[id].push(last_answer + 1);
  document.querySelector('#delanswer-' + id + '-' + (last_answer + 1)).addEventListener('click', () => deleteAnswer(id , last_answer + 1));

}


function deleteQuestion(id) {
  let curdiv = document.querySelector('#question-' + id).closest('div');


  curdiv.remove();
  delete obj[id];
  delete images[id];

  let questions = Object.keys(obj);
  for (let span of questions) {
    let span_num = questions.indexOf(span);
    document.querySelector('#number-' + span).textContent = (span_num + 1) + '.';
  }

}

function deleteAnswer(id_question, id_answer) {
  let start_elem = document.querySelector('#check-' + id_question + '-' + id_answer);
  let next = start_elem.nextElementSibling;
  let nextnext = next.nextElementSibling;
  let nextnextnext = nextnext.nextElementSibling;
  start_elem.remove();
  next.remove();
  nextnext.remove();
  nextnextnext.remove();
  obj[id_question].splice(obj[id_question].indexOf(id_answer), 1);
}

function addImage(event, id) {
  let image = event.target.files[0];
  if (image !== undefined) {
    let place_for_image = document.querySelector('#delquestion-' + id);
    let url = URL.createObjectURL(image);
    place_for_image.insertAdjacentHTML('afterend',
      `<br><img src="${url}" id="image-${id}" class="image">`
    );
    let curlabel = document.querySelector('#label-' + id);
    let curfileinput = document.querySelector('#addimage-' + id);
    curlabel.remove();
    curfileinput.remove();
    let delbutton_place = document.querySelector('#question-' + id);
    delbutton_place.insertAdjacentHTML('afterend', 
      `<button class="delimage" id="delimage-${id}">Удалить фото</button>`
    );
    delbutton_place.nextElementSibling.addEventListener('click', () => deleteImage(id));
    images[id] = url;
  }
}


function deleteImage(id){
  let image = document.querySelector('#image-' + id);
  image.previousElementSibling.remove();
  image.remove();
  let input_place = document.querySelector('#question-' + id);
  input_place.insertAdjacentHTML('afterend', 
    `<label for="addimage-${id}" id="label-${id}">Выберите файл</label>
    <input type="file" id="addimage-${id}" class="addimage" accept="image/*">`);
  document.querySelector('#addimage-' + id).addEventListener('change', (event) => addImage(event, id));
  let delimagebutton = document.querySelector('#delimage-' + id);
  delimagebutton.remove();
  delete images[id];
}


async function submitTest() {
  // Id вопросов, ответов, картинок, полей для ввода и т.д не обязательно будут идти подряд по порядку
  // На этапе создания теста - это не особо важно, так как все элементы, которые должны иметь единый Id, его имеют
  // Нормализация нумерации (для отправки json на сервер) происходит только на этапе отправки теста
  let result = {};
 
  let list_of_questions = Object.keys(obj);
  if (list_of_questions.length == 0) {
    alert("Вы не можете сдать пустой тест!");
    return;
  }

  let name = document.querySelector(".test_name_input").value;
  let description = document.querySelector(".test_description_input").value;
  if (!name || !description) {
    alert("Должно присутствовать название и описание теста");
    return;
  }

  result['name'] = name;
  result['description'] = description;

  for (let question of list_of_questions) {
    let id = list_of_questions.indexOf(question) + 1;
    let question_text = document.querySelector('#question-' + question).value;
    let max_score = document.querySelector('#max_score-' + question).value;

    if (!/^[1-9]\d*$/.test(max_score)) {
      alert("Выставьте все максимальные баллы!");
      return;
    }
    result['question' + "-" + id] = 
      {'question': question_text,
       'image': null,
       'answers': {},
       'max_score': max_score
      };
    if (obj[question].length == 0) {
      alert("Вопросы не могут не содержать ответов");
      return;
    }
    for (let answer of obj[question]) {
      let answer_id = obj[question].indexOf(answer) + 1; 
      result['question' + "-" + id]['answers']['answer' + '-' + answer_id] = {
        'answer': document.querySelector('#answer-' + question + '-' + answer).value,
        'is_correct': document.querySelector('#check-' + question + '-' + answer).checked,
      };
    }
  }

  for (let image of Object.keys(images)) {
    let image_file = await blobUrlToDataUrl(images[image])
    result['question-' + (list_of_questions.indexOf(image) + 1)]['image'] = image_file;
  }

  result = JSON.stringify(result);

  let resp = await fetch(
    'http://127.0.0.1:5000/teacher/create_test',
        {
            method: 'POST',
            body: result,
            headers: {
                'Content-Type': 'application/json'
        }
        }
  );

  resp = await resp.json();
  
  if (resp['type'] == 'success') {
    window.location.href = resp['url'];
    return;
  }
}

async function blobUrlToDataUrl(blobUrl) {
  const blob = await (await fetch(blobUrl)).blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

let obj = {1 : [1, 2]};
let images = {};

function inicialiseFirstQuestion() {
  document.querySelector('#addanswer-1').addEventListener('click', () => addAnswer(1));;
  document.querySelector('#delquestion-1').addEventListener('click', () => deleteQuestion(1));
  document.querySelector('#delanswer-1-1').addEventListener('click', () => deleteAnswer(1, 1));
  document.querySelector('#delanswer-1-2').addEventListener('click', () => deleteAnswer(1, 2));
  document.querySelector('#addimage-1').addEventListener('change', (event) => addImage(event, 1));
}


inicialiseFirstQuestion();

document.querySelector('.addquestion').addEventListener('click', addQuestion);
document.querySelector('.submittest').addEventListener('click', submitTest);
