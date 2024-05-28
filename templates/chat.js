const qList = get("#q-list");
const total_qnum = 120;

let answered_map = new Map();
const subjects = ['Mathematics', 'Quantitative Aptitude', 'Computer Awareness and English']
const num_ques_sub = [1, 51, 91, 121]

const qid_elem = get("#form_qnum");
const sid_elem = get("#form_sub_id");
const subname_elem = get("#subject_name");
const timer_span = get("#timer");

let curr_qid = parseInt(qid_elem.value);
let curr_sid = parseInt(sid_elem.value);
subname_elem.innerHTML = subjects[curr_sid];

function onLoad() {
	curr_qid = parseInt(qid_elem.value);
	curr_sid = parseInt(sid_elem.value);
	console.log(curr_qid);
	console.log(curr_sid);
  let qlisthtml = "<table style='border: 1px solid black;'><tr>"
  for (let i = 0; i < total_qnum; i++) {
		l = i+1;
		if (i>0 && i%8 == 0) {
			qlisthtml += "</tr><tr>"
		}
		qlisthtml += 
			"<th>\
			<div onclick=showQuestion("+l+") class='qcell link' id='qlnum"+l+"'>\
			" + l + "\
			</div>\
			</th>"
	}
	qlisthtml += "</tr></table>"
  qList.innerHTML = qlisthtml;
	timer_show();
	load_ans();
	showQuestion(curr_qid);
	loop();
}

async function timer_show() {
	await new Promise(r => setTimeout(r, 500));
	const timer_init = timer_span.innerHTML;
	console.log(timer_init);
	let timer = new Timer(timer_init);
	while (!timer.isZero()) {
		await timer.dec();
		timer_span.innerHTML = timer.getString();
	}
	if (timer.isZero() && curr_sid == 2) {
		window.location.href="/result"
	} else if(timer.isZero()) {
		window.location.href = "/next_subject";
	}
}

class Timer {
	constructor(timer_str) {
		this.min = parseInt(timer_str.split(":")[0])
		this.sec = parseInt(timer_str.split(":")[1])
	}
	async dec() {
		if (this.sec == 0) {
			this.min -= 1;
			this.sec = 60;
		} else {
			this.sec -= 1;
		}
		await new Promise(r => setTimeout(r, 1000));
	}
	isZero() {
		return (this.min == 0 && this.sec == 0);
	}
	getString() {
		return zeroPad(this.min.toString()) + ":" + zeroPad(this.sec.toString());
	}
}

async function loop() {
	while (true) {
		color_qlist();
		await new Promise(r => setTimeout(r, 500));
	}
}

async function color_qlist() {
  for (let i = 1; i <= total_qnum; i++) {
		const res = get_is_ans(i.toString());
		const qnum = i.toString()
		const qcell_i = get("#qlnum"+qnum);
		if (answered_map.has(qnum)) {
			if (res) {
				qcell_i.classList.add('answered');
				qcell_i.classList.remove('unanswered');
			} else {
				qcell_i.classList.add('unanswered');
				qcell_i.classList.remove('answered');
			}
		}
		if (curr_qid == i) {
			qcell_i.classList.add('selected');
		} else {
			qcell_i.classList.remove('selected');
		}
	}
}

function get_is_ans(qnum) {
	if (answered_map.has(qnum) && answered_map.get(qnum) !== "") {
		return true;
	} else {
		return false;
	}
}

async function load_ans() {
	const response = await fetch(`/getanswers`);
	const ansJson = await response.json();
	console.log(ansJson.answers)
	const jsonR = JSON.parse(ansJson.answers);
	for (let i = 1; i <= total_qnum; i++) {
		const qnum = i.toString()
		if (jsonR.hasOwnProperty(qnum)) {
			console.log(jsonR[qnum]);
			answered_map.set(qnum, jsonR[qnum]);
		}
	}
	showQuestion(curr_qid);
}

function showQuestion(qnum) {
	curr_sub_ques_num = num_ques_sub[curr_sid];
	next_sub_ques_num = num_ques_sub[curr_sid+1];
	if (qnum >= curr_sub_ques_num && qnum < next_sub_ques_num) {
		qnumStr = qnum.toString()
		const qbox = get("#question");
		qbox.innerHTML = "<img src='/question?num="+qnumStr+"' class='q-img' />";
		reset_options();
		const res = get_is_ans(qnumStr);
		if (res) {
			const op_ans = get("#option"+answered_map.get(qnumStr));
			op_ans.checked=true;
		}
		get("#form_qnum").value=qnumStr;
		if (qnum !== curr_qid) {
			reset_ans(curr_qid.toString());
		}
		curr_qid=qnum;
	}
}

function set_q_active(qnum) {
	
}
	
function unset_active_q(qnum) {
	
}


function set_ans(qnum, ans) {
	answered_map.set(qnum, ans);
	const response = fetch('/answer?qnum='+qnum+'&ans='+ans);
}

function reset_ans(qnum) {
	answered_map.set(qnum, "");
	reset_options();
	const response = fetch('/answer?qnum='+qnum+'&ans=');
}

function reset_options() {
	const options = document.getElementsByName("option");
	for(var i=0;i<options.length;i++) {
    options[i].checked = false;
	}
}

const qForm = get("#qForm");
qForm.addEventListener("submit", event => {
    event.preventDefault();
		const formdata = new FormData(event.target);
		const entries = Object.fromEntries(formdata.entries());
		console.log(entries.option);
		if (typeof entries.option === 'undefined')	{
			ans = ""
		} else {
			ans = entries.option
		}
		set_ans(entries.form_qnum, ans);
		const res = get_is_ans(entries.form_qnum);
		console.log(res);
		if (curr_qid < total_qnum) {
			curr_qid += 1;
			showQuestion(curr_qid);
		}
});

const clearbtn = get("#clear-button");
clearbtn.onclick = function() {
		const qnum = get("#form_qnum").value;
		console.log(qnum);
		reset_ans(qnum);
		const res = get_is_ans(qnum);
		console.log(res);
};

const prevQBtn = get("#prev-ques-button");
prevQBtn.onclick = function() {
		if (curr_qid > 1){
			curr_qid -= 1;
			showQuestion(curr_qid);
		}
};

const endBtn = get("#end-exam");
endBtn.onclick = function() {
		window.location.href="/result"
};

// const startTestBtn = get("#start_test");
// startTestBtn.onclick = function() {
// 	window.location.href = "/exam";
// }


function zeroPad(numberStr) {
  return numberStr.padStart(2, "0");
}


function get(selector, root = document) {
    return root.querySelector(selector);
}
onLoad()